"""Combined Portal — Gemini Enterprise StreamAssist for SharePoint + ServiceNow.

Both connectors are independent: each can be toggled on/off in the UI. When
both are enabled, a single StreamAssist call queries the union of data stores.

Flow (per connector):
  1. MSAL login → Entra ID token (frontend)
  2. Entra JWT → WIF/STS → GCP token (identifies user for Discovery Engine)
  3. OAuth popup → IdP login → auth code → /api/oauth/callback
  4. acquireAndStoreRefreshToken stores the connector refresh token under WIF identity
  5. StreamAssist federated search uses the stored token for per-user ACLs
"""

import os
import re
import json
import time
import base64
import secrets
import requests
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Shared config ──────────────────────────────────────────────────────────────

PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
ENGINE_ID = os.environ["ENGINE_ID"]  # single engine; both connectors must be attached to it
WIF_POOL_ID = os.environ["WIF_POOL_ID"]
WIF_PROVIDER_ID = os.environ["WIF_PROVIDER_ID"]
TENANT_ID = os.environ["TENANT_ID"]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")

BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
STREAMASSIST_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"


def _bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# ── Per-connector config ───────────────────────────────────────────────────────

CONNECTORS: dict[str, dict] = {}

if _bool("SHAREPOINT_ENABLED", True):
    sp_domain = os.environ.get("SHAREPOINT_DOMAIN", "contoso.sharepoint.com")
    CONNECTORS["sharepoint"] = {
        "enabled": True,
        "label": "SharePoint",
        "connector_id": os.environ["SHAREPOINT_CONNECTOR_ID"],
        "entity_types": ["file", "page", "comment", "event", "attachment"],
        "auth_provider": "microsoft",
        "client_id": os.environ["SHAREPOINT_CONNECTOR_CLIENT_ID"],
        "scopes": (
            f"openid offline_access "
            f"https://{sp_domain}/AllSites.Read "
            f"https://{sp_domain}/Sites.Search.All"
        ),
        "auth_url_base": f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize",
    }

if _bool("SERVICENOW_ENABLED", True):
    sn_instance = os.environ.get("SERVICENOW_INSTANCE_URI", "https://your-instance.service-now.com").rstrip("/")
    CONNECTORS["servicenow"] = {
        "enabled": True,
        "label": "ServiceNow",
        "connector_id": os.environ["SERVICENOW_CONNECTOR_ID"],
        "entity_types": ["incident", "knowledge", "catalog", "users", "attachment"],
        "auth_provider": "servicenow",
        "client_id": os.environ["SN_OAUTH_CLIENT_ID"],
        "scopes": os.environ.get("SN_OAUTH_SCOPES", "useraccount"),
        "auth_url_base": f"{sn_instance}/oauth_auth.do",
    }

if not CONNECTORS:
    raise RuntimeError("No connectors enabled. Set SHAREPOINT_ENABLED=true and/or SERVICENOW_ENABLED=true.")


def _connector(name: str) -> dict:
    cfg = CONNECTORS.get(name)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Connector '{name}' is not enabled.")
    return cfg


def _connector_url(name: str) -> str:
    return f"{BASE}/{_connector(name)['connector_id']}"


# ── Helpers (shared) ───────────────────────────────────────────────────────────

# Maps nonce → {jwt, connector} so the OAuth callback knows which connector to bind the refresh token to.
_pending_consents: dict[str, dict] = {}


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
            "input": {
                "audience": body["audience"],
                "grantType": body["grantType"],
                "subjectToken": entra_jwt[:40] + "...",
                "subjectTokenType": body["subjectTokenType"],
            },
            "output": {"access_token": token[:40] + "...", "token_type": "Bearer"} if token else {"error": resp.text[:200]},
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


def _adc_token() -> str:
    import google.auth
    import google.auth.transport.requests as gr
    cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    cred.refresh(gr.Request())
    return cred.token


def _decode_state(raw: str) -> dict:
    try:
        return json.loads(base64.b64decode(raw).decode())
    except Exception:
        try:
            return json.loads(raw) if raw else {}
        except Exception:
            return {}


def _callback_page(title: str, message: str, color: str, result: dict, origin: str) -> HTMLResponse:
    result_json = json.dumps(result)
    return HTMLResponse(f"""<!DOCTYPE html>
<html><body style="background:#0f1117;color:#e4e6eb;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center"><h2 style="color:{color}">{title}</h2><p>{message}</p>
<script>if(window.opener)window.opener.postMessage({result_json},'{origin}');setTimeout(()=>window.close(),2000)</script>
</div></body></html>""")


