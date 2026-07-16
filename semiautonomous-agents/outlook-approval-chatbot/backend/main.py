"""Outlook Approval Chatbot Backend.

Exposes:
  - MSAL / WIF Authentication handshake
  - Chat query to StreamAssist (Gemini Enterprise)
  - Scan approvals from Outlook inbox using LLM prompting
  - Perform approval/rejection reply using direct MS Graph API delegated access token
"""

import os
import json
import time
import base64
import secrets
import requests
import asyncio
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Dotenv Overrides as per General Instructions
load_dotenv(override=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ─────────────────────────────────────────────────────────────────────

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
ENGINE_ID = os.environ.get("ENGINE_ID", "gemini-enterprise")
CONNECTOR_ID = os.environ.get("CONNECTOR_ID")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID")
CONNECTOR_CLIENT_ID = os.environ.get("CONNECTOR_CLIENT_ID")
TENANT_ID = os.environ.get("TENANT_ID")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")

OUTLOOK_SCOPES = "openid offline_access https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Calendars.Read"

BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
CONNECTOR_URL = f"{BASE}/{CONNECTOR_ID}"
STREAMASSIST_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

_pending_consents: dict[str, str] = {}


def _fetch_datastore_specs() -> list[dict]:
    """Fetch dataStoreSpecs from the connector's entity list at startup."""
    import subprocess
    if not PROJECT_NUMBER or not CONNECTOR_ID:
        return []
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Goog-User-Project": PROJECT_NUMBER}
        resp = requests.get(f"{CONNECTOR_URL}/dataConnector", headers=headers, timeout=10)
        if resp.ok:
            specs = []
            for entity in resp.json().get("entities", []):
                ds = entity.get("dataStore")
                if ds:
                    specs.append({"dataStore": ds})
            if specs:
                print(f"[init] Loaded {len(specs)} dataStoreSpecs from connector")
                return specs
    except Exception as e:
        print(f"[init] Could not fetch dataStoreSpecs: {e}")
    return []


# Delay dataStoreSpecs initialization so backend can start even if config is empty initially
DATASTORE_SPECS = []


@app.on_event("startup")
async def startup_event():
    global DATASTORE_SPECS
    DATASTORE_SPECS = _fetch_datastore_specs()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _exchange_token(entra_jwt: str) -> Optional[str]:
    body = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    resp = requests.post("https://sts.googleapis.com/v1/token", json=body, timeout=10)
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


# ── Auth endpoints ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/outlook/auth-url")
async def get_auth_url(request: Request):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"error": "Missing X-Entra-Id-Token header"}

    origin = request.headers.get("origin") or "http://localhost:5173"
    nonce = secrets.token_urlsafe(16)
    _pending_consents[nonce] = entra_jwt

    params = {
        "client_id": CONNECTOR_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": OUTLOOK_SCOPES,
        "response_mode": "query",
        "state": base64.b64encode(json.dumps({"origin": origin, "useBroadcastChannel": "false", "nonce": nonce}).encode()).decode(),
        "prompt": "consent",
    }
    login_hint = request.query_params.get("login_hint", "")
    if login_hint:
        params["login_hint"] = login_hint

    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"
    return {"auth_url": url}


@app.get("/api/oauth/callback")
async def oauth_callback(request: Request):
    raw_state = request.query_params.get("state", "")
    try:
        state = json.loads(base64.b64decode(raw_state).decode())
    except Exception:
        state = json.loads(raw_state) if raw_state else {}
    origin = state.get("origin", "*")
    nonce = state.get("nonce", "")
    msg = {"type": "outlook-oauth-callback"}

    error = request.query_params.get("error")
    if error:
        desc = request.query_params.get("error_description", "Unknown")
        return _callback_page("Authorization Failed", desc[:200], "#fbbf24",
                               {**msg, "success": False, "error": desc[:200]}, origin)

    if not request.query_params.get("code"):
        return _callback_page("No Code", "No authorization code received.", "#fbbf24",
                               {**msg, "success": False, "error": "No code"}, origin)

    # WIF token from stored Entra JWT
    entra_jwt = _pending_consents.pop(nonce, None)
    gcp_token = _exchange_token(entra_jwt) if entra_jwt else None
    if not gcp_token:
        # fallback to default GCP credential if none exists
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
        return _callback_page("Outlook Connected!", "You can close this window.", "#34d399",
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

    gcp_token = _exchange_token(entra_jwt)
    if not gcp_token:
        import google.auth
        import google.auth.transport.requests as gr
        cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        cred.refresh(gr.Request())
        gcp_token = cred.token

    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken",
        headers=_gcp_headers(gcp_token),
        json={"fullRedirectUri": body.fullRedirectUrl},
        timeout=30,
    )

    if resp.ok:
        return {"success": True}
    return {"success": False, "error": resp.text[:200]}


@app.get("/api/outlook/check-connection")
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
    connected = resp.ok and bool(resp.json().get("accessToken"))
    return {"connected": connected}


# ── Search & Assistant endpoints ───────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    session_token: Optional[str] = None


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"error": "Authentication required"}

    result = await asyncio.to_thread(_stream_assist, gcp_token, body.query, body.session_token)
    return result


