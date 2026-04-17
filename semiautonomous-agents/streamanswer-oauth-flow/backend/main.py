"""StreamAnswer vs StreamAssist — Troubleshooting Lab.

Same WIF auth pipeline as streamassist-oauth-flow, but exposes BOTH
streamAnswer and streamAssist endpoints side by side for comparison.

Toggles:
  - API mode: streamAnswer vs streamAssist
  - dataStoreSpecs: include or omit
  - answerGenerationSpec flags (streamAnswer only)
"""

import os
import json
import time
import base64
import secrets
import requests
from urllib.parse import urlencode
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Config ─────────────────────────────────────────────────────────────────────

PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
ENGINE_ID = os.environ["ENGINE_ID"]
CONNECTOR_ID = os.environ["CONNECTOR_ID"]
WIF_POOL_ID = os.environ["WIF_POOL_ID"]
WIF_PROVIDER_ID = os.environ["WIF_PROVIDER_ID"]
CONNECTOR_CLIENT_ID = os.environ["CONNECTOR_CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")
SP_DOMAIN = os.environ.get("SHAREPOINT_DOMAIN", "contoso.sharepoint.com")
SP_SCOPES = f"openid offline_access https://{SP_DOMAIN}/AllSites.Read https://{SP_DOMAIN}/Sites.Search.All"

BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
CONNECTOR_URL = f"{BASE}/{CONNECTOR_ID}"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

STREAM_ASSIST_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
STREAM_ANSWER_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:streamAnswer"

_pending_consents: dict[str, str] = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _exchange_token(entra_jwt: str, trace: list | None = None) -> Optional[str]:
    start = time.time()
    body = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    resp = requests.post("https://sts.googleapis.com/v1/token", json=body, timeout=10)
    token = resp.json().get("access_token") if resp.ok else None
    if trace is not None:
        trace.append({
            "stage": "STS Token Exchange",
            "endpoint": "POST sts.googleapis.com/v1/token",
            "status": resp.status_code,
            "duration_ms": round((time.time() - start) * 1000),
            "input": {"audience": body["audience"], "subjectToken": entra_jwt[:40] + "..."},
            "output": {"access_token": token[:40] + "..."} if token else {"error": resp.text[:200]},
        })
    return token


def _gcp_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }


def _get_gcp_token(request: Request, trace: list | None = None) -> Optional[str]:
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    return _exchange_token(entra_jwt, trace) if entra_jwt else None


def _callback_page(title: str, message: str, color: str, result: dict, origin: str) -> HTMLResponse:
    return HTMLResponse(f"""<!DOCTYPE html>
<html><body style="background:#0f1117;color:#e4e6eb;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center"><h2 style="color:{color}">{title}</h2><p>{message}</p>
<script>if(window.opener)window.opener.postMessage({json.dumps(result)},'{origin}');setTimeout(()=>window.close(),2000)</script>
</div></body></html>""")


# ── OAuth Flow (identical to streamassist-oauth-flow) ─────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/sharepoint/auth-url")
async def get_auth_url(request: Request):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"error": "Missing X-Entra-Id-Token header"}
    origin = request.headers.get("origin") or "http://localhost:5176"
    nonce = secrets.token_urlsafe(16)
    _pending_consents[nonce] = entra_jwt
    params = {
        "client_id": CONNECTOR_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SP_SCOPES,
        "response_mode": "query",
        "state": base64.b64encode(json.dumps({"origin": origin, "useBroadcastChannel": "false", "nonce": nonce}).encode()).decode(),
        "prompt": "login",
    }
    login_hint = request.query_params.get("login_hint", "")
    if login_hint:
        params["login_hint"] = login_hint
    return {"auth_url": f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"}


@app.get("/api/oauth/callback")
async def oauth_callback(request: Request):
    raw_state = request.query_params.get("state", "")
    try:
        state = json.loads(base64.b64decode(raw_state).decode())
    except Exception:
        state = json.loads(raw_state) if raw_state else {}
    origin = state.get("origin", "*")
    nonce = state.get("nonce", "")
    msg = {"type": "sharepoint-oauth-callback"}

    error = request.query_params.get("error")
    if error:
        desc = request.query_params.get("error_description", "Unknown")
        return _callback_page("Authorization Failed", desc[:200], "#fbbf24",
                              {**msg, "success": False, "error": desc[:200]}, origin)

    if not request.query_params.get("code"):
        return _callback_page("No Code", "No authorization code received.", "#fbbf24",
                              {**msg, "success": False, "error": "No code"}, origin)

    entra_jwt = _pending_consents.pop(nonce, None)
    gcp_token = _exchange_token(entra_jwt) if entra_jwt else None
    if not gcp_token:
        import google.auth
        import google.auth.transport.requests as gr
        cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        cred.refresh(gr.Request())
        gcp_token = cred.token

    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken",
        headers=_gcp_headers(gcp_token),
        json={"fullRedirectUri": str(request.url)},
        timeout=30,
    )
    if resp.ok:
        return _callback_page("SharePoint Connected!", "You can close this window.", "#34d399",
                              {**msg, "success": True}, origin)
    return _callback_page("Connection Failed", f"{resp.status_code}: {resp.text[:100]}", "#fbbf24",
                          {**msg, "success": False, "error": resp.text[:200]}, origin)