# ── Health & metadata ──────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/connectors")
async def list_connectors():
    """Tells the frontend which connectors are enabled in this deployment."""
    return {
        name: {"enabled": cfg["enabled"], "label": cfg["label"]}
        for name, cfg in CONNECTORS.items()
    }


# ── Web grounding toggle (assistant-level) ─────────────────────────────────────

ASSISTANT_URL = (
    f"{BASE}/default_collection/engines/{ENGINE_ID}/assistants/default_assistant"
)
GROUNDED_INSTRUCTION = (
    "STRICT GROUNDING RULES:\n\n"
    "1. Use ONLY information that appears VERBATIM in the retrieved snippets. Do not paraphrase "
    "loosely; do not extrapolate; do not embellish.\n\n"
    "2. NEVER fabricate identifiers. This includes CVE IDs (e.g. CVE-2024-001), incident numbers "
    "(INC0001234), knowledge base IDs (KB0001234), ticket numbers, employee IDs, contract numbers, "
    "or ANY structured identifier. If the source describes a vulnerability or item but does not "
    "give it an ID, describe it WITHOUT inventing one.\n\n"
    "3. NEVER add example IDs, sample data, or placeholder values to make a table or list look "
    "more complete.\n\n"
    "4. If your answer requires structured data (table, list of incidents, etc.) and the sources "
    "do not contain that structured data verbatim, present the information as prose instead, OR "
    "say so explicitly: \"The source documents describe these findings but do not assign IDs to them.\"\n\n"
    "5. If retrieval returns no relevant documents, respond exactly: \"No matching documents were "
    "found in the selected connectors. Try rephrasing or enabling another connector.\"\n\n"
    "6. Do not use prior knowledge, training data, or web sources. Every concrete fact must trace "
    "to a snippet.\n\n"
    "BAD example: \"| CVE-2024-001 | SQL Injection | Critical |\" (when no CVE ID is in the source)\n"
    "GOOD example: \"The assessment found a SQL injection vulnerability in the customer search API "
    "endpoint (rated Critical, status: Unpatched).\""
)
WEB_AUGMENTED_INSTRUCTION = (
    "Prefer information from the connected data stores (SharePoint and ServiceNow). If those "
    "stores have no relevant content, you may use Google Search results. Clearly label which "
    "facts come from web search vs. internal documents. NEVER invent CVE IDs, ticket numbers, "
    "or any other identifiers — every concrete identifier must come from a real source."
)


def _admin_token() -> str:
    """Use the active gcloud identity for assistant-config calls (needs discoveryengine.assistants.update)."""
    import subprocess
    out = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True, text=True, timeout=10,
    )
    if out.returncode != 0:
        raise RuntimeError(f"gcloud auth print-access-token failed: {out.stderr}")
    return out.stdout.strip()


@app.get("/api/grounding/web")
async def get_web_grounding():
    token = _admin_token()
    resp = requests.get(ASSISTANT_URL, headers=_gcp_headers(token), timeout=15)
    if not resp.ok:
        return {"enabled": False, "error": f"{resp.status_code}: {resp.text[:200]}"}
    data = resp.json()
    enabled = data.get("webGroundingType") == "WEB_GROUNDING_TYPE_GOOGLE_SEARCH"
    return {"enabled": enabled}


class GroundingRequest(BaseModel):
    enabled: bool


@app.post("/api/grounding/web")
async def set_web_grounding(body: GroundingRequest):
    token = _admin_token()
    payload = {
        "webGroundingType": "WEB_GROUNDING_TYPE_GOOGLE_SEARCH" if body.enabled else "WEB_GROUNDING_TYPE_DISABLED",
        "generationConfig": {
            "systemInstruction": {
                "additionalSystemInstruction": WEB_AUGMENTED_INSTRUCTION if body.enabled else GROUNDED_INSTRUCTION,
            }
        },
    }
    resp = requests.patch(
        f"{ASSISTANT_URL}?updateMask=webGroundingType,generationConfig.systemInstruction",
        headers=_gcp_headers(token),
        json=payload,
        timeout=15,
    )
    if not resp.ok:
        return {"enabled": None, "error": f"{resp.status_code}: {resp.text[:200]}"}
    return {"enabled": body.enabled}


# ── Auth URL (per connector) ───────────────────────────────────────────────────