def _stream_assist(gcp_token: str, query: str, session_token: Optional[str] = None) -> dict:
    payload = {"query": {"text": query}}
    if DATASTORE_SPECS:
        payload["toolsSpec"] = {"vertexAiSearchSpec": {"dataStoreSpecs": DATASTORE_SPECS}}
    if session_token:
        payload["session"] = session_token

    resp = requests.post(STREAMASSIST_URL, headers=_gcp_headers(gcp_token), json=payload, timeout=60)

    if not resp.ok:
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


# ── Approvals Endpoints ────────────────────────────────────────────────────────

@app.get("/api/approvals")
async def get_approvals(request: Request, lookback_hours: int = 48, timezone: str = "EST"):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"error": "Authentication required"}

    # Dynamic date formulation
    from datetime import datetime
    current_datetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # Prompt user supplied to scan inbox
    prompt = f"""You are the user's executive assistant. Scan the user's Outlook inbox and surface
emails that need the user to act, sorting each into exactly ONE category.
Today is {current_datetime} (timezone: {timezone}).
Return ONE JSON object — no prose, no code fences, no markdown — in exactly
this shape:
{{"items":[{{"id":"","label":"","context":{{"category":"","source":"","requester":"","from":"","subject":"","dueDate":"","summary":"","requested_action":"","link":""}}}}]}}
Rules:
- Look at emails received in the last {lookback_hours} hours. Judge by language/intent, be accurate, don't miss anything.
- Set context.category to exactly one of:
  • "approval" — a person is asking the user to approve, sign off, authorize, or
    give a go/no-go decision. Also set context.source="Email", context.requester
    (who is asking) and context.dueDate (the by-when) if stated.
  • "email_reply" — ANY other email needing the user's action: a reply, follow-up,
    introduction, or new outbound email the user must send.
- Use only facts stated in the email; leave any unknown field "". context.subject:
  the subject. context.from: sender name/address. context.summary: 1-2 sentences on
  what's needed and why, plus any prior email history on this matter from the last
  24 hours (earlier messages or reminders). context.requested_action: the exact
  action if stated. context.link: link if available. For threads, use the latest message only.
- EXCLUDE newsletters, FYIs, system/automated notifications, calendar invites, and
  anything already approved/completed/rejected.
- Order by priority (soonest due first).
- If nothing matches, return exactly: {{"items":[]}}
- Use the user's local timezone; 12-hour AM/PM; never label "(UTC)". Keep "label" under 80 chars."""

    result = await asyncio.to_thread(_stream_assist, gcp_token, prompt, None)
    answer = result.get("answer", "")

    if "error" in result:
        return {"error": result["error"]}

    # Clean code fences or extra text if any
    cleaned_answer = answer.strip()
    if cleaned_answer.startswith("```"):
        # Strip ```json or ```
        lines = cleaned_answer.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned_answer = "\n".join(lines).strip()

    try:
        parsed_data = json.loads(cleaned_answer)
        return parsed_data
    except Exception as e:
        return {
            "error": "Failed to parse JSON from StreamAssist response",
            "raw_response": answer,
            "details": str(e)
        }


class ApprovalActionBody(BaseModel):
    action: str  # "approve" or "reject"
    comment: Optional[str] = None


@app.post("/api/approvals/{message_id}/action")
async def perform_approval_action(request: Request, message_id: str, body: ApprovalActionBody):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    comment = body.comment
    if not comment:
        comment = "Approved." if body.action == "approve" else "Rejected."

    # 1. Fetch MS Graph access token from DE
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    if not resp.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to acquire Microsoft Graph token from GCP: {resp.text[:300]}"
        )

    graph_token = resp.json().get("accessToken")
    if not graph_token:
        raise HTTPException(status_code=502, detail="No Microsoft Graph token returned by GCP")

    # 2. Reply to the message in Outlook
    reply_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/reply"
    reply_headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }
    reply_body = {
        "comment": comment
    }

    reply_resp = requests.post(reply_url, headers=reply_headers, json=reply_body, timeout=15)
    if not reply_resp.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reply to message via Microsoft Graph API: {reply_resp.text[:300]}"
        )

    return {"success": True, "action": body.action, "comment": comment}


class SendEmailBody(BaseModel):
    to_address: str
    subject: str
    body: str


@app.post("/api/send-email")
async def send_custom_email(request: Request, body: SendEmailBody):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    # 1. Fetch MS Graph access token from DE
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    if not resp.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to acquire Microsoft Graph token from GCP: {resp.text[:300]}"
        )

    graph_token = resp.json().get("accessToken")
    if not graph_token:
        raise HTTPException(status_code=502, detail="No Microsoft Graph token returned by GCP")

    # 2. Send the email in Outlook
    send_url = "https://graph.microsoft.com/v1.0/me/sendMail"
    send_headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }
    send_body = {
        "message": {
            "subject": body.subject,
            "body": {
                "contentType": "HTML",
                "content": body.body.replace("\n", "<br>")
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": body.to_address
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    send_resp = requests.post(send_url, headers=send_headers, json=send_body, timeout=15)
    if not send_resp.ok:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send email via Microsoft Graph API: {send_resp.text[:300]}"
        )

    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    # Determine port to run. We must check and run, port 8005 is default for Outlook projects
    uvicorn.run(app, host="0.0.0.0", port=8005)
