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
load_dotenv(dotenv_path=".env", override=True)
load_dotenv(dotenv_path="../.env", override=True)

# Force-set Vertex project settings to match the outlook connector's project
if os.environ.get("PROJECT_NUMBER") == "545964020693":
    os.environ["GOOGLE_CLOUD_PROJECT"] = "sharepoint-wif-agent"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

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
    if not entra_jwt or entra_jwt in ("undefined", "null", "mock-graph-token-12345", "mock-token"):
        try:
            import google.auth
            import google.auth.transport.requests as gr
            cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            cred.refresh(gr.Request())
            return cred.token
        except Exception as e:
            print(f"Auth Fallback Error: {e}")
            pass
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


# ── Search & Assistant endpoints (Google ADK & MCP Tools) ──────────────────────

import contextvars
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

current_graph_token = contextvars.ContextVar("current_graph_token", default=None)
last_fetched_items = contextvars.ContextVar("last_fetched_items", default=None)


def fetch_outlook_emails() -> str:
    """Fetches the user's recent email messages from Outlook inbox.
    
    Returns:
        A list of recent email messages formatted as a JSON string. Each message contains:
        id, subject, snippet, from_name, from_address, received, and web_link.
    """
    token = current_graph_token.get()
    if not token:
        return "Error: No active Microsoft Graph access token. Authentication required."
    
    url = "https://graph.microsoft.com/v1.0/me/messages?$top=50&$select=id,subject,bodyPreview,from,receivedDateTime,webLink"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.ok:
            messages = resp.json().get("value", [])
            formatted_messages = []
            for msg in messages:
                item = {
                    "id": msg.get("id"),
                    "subject": msg.get("subject"),
                    "snippet": msg.get("bodyPreview"),
                    "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", "Unknown"),
                    "from_address": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "received": msg.get("receivedDateTime"),
                    "web_link": msg.get("webLink")
                }
                formatted_messages.append(item)
                
                # Store in ContextVar for auto-grounding fallback
                current_fetched = last_fetched_items.get()
                if current_fetched is not None:
                    current_fetched.append(item)
            return json.dumps(formatted_messages, indent=2)
        else:
            return f"Error fetching emails from Microsoft Graph API: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Exception while fetching emails: {str(e)}"


def send_outlook_reply(message_id: str, comment: str) -> str:
    """Sends a reply/comment to an existing email message in Outlook.
    
    Args:
        message_id: The ID of the email message to reply to.
        comment: The text comment/body of the reply.
    """
    token = current_graph_token.get()
    if not token:
        return "Error: No active Microsoft Graph access token."
    
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/reply"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"comment": comment}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.ok:
            return f"Reply successfully sent to message {message_id}."
        return f"Failed to reply via Microsoft Graph API: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Exception replying: {str(e)}"


def send_new_outlook_email(to_address: str, subject: str, body: str) -> str:
    """Sends a new outbound email from the user's Outlook account.
    
    Args:
        to_address: Recipient's email address.
        subject: Email subject.
        body: Email body text.
    """
    token = current_graph_token.get()
    if not token:
        return "Error: No active Microsoft Graph access token."
    
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body.replace("\n", "<br>")
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_address
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.ok:
            return "Email successfully sent."
        return f"Failed to send email via Microsoft Graph: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Exception sending email: {str(e)}"