def _build_auth_url(connector_name: str, entra_jwt: str, origin: str, login_hint: str = "") -> str:
    cfg = _connector(connector_name)
    nonce = secrets.token_urlsafe(16)
    _pending_consents[nonce] = {"jwt": entra_jwt, "connector": connector_name}

    state_obj = {
        "origin": origin,
        "useBroadcastChannel": "false",
        "nonce": nonce,
        "connector": connector_name,
    }
    params = {
        "client_id": cfg["client_id"],
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": cfg["scopes"],
        "response_mode": "query",
        "state": base64.b64encode(json.dumps(state_obj).encode()).decode(),
        "prompt": "login",
    }
    if login_hint:
        params["login_hint"] = login_hint
    return f"{cfg['auth_url_base']}?{urlencode(params)}"


@app.get("/api/sharepoint/auth-url")
async def sharepoint_auth_url(request: Request):
    return await _auth_url_handler(request, "sharepoint")


@app.get("/api/servicenow/auth-url")
async def servicenow_auth_url(request: Request):
    return await _auth_url_handler(request, "servicenow")


async def _auth_url_handler(request: Request, connector_name: str):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"error": "Missing X-Entra-Id-Token header"}
    if connector_name not in CONNECTORS:
        return {"error": f"Connector '{connector_name}' is not enabled."}

    origin = request.headers.get("origin") or "http://localhost:5174"
    login_hint = request.query_params.get("login_hint", "")
    return {"auth_url": _build_auth_url(connector_name, entra_jwt, origin, login_hint)}


# ── OAuth callback (shared) ────────────────────────────────────────────────────

@app.get("/api/oauth/callback")
async def oauth_callback(request: Request):
    state = _decode_state(request.query_params.get("state", ""))
    origin = state.get("origin", "*")
    nonce = state.get("nonce", "")
    connector_name = state.get("connector", "sharepoint")
    msg = {"type": f"{connector_name}-oauth-callback", "connector": connector_name}

    error = request.query_params.get("error")
    if error:
        desc = request.query_params.get("error_description", "Unknown")
        return _callback_page("Authorization Failed", desc[:200], "#fbbf24",
                              {**msg, "success": False, "error": desc[:200]}, origin)

    if not request.query_params.get("code"):
        return _callback_page("No Code", "No authorization code received.", "#fbbf24",
                              {**msg, "success": False, "error": "No code"}, origin)

    pending = _pending_consents.pop(nonce, None)
    entra_jwt = pending.get("jwt") if pending else None
    gcp_token = _exchange_token(entra_jwt) if entra_jwt else None
    if not gcp_token:
        gcp_token = _adc_token()

    resp = requests.post(
        f"{_connector_url(connector_name)}/dataConnector:acquireAndStoreRefreshToken",
        headers=_gcp_headers(gcp_token),
        json={"fullRedirectUri": str(request.url)},
        timeout=30,
    )

    label = _connector(connector_name)["label"]
    if resp.ok:
        return _callback_page(f"{label} Connected!", "You can close this window.", "#34d399",
                              {**msg, "success": True}, origin)
    return _callback_page("Connection Failed", f"{resp.status_code}: {resp.text[:100]}", "#fbbf24",
                          {**msg, "success": False, "error": resp.text[:200]}, origin)


# ── OAuth exchange (shared) ────────────────────────────────────────────────────

class ExchangeRequest(BaseModel):
    fullRedirectUrl: str
    connector: Optional[str] = None  # optional override; otherwise inferred from state


@app.post("/api/oauth/exchange")
async def oauth_exchange(request: Request, body: ExchangeRequest):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"success": False, "error": "Missing X-Entra-Id-Token header"}

    # Infer connector from the state parameter inside fullRedirectUrl if not explicitly provided.
    connector_name = body.connector
    if not connector_name:
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(body.fullRedirectUrl).query)
        raw_state = (qs.get("state") or [""])[0]
        connector_name = _decode_state(raw_state).get("connector", "sharepoint")

    if connector_name not in CONNECTORS:
        return {"success": False, "error": f"Connector '{connector_name}' is not enabled."}

    trace = []
    gcp_token = _exchange_token(entra_jwt, trace) or _adc_token()

    start = time.time()
    resp = requests.post(
        f"{_connector_url(connector_name)}/dataConnector:acquireAndStoreRefreshToken",
        headers=_gcp_headers(gcp_token),
        json={"fullRedirectUri": body.fullRedirectUrl},
        timeout=30,
    )
    trace.append({
        "stage": "acquireAndStoreRefreshToken",
        "endpoint": f"POST {_connector(connector_name)['connector_id']}/dataConnector:acquireAndStoreRefreshToken",
        "status": resp.status_code,
        "duration_ms": round((time.time() - start) * 1000),
        "input": {"fullRedirectUri": body.fullRedirectUrl[:80] + "...", "connector": connector_name},
        "output": {"success": resp.ok} if resp.ok else {"error": resp.text[:200]},
    })

    if resp.ok:
        return {"success": True, "connector": connector_name, "_trace": trace}
    return {"success": False, "connector": connector_name, "error": resp.text[:200], "_trace": trace}