class ExchangeRequest(BaseModel):
    fullRedirectUrl: str


@app.post("/api/oauth/exchange")
async def oauth_exchange(request: Request, body: ExchangeRequest):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"success": False, "error": "Missing X-Entra-Id-Token header"}
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
        import google.auth
        import google.auth.transport.requests as gr
        cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        cred.refresh(gr.Request())
        gcp_token = cred.token
    start = time.time()
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken",
        headers=_gcp_headers(gcp_token),
        json={"fullRedirectUri": body.fullRedirectUrl},
        timeout=30,
    )
    trace.append({
        "stage": "acquireAndStoreRefreshToken",
        "status": resp.status_code,
        "duration_ms": round((time.time() - start) * 1000),
        "output": {"success": resp.ok} if resp.ok else {"error": resp.text[:200]},
    })
    if resp.ok:
        return {"success": True, "_trace": trace}
    return {"success": False, "error": resp.text[:200], "_trace": trace}


@app.get("/api/sharepoint/check-connection")
async def check_connection(request: Request):
    trace = []
    gcp_token = _get_gcp_token(request, trace)
    if not gcp_token:
        return {"connected": False, "_trace": trace}
    start = time.time()
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    connected = resp.ok and bool(resp.json().get("accessToken"))
    trace.append({
        "stage": "acquireAccessToken",
        "status": resp.status_code,
        "duration_ms": round((time.time() - start) * 1000),
        "output": {"connected": connected},
    })
    return {"connected": connected, "_trace": trace}


# ── Search — Both APIs ────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    mode: str = "stream_assist"
    include_data_store_specs: bool = True
    ignore_non_answer_seeking: bool = True
    ignore_adversarial: bool = True
    ignore_low_relevant: bool = True
    session_token: Optional[str] = None


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    import asyncio

    trace = []
    gcp_token = _get_gcp_token(request, trace)
    if not gcp_token:
        return {"error": "Authentication required", "_trace": trace}

    if body.mode == "stream_answer":
        result = await asyncio.to_thread(_stream_answer, gcp_token, body, trace)
    else:
        result = await asyncio.to_thread(_stream_assist, gcp_token, body, trace)
    result["_trace"] = trace
    return result


def _build_data_store_specs() -> list[dict]:
    ds_base = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}"
    return [{"dataStore": f"{ds_base}_{et}"} for et in ENTITY_TYPES]


def _stream_assist(gcp_token: str, body: SearchRequest, trace: list) -> dict:
    payload: dict = {"query": {"text": body.query}}
    if body.include_data_store_specs:
        payload["dataStoreSpecs"] = _build_data_store_specs()
    if body.session_token:
        payload["session"] = body.session_token

    start = time.time()
    resp = requests.post(STREAM_ASSIST_URL, headers=_gcp_headers(gcp_token), json=payload, timeout=60)
    elapsed = round((time.time() - start) * 1000)

    trace_entry: dict = {
        "stage": "streamAssist",
        "endpoint": "POST .../assistants/default_assistant:streamAssist",
        "status": resp.status_code,
        "duration_ms": elapsed,
        "request_payload": payload,
    }

    if not resp.ok:
        trace_entry["response_raw"] = resp.text[:2000]
        trace.append(trace_entry)
        return {"error": f"streamAssist returned {resp.status_code}", "raw_response": resp.text[:2000], "request_payload": payload}

    raw = resp.text
    chunks = json.loads(raw)
    if not isinstance(chunks, list):
        chunks = [chunks]

    answer_parts, session_name, sources = [], None, []
    for chunk in chunks:
        session_name = chunk.get("sessionInfo", {}).get("session") or session_name
        for reply in chunk.get("answer", {}).get("replies", []):
            gc = reply.get("groundedContent", {})
            content = gc.get("content", {})
            if not content.get("thought") and content.get("text"):
                answer_parts.append(content["text"])
            for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                try:
                    s = json.loads(ref.get("content", "{}"))
                except (json.JSONDecodeError, TypeError):
                    continue
                if s.get("url"):
                    sources.append({
                        "title": s.get("title", "Untitled"), "url": s["url"],
                        "file_type": s.get("file_type", ""), "entity_type": s.get("entity_type", ""),
                    })

    seen: set[str] = set()
    unique = [s for s in sources if s["url"] not in seen and not seen.add(s["url"])]

    trace_entry["response_summary"] = {
        "answer_length": len("".join(answer_parts)),
        "sources": len(unique),
        "session": session_name,
        "chunks": len(chunks),
    }
    trace_entry["response_raw"] = raw[:4000]
    trace.append(trace_entry)

    return {
        "answer": "".join(answer_parts),
        "sources": unique,
        "session_token": session_name,
        "skipped_reasons": [],
        "raw_response": raw[:4000],
        "request_payload": payload,
    }