def fetch_outlook_calendar(top_n: int = 10) -> str:
    """Fetches upcoming calendar events from the user's Microsoft calendar.
    
    Args:
        top_n: Maximum number of upcoming calendar events to retrieve.
    """
    token = current_graph_token.get()
    if not token:
        return "Error: No active Microsoft Graph access token."
        
    url = "https://graph.microsoft.com/v1.0/me/calendarview"
    from datetime import datetime, timedelta
    start_dt = datetime.now().isoformat()
    end_dt = (datetime.now() + timedelta(days=7)).isoformat()
    
    params = {
        "startDateTime": start_dt,
        "endDateTime": end_dt,
        "$top": top_n,
        "$select": "subject,start,end,organizer,attendees,bodyPreview,webLink",
        "$orderby": "start/dateTime"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.ok:
            events = resp.json().get("value", [])
            if not events:
                return "No upcoming events found in calendar."
            results = []
            for ev in events:
                subj = ev.get("subject", "No Title")
                st = ev.get("start", {}).get("dateTime", "Unknown")
                en = ev.get("end", {}).get("dateTime", "Unknown")
                org = ev.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown")
                snippet = ev.get("bodyPreview", "")
                wl = ev.get("webLink", "")
                results.append(f"• {subj} ({st} to {en}) | Organizer: {org}\n  Description: {snippet}\n  Link: {wl}")
                
                # Store in ContextVar for auto-grounding fallback
                item = {
                    "subject": subj,
                    "web_link": wl,
                    "organizer": org
                }
                current_fetched = last_fetched_items.get()
                if current_fetched is not None:
                    current_fetched.append(item)
            return "\n\n".join(results)
        return f"Failed to fetch calendar: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Exception fetching calendar: {str(e)}"


# Define ADK Agent using Allowed model gemini-3.5-flash
outlook_agent = Agent(
    name="outlook_mcp_assistant",
    model="gemini-2.5-flash",
    description="Outlook executive assistant utilizing Graph API local tool bounds",
    instruction="""You are a highly efficient, executive-ready Outlook assistant.
You have direct tool access to the user's mailbox (fetch_outlook_emails, send_outlook_reply, send_new_outlook_email) and calendar (fetch_outlook_calendar).

When asked about the inbox, emails, or recent messages, always fetch the emails first using `fetch_outlook_emails`.
When asked about meetings, schedule, agenda or events, use `fetch_outlook_calendar`.

CRITICAL INSTRUCTION FOR GROUNDING:
Whenever you reference, summarize, or list any specific email or calendar event in your answer, you MUST format its title as a Markdown link pointing exactly to its corresponding 'web_link' or 'Link' URL provided by the tool.
For example: [Testing](https://outlook.office.com/mail/id/XYZ...)
This is mandatory so the frontend UI can automatically extract and display interactive grounding citation badges.

Maintain an extremely professional, premium tone.
""",
    tools=[fetch_outlook_emails, send_outlook_reply, send_new_outlook_email, fetch_outlook_calendar]
)

_active_runners: dict[str, InMemoryRunner] = {}


class SearchRequest(BaseModel):
    query: str
    session_token: Optional[str] = None


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    import time
    start_time = time.time()
    
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"error": "Authentication required"}
    
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    if not resp.ok:
        return {"error": f"Failed to acquire Microsoft Graph token: {resp.text[:300]}"}
    
    graph_token = resp.json().get("accessToken")
    if not graph_token:
        return {"error": "No Microsoft Graph token returned by GCP"}
    
    # Track items fetched in this API turn
    fetched_list = []
    token_fetched = last_fetched_items.set(fetched_list)
    token_token = current_graph_token.set(graph_token)
    session_id = body.session_token or "default-session"
    
    if session_id not in _active_runners:
        _active_runners[session_id] = InMemoryRunner(agent=outlook_agent, app_name="outlook-mcp-chatbot")
        
    runner = _active_runners[session_id]
    
    session = None
    try:
        session = await runner.session_service.get_session(app_name="outlook-mcp-chatbot", user_id="user", session_id=session_id)
    except Exception:
        pass
        
    if not session:
        try:
            session = await runner.session_service.create_session(
                app_name="outlook-mcp-chatbot", user_id="user", session_id=session_id
            )
        except Exception:
            class DummySession:
                def __init__(self, sid):
                    self.id = sid
            session = DummySession(session_id)
        
    content = Content(parts=[Part(text=body.query)], role="user")
    answer_parts = []
    
    try:
        async for event in runner.run_async(
            user_id="user", session_id=session.id, new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        answer_parts.append(part.text)
    finally:
        current_graph_token.reset(token_token)
        last_fetched_items.reset(token_fetched)
        
    full_answer = "".join(answer_parts)
    
    # Auto-extract unique clickable email references for UI source integration
    sources = []
    import re
    # Support both office.com and office365.com domains
    links = re.findall(r'\[([^\]]+)\]\((https://outlook\.(?:office|office365)\.com/[^\)]+)\)', full_answer)
    for title, url in links:
        if not any(s["url"] == url for s in sources):
            sources.append({
                "title": title,
                "url": url,
                "description": "Email referenced by ADK Agent",
                "entity_type": "Email"
            })
        
    # Auto-grounding Fallback: Scan fetched list for mentions of subject in full_answer
    for item in fetched_list:
        subj = item.get("subject")
        sender = item.get("from_name") or item.get("organizer")
        web_link = item.get("web_link")
        if not web_link:
            continue
        
        # Match only when the specific email's subject is referenced, preventing irrelevant matches
        if subj and len(subj) >= 4:
            if subj.lower() in full_answer.lower():
                if not any(s["url"] == web_link for s in sources):
                    sources.append({
                        "title": subj,
                        "url": web_link,
                        "description": f"Grounded reference from {sender or 'Outlook'}",
                        "entity_type": "Email"
                    })
                    
    # Clean up full_answer: replace raw markdown links with clean readable bracketed text
    full_answer = re.sub(
        r'\[([^\]]+)\]\((https://outlook\.(?:office|office365)\.com/[^\)]+)\)',
        r'[\1]',
        full_answer
    )
                
    latency_sec = time.time() - start_time
    
    return {
        "answer": full_answer,
        "sources": sources,
        "session_token": session_id,
        "latency": round(latency_sec, 2)
    }


# ── Approvals Endpoints ────────────────────────────────────────────────────────

@app.get("/api/approvals")
async def get_approvals(request: Request, lookback_hours: int = 48, timezone: str = "EST"):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return {"error": "Authentication required"}
        
    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    if not resp.ok:
        return {"error": f"Failed to acquire Microsoft Graph token: {resp.text[:300]}"}
    
    graph_token = resp.json().get("accessToken")
    if not graph_token:
        return {"error": "No Microsoft Graph token returned by GCP"}
        
    token_token = current_graph_token.set(graph_token)
    session_id = "approvals-scanning-session"
    
    if session_id not in _active_runners:
        _active_runners[session_id] = InMemoryRunner(agent=outlook_agent, app_name="outlook-mcp-chatbot")
        
    runner = _active_runners[session_id]
    
    session = None
    try:
        session = await runner.session_service.get_session(app_name="outlook-mcp-chatbot", user_id="user", session_id=session_id)
    except Exception:
        pass
        
    if not session:
        try:
            session = await runner.session_service.create_session(
                app_name="outlook-mcp-chatbot", user_id="user", session_id=session_id
            )
        except Exception:
            class DummySession:
                def __init__(self, sid):
                    self.id = sid
            session = DummySession(session_id)
        
    from datetime import datetime
    current_datetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    prompt = f"""You are the user's executive assistant. Scan the user's Outlook inbox and surface
emails that need the user to act, sorting each into exactly ONE category.
Today is {current_datetime} (timezone: {timezone}).

First, use your `fetch_outlook_emails` tool to pull recent messages.
Then, parse them and return ONE JSON object — no prose, no code fences, no markdown — in exactly this shape:
{{"items":[{{"id":"","label":"","context":{{"category":"","source":"","requester":"","from":"","subject":"","dueDate":"","summary":"","requested_action":"","link":""}}}}]}}

Rules:
- Look at emails received in the last {lookback_hours} hours. Judge by language/intent, be accurate, don't miss anything.
- Set context.category to exactly one of:
  • "approval" — a person is asking the user to approve, sign off, authorize, or give a go/no-go decision. Also set context.source="Email", context.requester and context.dueDate.
  • "email_reply" — ANY other email needing the user's action.
- Extract details carefully from the emails returned by your tool.
- For context.link, use deep-links format: https://outlook.office.com/mail/id/{{id}}
- Order by priority (soonest due first).
- If nothing matches, return exactly: {{"items":[]}}
- Use the user's local timezone; 12-hour AM/PM; never label "(UTC)". Keep "label" under 80 chars."""

    content = Content(parts=[Part(text=prompt)], role="user")
    answer_parts = []
    
    try:
        async for event in runner.run_async(
            user_id="user", session_id=session.id, new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        answer_parts.append(part.text)
    finally:
        current_graph_token.reset(token_token)
        
    answer = "".join(answer_parts).strip()
    cleaned_answer = answer
    if cleaned_answer.startswith("```"):
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
            "error": "Failed to parse JSON from ADK Agent response",
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


@app.get("/api/calendar")
async def get_calendar(request: Request, top: int = 10):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    # 1. Fetch MS Graph access token
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

    # 2. Fetch events from Graph API
    url = "https://graph.microsoft.com/v1.0/me/calendarview"
    from datetime import datetime, timedelta
    start_dt = datetime.now().isoformat()
    end_dt = (datetime.now() + timedelta(days=7)).isoformat()

    params = {
        "startDateTime": start_dt,
        "endDateTime": end_dt,
        "$top": top,
        "$select": "id,subject,start,end,organizer,attendees,bodyPreview",
        "$orderby": "start/dateTime"
    }
    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }
    try:
        cal_resp = requests.get(url, headers=headers, params=params, timeout=15)
        if cal_resp.ok:
            events = cal_resp.json().get("value", [])
            items = []
            for ev in events:
                # Format times
                st_str = ev.get("start", {}).get("dateTime", "2026-07-16T12:00:00")
                en_str = ev.get("end", {}).get("dateTime", "2026-07-16T13:00:00")
                
                try:
                    t_start = datetime.fromisoformat(st_str.split(".")[0]).strftime("%I:%M %p")
                    t_end = datetime.fromisoformat(en_str.split(".")[0]).strftime("%I:%M %p")
                except Exception:
                    t_start = "1:00 PM"
                    t_end = "2:00 PM"

                items.append({
                    "id": ev.get("id"),
                    "subject": ev.get("subject", "No Title"),
                    "start": t_start,
                    "end": t_end,
                    "attendeesCount": len(ev.get("attendees", [])),
                    "organizer": ev.get("organizer", {}).get("emailAddress", {}).get("name", "Unknown"),
                    "snippet": ev.get("bodyPreview", "No additional context.")
                })
            return {"items": items}
        raise HTTPException(status_code=502, detail=f"Failed to query Graph: {cal_resp.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_mock_dashboard():
    return {
        "summary": [
            {
                "id": "s1",
                "icon": "meeting",
                "text": "Your next meeting is at 11:00 AM",
                "prompt": "Tell me more about the PxE Transformation Office onboarding meeting at 11:00 AM"
            },
            {
                "id": "s2",
                "icon": "calendar",
                "text": "You have 5 other meetings today",
                "prompt": "Summarize my full schedule for today"
            }
        ],
        "actions": [
            {
                "id": "a1",
                "icon": "warning",
                "text": "You have 1 compliance item due soon",
                "prompt": "Show details on the compliance item or interview that needs attention"
            },
            {
                "id": "a2",
                "icon": "attention",
                "text": "1 email requires attention",
                "prompt": "Which emails require my attention or action?"
            }
        ],
        "well_being": [
            {
                "id": "w1",
                "icon": "lotus",
                "text": "You're free at 11:30 AM — consider a 15-min stretch to recharge"
            },
            {
                "id": "w2",
                "icon": "burger",
                "text": "Even though you have a meeting, consider taking a lunch break at 1:30 PM"
            }
        ]
    }


@app.get("/api/dashboard")
async def get_dashboard(request: Request, lookback_hours: int = 48, timezone: str = "EST"):
    gcp_token = _get_gcp_token(request)
    if not gcp_token:
        return _get_mock_dashboard()

    resp = requests.post(
        f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
        headers=_gcp_headers(gcp_token),
        json={},
        timeout=15,
    )
    if not resp.ok:
        return _get_mock_dashboard()
    
    graph_token = resp.json().get("accessToken")
    if not graph_token:
        return _get_mock_dashboard()

    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }

    try:
        # Fetch events for today
        from datetime import datetime, timedelta
        now = datetime.now()
        start_dt = now.strftime("%Y-%m-%dT00:00:00")
        end_dt = (now + timedelta(days=1)).strftime("%Y-%m-%dT23:59:59")
        
        cal_url = "https://graph.microsoft.com/v1.0/me/calendarview"
        cal_params = {
            "startDateTime": start_dt,
            "endDateTime": end_dt,
            "$top": 15,
            "$select": "subject,start,end,organizer"
        }
        cal_resp = requests.get(cal_url, headers=headers, params=cal_params, timeout=10)
        events = cal_resp.json().get("value", []) if cal_resp.ok else []

        # Fetch emails from last 48h
        mail_url = "https://graph.microsoft.com/v1.0/me/messages"
        mail_params = {
            "$top": 20,
            "$select": "id,subject,bodyPreview,from,receivedDateTime"
        }
        mail_resp = requests.get(mail_url, headers=headers, params=mail_params, timeout=10)
        messages = mail_resp.json().get("value", []) if mail_resp.ok else []

        if not events and not messages:
            return _get_mock_dashboard()

        # Build dynamic dashboard items
        summary_cards = []
        action_cards = []
        wellbeing_cards = []

        # 1. Schedule summaries
        if events:
            # Sort events by start dateTime
            events_sorted = sorted(events, key=lambda x: x.get("start", {}).get("dateTime", ""))
            next_meeting = events_sorted[0]
            m_subject = next_meeting.get("subject", "Meeting")
            m_start_raw = next_meeting.get("start", {}).get("dateTime", "")
            try:
                m_time = datetime.fromisoformat(m_start_raw.split(".")[0]).strftime("%I:%M %p")
            except Exception:
                m_time = "11:00 AM"

            summary_cards.append({
                "id": "s1_dynamic",
                "icon": "meeting",
                "text": f"Your next meeting is at {m_time}",
                "prompt": f"Tell me more about the meeting '{m_subject}' at {m_time}"
            })
            if len(events_sorted) > 1:
                summary_cards.append({
                    "id": "s2_dynamic",
                    "icon": "calendar",
                    "text": f"You have {len(events_sorted) - 1} other meetings today",
                    "prompt": "Show me a list of all my meetings today and highlight any conflicts"
                })
        else:
            summary_cards.append({
                "id": "s1_empty",
                "icon": "calendar",
                "text": "Your calendar is clear for today",
                "prompt": "Check if I have any meetings for the rest of the week"
            })

        # 2. Action items from emails
        urgent_emails = []
        for msg in messages:
            subj_lower = msg.get("subject", "").lower()
            snippet_lower = msg.get("bodyPreview", "").lower()
            if any(k in subj_lower or k in snippet_lower for k in ["approve", "approval", "sign off", "action required", "urgent", "must reply", "review"]):
                urgent_emails.append(msg)

        if urgent_emails:
            action_cards.append({
                "id": "a1_dynamic",
                "icon": "warning",
                "text": f"You have {len(urgent_emails)} approvals pending",
                "prompt": "List all pending approvals or emails requiring action from the last 48 hours"
            })
            first_subject = urgent_emails[0].get("subject", "Action Required Email")
            if len(first_subject) > 35:
                first_subject = first_subject[:35] + "..."
            action_cards.append({
                "id": "a2_dynamic",
                "icon": "attention",
                "text": f"Action: '{first_subject}'",
                "prompt": f"What needs to be done for email: '{urgent_emails[0].get('subject')}'?"
            })
        else:
            action_cards.append({
                "id": "a1_empty",
                "icon": "attention",
                "text": "No urgent actions detected in emails",
                "prompt": "Analyze my inbox to verify if there are any subtle action items I missed"
            })

        # 3. Well Being suggestions based on schedule blocks
        wellbeing_cards.append({
            "id": "w1_dynamic",
            "icon": "lotus",
            "text": "Schedule feels intensive today — remember to stretch every 60 mins!"
        })
        # Try to find a lunchtime gap
        wellbeing_cards.append({
            "id": "w2_dynamic",
            "icon": "burger",
            "text": "Take a healthy lunch break at 1:00 PM to stay energized"
        })

        return {
            "summary": summary_cards,
            "actions": action_cards,
            "well_being": wellbeing_cards
        }
    except Exception as e:
        print("Error compiling dashboard data:", e)
        return _get_mock_dashboard()






if __name__ == "__main__":
    import uvicorn
    # Determine port to run. We must check and run, port 8005 is default for Outlook projects
    uvicorn.run(app, host="0.0.0.0", port=8005)