# ── Check connection (per connector) ───────────────────────────────────────────

@app.get("/api/sharepoint/check-connection")
async def sharepoint_check(request: Request):
    return await _check_handler(request, "sharepoint")


@app.get("/api/servicenow/check-connection")
async def servicenow_check(request: Request):
    return await _check_handler(request, "servicenow")


async def _check_handler(request: Request, connector_name: str):
    if connector_name not in CONNECTORS:
        return {"connected": False, "error": f"Connector '{connector_name}' is not enabled."}

    trace = []
    gcp_token = _get_gcp_token(request, trace)
    if not gcp_token:
        return {"connected": False, "_trace": trace}

    start = time.time()
    resp = requests.post(
        f"{_connector_url(connector_name)}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    connected = resp.ok and bool(resp.json().get("accessToken"))
    trace.append({
        "stage": "acquireAccessToken",
        "endpoint": f"POST {_connector(connector_name)['connector_id']}/dataConnector:acquireAccessToken",
        "status": resp.status_code,
        "duration_ms": round((time.time() - start) * 1000),
        "input": {
            "connector": connector_name,
            "api": "dataConnector:acquireAccessToken",
            "body": "(empty — identity comes from GCP token in Authorization header)",
            "gcpToken": gcp_token[:40] + "...",
        },
        "output": {"connected": connected, "hasAccessToken": connected},
    })
    return {"connected": connected, "connector": connector_name, "_trace": trace}


# ── StreamAssist Search (multi-connector) ──────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    session_token: Optional[str] = None
    connectors: Optional[list[str]] = None  # subset of enabled connector names; default = all enabled


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    import asyncio

    trace = []
    gcp_token = _get_gcp_token(request, trace)
    if not gcp_token:
        return {"error": "Authentication required", "_trace": trace}

    selected = body.connectors or list(CONNECTORS.keys())
    invalid = [c for c in selected if c not in CONNECTORS]
    if invalid:
        return {"error": f"Connector(s) not enabled: {', '.join(invalid)}", "_trace": trace}
    if not selected:
        return {"error": "No connectors selected for search.", "_trace": trace}

    result = await asyncio.to_thread(
        _stream_assist, gcp_token, body.query, body.session_token, selected, trace
    )
    result["_trace"] = trace
    return result


def _stream_assist(
    gcp_token: str,
    query: str,
    session_token: Optional[str],
    selected_connectors: list[str],
    trace: list | None = None,
) -> dict:
    data_store_specs: list[dict] = []
    spec_labels: list[str] = []
    for name in selected_connectors:
        cfg = _connector(name)
        ds_base = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{cfg['connector_id']}"
        for et in cfg["entity_types"]:
            data_store_specs.append({"dataStore": f"{ds_base}_{et}"})
            spec_labels.append(f"{cfg['connector_id']}_{et}")

    payload = {
        "query": {"text": query},
        "toolsSpec": {"vertexAiSearchSpec": {"dataStoreSpecs": data_store_specs}},
    }
    if session_token:
        payload["session"] = session_token

    print(f"[search] connectors={selected_connectors} query={query!r}", flush=True)
    start = time.time()
    resp = requests.post(STREAMASSIST_URL, headers=_gcp_headers(gcp_token), json=payload, timeout=60)
    elapsed = round((time.time() - start) * 1000)

    if not resp.ok:
        if trace is not None:
            trace.append({
                "stage": "StreamAssist",
                "endpoint": "POST .../streamAssist",
                "status": resp.status_code,
                "duration_ms": elapsed,
                "input": {
                    "query": query,
                    "connectors": selected_connectors,
                    "dataStoreSpecs": spec_labels,
                    "session": session_token,
                },
                "output": {"error": resp.text[:300]},
            })
        return {"error": f"StreamAssist returned {resp.status_code}: {resp.text[:200]}"}

    chunks = json.loads(resp.text)
    if not isinstance(chunks, list):
        chunks = [chunks]

    answer_parts, session_name, sources = [], None, []
    for chunk in chunks:
        session_name = chunk.get("sessionInfo", {}).get("session") or session_name
        for reply in chunk.get("answer", {}).get("replies", []):
            gc = reply.get("groundedContent", {})
            content = gc.get("content", {})
            if isinstance(content, dict) and not content.get("thought") and content.get("text"):
                answer_parts.append(content["text"])
            for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                src = _ref_to_source(ref, selected_connectors)
                if src:
                    sources.append(src)

    # Dedupe by URL but keep all unique snippets that grounded the answer.
    by_url: dict[str, dict] = {}
    for s in sources:
        url = s["url"]
        snippet = s.pop("snippet", "")
        if url not in by_url:
            s["snippets"] = []
            by_url[url] = s
        if snippet and snippet not in by_url[url]["snippets"]:
            by_url[url]["snippets"].append(snippet)
    unique = list(by_url.values())

    answer_text = "".join(answer_parts)
    ungrounded = bool(answer_text) and not unique

    if trace is not None:
        trace.append({
            "stage": "StreamAssist",
            "endpoint": "POST .../streamAssist",
            "status": resp.status_code,
            "duration_ms": elapsed,
            "input": {
                "query": query,
                "connectors": selected_connectors,
                "dataStoreSpecs": spec_labels,
                "session": session_token,
            },
            "output": {
                "answer_length": len(answer_text),
                "sources_count": len(unique),
                "ungrounded": ungrounded,
                "session": session_name,
                "chunks": len(chunks),
            },
        })

    print(f"[search] -> answer_len={len(answer_text)} sources={len(unique)} ungrounded={ungrounded}", flush=True)

    return {
        "answer": answer_text,
        "sources": unique,
        "session_token": session_name,
        "ungrounded": ungrounded,
    }


def _infer_connector_for_source(src: dict, selected: list[str]) -> str:
    et = (src.get("entity_type") or "").lower()
    for name in selected:
        if et in CONNECTORS[name]["entity_types"]:
            return name
    return selected[0] if selected else ""


def _entity_type_from_doc_path(doc_path: str, selected: list[str]) -> str:
    """Extract entity type from a data store path like '.../{connector_id}_{entity}/...'."""
    if not doc_path:
        return ""
    for name in selected:
        cid = CONNECTORS[name]["connector_id"]
        for et in CONNECTORS[name]["entity_types"]:
            if f"/{cid}_{et}/" in doc_path:
                return et
    return ""


def _file_type_from_uri(uri: str) -> str:
    if not uri:
        return ""
    path = uri.split("?", 1)[0]
    ext = path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
    return ext if 1 <= len(ext) <= 5 else ""


_SNIPPET_HIGHLIGHT_RE = re.compile(r"<c\d+>(.*?)</c\d+>", re.DOTALL)


def _clean_snippet(raw: str) -> str:
    """SharePoint refs put highlighted snippets in `content` with <ddd/> ellipses
    and <c0>...</c0> highlight tags. Convert to a clean string with [[term]]
    markers around highlighted spans (so the frontend can style them)."""
    if not raw:
        return ""
    txt = raw.replace("<ddd/>", "…")
    txt = _SNIPPET_HIGHLIGHT_RE.sub(r"[[\1]]", txt)
    return " ".join(txt.split()).strip()


def _ref_to_source(ref: dict, selected: list[str]) -> Optional[dict]:
    """Normalize a streamAssist reference. Handles both shapes:
    - SharePoint: `documentMetadata` (uri/title/document) + `content` is a snippet
    - ServiceNow: `content` is a JSON string with url/title/etc."""
    doc_meta = ref.get("documentMetadata")
    if isinstance(doc_meta, dict) and doc_meta.get("uri"):
        doc_path = doc_meta.get("document", "")
        entity_type = _entity_type_from_doc_path(doc_path, selected)
        return {
            "title": (doc_meta.get("title") or "Untitled").strip(),
            "url": doc_meta["uri"],
            "description": "",
            "snippet": _clean_snippet(ref.get("content", "") if isinstance(ref.get("content"), str) else ""),
            "file_type": _file_type_from_uri(doc_meta["uri"]),
            "author": "",
            "entity_type": entity_type,
            "connector": _infer_connector_for_source({"entity_type": entity_type}, selected),
        }
    raw = ref.get("content")
    if isinstance(raw, str):
        try:
            s = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None
        if isinstance(s, dict) and s.get("url"):
            return {
                "title": s.get("title", "Untitled"),
                "url": s["url"],
                "description": s.get("description", ""),
                "snippet": s.get("snippet") or s.get("description", ""),
                "file_type": s.get("file_type", ""),
                "author": s.get("author", ""),
                "entity_type": s.get("entity_type", ""),
                "connector": _infer_connector_for_source(s, selected),
            }
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("BACKEND_PORT", "8003")))