def _stream_answer(gcp_token: str, body: SearchRequest, trace: list) -> dict:
    payload: dict = {"query": {"text": body.query}}

    if body.include_data_store_specs:
        payload["searchSpec"] = {"searchParams": {"dataStoreSpecs": _build_data_store_specs()}}

    payload["answerGenerationSpec"] = {
        "ignoreAdversarialQuery": body.ignore_adversarial,
        "ignoreNonAnswerSeekingQuery": body.ignore_non_answer_seeking,
        "ignoreLowRelevantContent": body.ignore_low_relevant,
    }

    if body.session_token:
        payload["session"] = body.session_token
    else:
        payload["session"] = (
            f"projects/{PROJECT_NUMBER}/locations/global/collections/"
            f"default_collection/engines/{ENGINE_ID}/sessions/-"
        )

    start = time.time()
    resp = requests.post(STREAM_ANSWER_URL, headers=_gcp_headers(gcp_token), json=payload, timeout=60)
    elapsed = round((time.time() - start) * 1000)

    trace_entry: dict = {
        "stage": "streamAnswer",
        "endpoint": "POST .../servingConfigs/default_search:streamAnswer",
        "status": resp.status_code,
        "duration_ms": elapsed,
        "request_payload": payload,
    }

    if not resp.ok:
        trace_entry["response_raw"] = resp.text[:2000]
        trace.append(trace_entry)
        return {"error": f"streamAnswer returned {resp.status_code}", "raw_response": resp.text[:2000], "request_payload": payload}

    raw = resp.text
    chunks = json.loads(raw)
    if not isinstance(chunks, list):
        chunks = [chunks]

    answer_text = ""
    session_name = None
    sources: list[dict] = []
    skipped_reasons: list[str] = []

    for chunk in chunks:
        session_info = chunk.get("session", {})
        session_name = session_info.get("name") or session_name

        answer = chunk.get("answer", {})
        answer_text = answer.get("answerText", answer_text)

        for reason in answer.get("answerSkippedReasons", []):
            if reason not in skipped_reasons:
                skipped_reasons.append(reason)

        for step in answer.get("steps", []):
            for action in step.get("actions", []):
                for obs in action.get("observation", {}).get("searchResults", []):
                    struct = obs.get("structData", {})
                    url = struct.get("url", "") if isinstance(struct, dict) else ""
                    title = obs.get("title", struct.get("title", "")) if isinstance(struct, dict) else obs.get("title", "")
                    if url or title:
                        sources.append({
                            "title": title or "Untitled", "url": url,
                            "file_type": struct.get("file_type", "") if isinstance(struct, dict) else "",
                            "entity_type": struct.get("entity_type", "") if isinstance(struct, dict) else "",
                        })

    seen: set[str] = set()
    unique = [s for s in sources if s.get("url") and s["url"] not in seen and not seen.add(s["url"])]

    trace_entry["response_summary"] = {
        "answer_length": len(answer_text),
        "sources": len(unique),
        "session": session_name,
        "skipped_reasons": skipped_reasons,
        "chunks": len(chunks),
    }
    trace_entry["response_raw"] = raw[:4000]
    trace.append(trace_entry)

    return {
        "answer": answer_text or (
            "(No answer -- skipped: " + ", ".join(skipped_reasons) + ")"
            if skipped_reasons else "No answer generated."
        ),
        "sources": unique,
        "session_token": session_name,
        "skipped_reasons": skipped_reasons,
        "raw_response": raw[:4000],
        "request_payload": payload,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
