"""SharePoint Portal — Gemini Enterprise StreamAssist with per-user OAuth.

Flow:
  1. MSAL login → Entra ID token (frontend)
  2. Entra JWT → WIF/STS → GCP token (identifies user for Discovery Engine)
  3. OAuth popup → Microsoft login → auth code → /api/oauth/callback
  4. acquireAndStoreRefreshToken stores SharePoint refresh token under WIF identity
  5. StreamAssist federated search uses stored token for per-user SharePoint ACLs
"""

import os
import json
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
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8003/api/oauth/callback")
SP_SCOPES = "openid offline_access https://CONTOSO.sharepoint.com/AllSites.Read https://CONTOSO.sharepoint.com/Sites.Search.All"

BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
CONNECTOR_URL = f"{BASE}/{CONNECTOR_ID}"
STREAMASSIST_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

_pending_consents: dict[str, str] = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _exchange_token(entra_jwt: str) -> Optional[str]:
    resp = requests.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }, timeout=10)
    return resp.json().get("access_token") if resp.ok else None


def _gcp_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }


def _get_gcp_token(request: Request) -> Optional[str]:
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    return _exchange_token(entra_jwt) if entra_jwt else None


def _callback_page(title: str, message: str, color: str, result: dict, origin: str) -> HTMLResponse:
    result_json = json.dumps(result)
    return HTMLResponse(f"""<!DOCTYPE html>
<html><body style="background:#0f1117;color:#e4e6eb;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center"><h2 style="color:{color}">{title}</h2><p>{message}</p>
<script>if(window.opener)window.opener.postMessage({result_json},'{origin}');setTimeout(()=>window.close(),2000)</script>
</div></body></html>""")


# ── OAuth Flow ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/sharepoint/auth-url")
async def get_auth_url(request: Request):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"error": "Missing X-Entra-Id-Token header"}

    origin = request.headers.get("origin") or "http://localhost:5174"
    nonce = secrets.token_urlsafe(16)
    _pending_consents[nonce] = entra_jwt

    params = {
        "client_id": CONNECTOR_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SP_SCOPES,
        "response_mode": "query",
        "state": json.dumps({"origin": origin, "nonce": nonce}),
        "prompt": "login",
    }
    login_hint = request.query_params.get("login_hint", "")
    if login_hint:
        params["login_hint"] = login_hint

    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"
    return {"auth_url": url}


@app.get("/api/oauth/callback")
async def oauth_callback(request: Request):
    state = json.loads(request.query_params.get("state", "{}"))
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

    # WIF token from stored Entra JWT (falls back to ADC)
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


@app.get("/api/sharepoint/check-connection")
async def check_connection(request: Request):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"connected": False}

    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    return {"connected": resp.ok and bool(resp.json().get("accessToken"))}


# ── StreamAssist Search ────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    session_token: Optional[str] = None


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    import asyncio

    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"error": "Authentication required"}

    return await asyncio.to_thread(_stream_assist, gcp_token, body.query, body.session_token)


def _stream_assist(gcp_token: str, query: str, session_token: Optional[str] = None) -> dict:
    ds_base = f"{BASE}/default_collection/dataStores/{CONNECTOR_ID}"
    payload = {
        "query": {"text": query},
        "dataStoreSpecs": [{"dataStore": f"{ds_base}_{et}"} for et in ENTITY_TYPES],
    }
    if session_token:
        payload["session"] = session_token

    resp = requests.post(STREAMASSIST_URL, headers=_gcp_headers(gcp_token), json=payload, timeout=60)
    if not resp.ok:
        return {"error": f"StreamAssist returned {resp.status_code}"}

    chunks = json.loads(resp.text)
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
                        "description": s.get("description", ""), "file_type": s.get("file_type", ""),
                        "author": s.get("author", ""), "entity_type": s.get("entity_type", ""),
                    })

    seen = set()
    unique = [s for s in sources if s["url"] not in seen and not seen.add(s["url"])]
    return {"answer": "".join(answer_parts), "sources": unique, "session_token": session_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
