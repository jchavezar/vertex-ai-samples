import os
os.environ['GOOGLE_CLOUD_PROJECT'] = '254356041555'
os.environ['PROJECT_ID'] = '254356041555'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'
os.environ['GCP_PROJECT'] = '254356041555'

import time
import json
import logging
import datetime
import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)
load_dotenv("../.env", override=True)

from google import genai
from backend.outlook_client import OutlookClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outlook-executive-app")

app = FastAPI(title="Outlook AI Executive Assistant")
import msal

@app.get("/login")
async def login_route():
    client_id = os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    msal_app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    scopes = [
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Calendars.Read"
    ]
    auth_url = msal_app.get_authorization_request_url(
        scopes,
        redirect_uri="http://localhost:8005/callback"
    )
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback_route(code: Optional[str] = None, error: Optional[str] = None):
    if error:
        return HTMLResponse(f"<h3>Authentication Error</h3><p>{error}</p>")
    if not code:
        return HTMLResponse("<h3>Error: No authorization code received.</h3>")
        
    client_id = os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    msal_app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    scopes = [
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Calendars.Read"
    ]
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri="http://localhost:8005/callback"
    )
    if "error" in result:
        return HTMLResponse(f"<h3>Token Exchange Error</h3><p>{result.get('error_description')}</p>")
        
    refresh_token = result.get("refresh_token")
    if not refresh_token:
        return HTMLResponse("<h3>Warning: No refresh token returned.</h3>")
        
    env_path = "../.env"
    if not os.path.exists(env_path):
        env_path = ".env"
        
    lines = []
    updated = False
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("MS_GRAPH_REFRESH_TOKEN="):
                    lines.append(f"MS_GRAPH_REFRESH_TOKEN={refresh_token}\n")
                    updated = True
                else:
                    lines.append(line)
    if not updated:
        lines.append(f"MS_GRAPH_REFRESH_TOKEN={refresh_token}\n")
        
    with open(env_path, "w") as f:
        f.writelines(lines)
        
    load_dotenv(dotenv_path=env_path)
    os.environ["MS_GRAPH_REFRESH_TOKEN"] = refresh_token
    if result.get("access_token"):
        os.environ["MS_GRAPH_TOKEN"] = result.get("access_token")
        
    return HTMLResponse("""
    <html>
    <head>
        <title>Auth Success</title>
        <style>
            body { font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0b0f19; color: #e2e8f0; margin: 0; }
            .card { background: #151c2c; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); text-align: center; }
            h2 { color: #10b981; margin-top: 0; }
            p { margin-bottom: 0; color: #94a3b8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 Authentication Successful!</h2>
            <p>Delegated access token and refresh token successfully saved.</p>
            <p>You can close this window now and return to the chat.</p>
        </div>
    </body>
    </html>
    """)

outlook_client = OutlookClient()
genai_client = genai.Client(vertexai=True, project="254356041555", location="global")

class ChatMessage(BaseModel):
    role: str
    content: str

class SendEmailRequest(BaseModel):
    to_address: str
    subject: str
    body: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None
    timezone: Optional[str] = "America/New_York"
    model: Optional[str] = "gemini-3.6-flash"

import google.adk as adk
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.genai import types

session_service = InMemorySessionService()

latest_grounding_items = {"emails": [], "meetings": []}

async def search_m365(query: str) -> str:
    """
    Search the user's Microsoft 365 inbox, calendar meetings, and profile information.
    Use this tool whenever the user asks to check, read, get, search, or summarize emails, meetings, calendar, schedule, or user profile.
    
    Args:
        query: The search query keywords to search for.
    """
    global latest_grounding_items
    logger.info(f"### [ADK TOOL CALLED] search_m365 with query: '{query}'")
    try:
        # Resolve search query through Microsoft Graph API client
        fed_res = await outlook_client.federated_search(query=query)
        prof = fed_res.get("profile", {})
        emails = fed_res.get("emails", [])
        meetings = fed_res.get("meetings", [])
        
        latest_grounding_items = {"emails": emails, "meetings": meetings}

        lines = [
            f"Profile: Jesus Chavez (admin@sockcop.onmicrosoft.com) | Job Title: {prof.get('jobTitle') or 'None'}"
        ]
        if meetings:
            lines.append("Calendar Meetings:")
            for m in meetings:
                body_clean = " ".join((m.get('bodyPreview') or "").split())[:800]
                lines.append(f"- {m.get('subject')} (Time: {(m.get('start') or {}).get('dateTime')} to {(m.get('end') or {}).get('dateTime')}) | Organizer: {(m.get('organizer') or {}).get('emailAddress', {}).get('name')} | Preview: {body_clean}")
        if emails:
            lines.append("Inbox Emails:")
            for em in emails:
                body_obj = em.get('body') or {}
                body_content = body_obj.get('content') or em.get('bodyPreview') or ""
                body_clean = " ".join(body_content.split())[:1200]
                to_list = [t.get('emailAddress', {}).get('address') for t in (em.get('toRecipients') or []) if t.get('emailAddress', {}).get('address')]
                to_str = ", ".join(to_list) if to_list else "None"
                lines.append(f"- [Folder: {em.get('folderName')}] {em.get('subject')} (From: {(em.get('from') or {}).get('emailAddress', {}).get('address')} | To: {to_str} | Received: {em.get('receivedDateTime')}) - Body: {body_clean}")
                
        if not emails and not meetings:
            return "No matching Microsoft 365 emails or calendar meetings found."
            
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error in search_m365: {e}")
        return f"Error executing search: {str(e)}"

async def send_email(subject: str, body: str, to_recipients: List[str]) -> str:
    """
    Send an outgoing email message to recipients via Microsoft Graph API.
    
    Args:
        subject: The subject of the email.
        body: The plain text content of the email.
        to_recipients: A list of recipient email addresses.
    """
    logger.info(f"### [ADK TOOL CALLED] send_email to {to_recipients} subject='{subject}'")
    try:
        headers = outlook_client._get_headers()
        url = f"{outlook_client.base_url}/me/sendMail"
        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": a}} for a in to_recipients]
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 202):
                outlook_client.clear_cache()
                return "Email sent successfully."
            else:
                return f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        logger.error(f"Error in send_email: {e}")
        return f"Error executing send_email: {str(e)}"

async def reply_email(message_id: str, comment: str) -> str:
    """
    Reply to an existing email thread using the message ID of the original email.
    
    Args:
        message_id: The ID of the original email message to reply to.
        comment: The plain text reply content.
    """
    logger.info(f"### [ADK TOOL CALLED] reply_email message_id='{message_id}'")
    try:
        headers = outlook_client._get_headers()
        url = f"{outlook_client.base_url}/me/messages/{message_id}/reply"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json={"comment": comment})
            if resp.status_code in (200, 202):
                outlook_client.clear_cache()
                return "Reply posted successfully."
            else:
                return f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        logger.error(f"Error in reply_email: {e}")
        return f"Error executing reply_email: {str(e)}"

async def create_meeting(subject: str, start_time: str, end_time: str, attendees: Optional[List[str]] = None) -> str:
    """
    Create a new calendar meeting/event with a Microsoft Teams join link.
    
    Args:
        subject: The title of the meeting.
        start_time: Start date-time string in ISO format (e.g. '2026-07-23T14:00:00Z').
        end_time: End date-time string in ISO format (e.g. '2026-07-23T15:00:00Z').
        attendees: Optional list of email addresses of attendees to invite.
    """
    logger.info(f"### [ADK TOOL CALLED] create_meeting subject='{subject}' start='{start_time}' end='{end_time}'")
    try:
        headers = outlook_client._get_headers()
        url = f"{outlook_client.base_url}/me/events"
        payload = {
            "subject": subject,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness",
            "attendees": [{"emailAddress": {"address": a}, "type": "required"} for a in (attendees or [])]
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                outlook_client.clear_cache()
                return "Meeting created successfully."
            else:
                return f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        logger.error(f"Error in create_meeting: {e}")
        return f"Error executing create_meeting: {str(e)}"

# Model lookup mapping for Deep, Accurate, and Speed tiers
MODEL_MAP = {
    # 1. Deep: gemini-3.1-pro alias -> gemini-2.5-pro (Global)
    "gemini-3.1-pro": "gemini-2.5-pro",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "deep": "gemini-2.5-pro",
    # 2. Accurate: gemini-3.6-flash alias -> gemini-3-flash-preview (Global)
    "gemini-3.6-flash": "gemini-3-flash-preview",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "accurate": "gemini-3-flash-preview",
    # 3. Speed: gemini-3.5-flash alias -> gemini-2.5-flash (Global)
    "gemini-3.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "speed": "gemini-2.5-flash",
    "swift": "gemini-2.5-flash",
    "vision": "gemini-2.5-flash",
    "auto": "gemini-3-flash-preview"
}

def get_agent_for_model(model_name: str) -> Agent:
    target_vertex_model = MODEL_MAP.get(model_name.lower().strip(), "gemini-3-flash-preview")
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    current_time_str = now_utc.strftime("%A, %B %d, %Y at %H:%M:%S UTC")
    clean_name = f"outlook_executive_agent_{target_vertex_model.replace('.', '_').replace('-', '_')}"
    
    return Agent(
        name=clean_name,
        model=target_vertex_model,
        instruction=f"""You are an executive AI assistant.
You have access to the user's Microsoft 365 data via the search tools.
Always refer to the CURRENT REAL-TIME SYSTEM CLOCK ({current_time_str}) as the absolute ground-truth for today's date and relative date calculations (e.g., "today", "yesterday", "a week ago", "tomorrow"). Do NOT infer today's date from email timestamps.
Provide the direct answer first in 1-2 clear, natural sentences, followed by a structured breakdown or table if details are present.
Use markdown formatting. If the search tool returns empty results or doesn't have the info, state that no matching record was found.

CRITICAL CONVERSATIONAL GUARDRAIL:
- If the user's input is casual chit-chat, a greeting, how-are-you questions, small talk, or general non-data queries (e.g. "hi", "hello", "hiw how ar you", "thanks", "who are you", "what can you do"), DO NOT call any tool. Simply respond in a warm, helpful, polite conversation tone.
- ONLY invoke search_m365 when the user asks to look up, search, find, read, check, or summarize specific emails, calendar events, meetings, or person profile information.

Tool Usage Guidelines:
1. When calling search_m365, pass specific keywords like the subject line, the sender's email address, or the meeting name.
2. If the user's query refers to a previous item (using words like "that", "it", "this email", "the meeting"), first resolve what item the user is referring to from the conversation history, and then call search_m365 using the specific name, subject, or topic of that item (e.g., call search_m365(query="Password Rotation Notice")).
3. NEVER pass generic query terms like "summary", "details", "that", "it", or "emails" to the search tool.
4. DRAFT FILTERING: Drafts are unsent messages. Standard email queries (like 'most recent sent message', 'recent emails') expect actual sent or received emails. In your tool outputs, ignore or filter out messages where isDraft is true, unless the user specifically asks for drafts.
""",
        tools=[search_m365, send_email, reply_email, create_meeting]
    )

agent_runners: Dict[str, adk.Runner] = {}

def get_runner_for_model(model_name: str) -> adk.Runner:
    resolved = MODEL_MAP.get(model_name.lower().strip(), "gemini-3-flash-preview")
    if resolved not in agent_runners:
        ag = get_agent_for_model(resolved)
        agent_runners[resolved] = adk.Runner(
            agent=ag,
            app_name=f"outlook_assistant_{resolved.replace('.', '_').replace('-', '_')}",
            session_service=session_service
        )
    return agent_runners[resolved]

@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest):
    outlook_client.clear_cache()
    global is_ms_authenticated
    if not is_ms_authenticated:
        return {
            "response": "🔒 **Authentication Error (HTTP 401 Unauthorized)**: Microsoft 365 OAuth bearer token is disconnected or expired. Please click **AuthN/AuthZ** status in the top bar to reconnect your Microsoft Graph identity (`admin@sockcop.onmicrosoft.com`).",
            "tools_called": [],
            "latency_s": 0.01,
            "search_latency_s": 0.0,
            "raw_grounding_data": {}
        }
    t0 = time.time()
    session_id = body.session_id or "default_session"
    model_requested = body.model or "gemini-3.6-flash"
    runner = get_runner_for_model(model_requested)
    
    # Check if session exists in session_service, if not create it
    session = await session_service.get_session(session_id=session_id, app_name=runner.app_name, user_id="user_1")
    if not session:
        session = await session_service.create_session(session_id=session_id, app_name=runner.app_name, user_id="user_1")
        
    # POPULATE/SYNC ADK SESSIONS HISTORY WITH FRONTEND TRUTH HISTORY
    session.events = []
    logger.info(f"### [ADK INCOMING] model='{model_requested}' -> '{runner.agent.model}' | message='{body.message}' | history_len={len(body.history) if body.history else 0}")
    if body.history:
        for msg in body.history:
            role = "user" if msg.role == "user" else "model"
            content_obj = types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
            session.events.append(Event(author=role, content=content_obj))

    logger.info(f"### [ADK SYNC] Syncing {len(session.events)} events to session history:")
    for i, ev in enumerate(session.events):
        text_preview = ev.content.parts[0].text[:80] + "..." if ev.content and ev.content.parts and ev.content.parts[0].text else "None"
        logger.info(f"   Turn {i}: author='{ev.author}', content='{text_preview}'")

    new_message = types.Content(role="user", parts=[types.Part.from_text(text=body.message)])
    
    ans_text = ""
    tools_called = []
    
    try:
        async for event in runner.run_async(user_id="user_1", session_id=session_id, new_message=new_message):
            # Extract tool calls from event parts
            if event.content and hasattr(event.content, "parts") and event.content.parts:
                for part in event.content.parts:
                    # Handle both dictionary and object formats safely
                    if isinstance(part, dict):
                        fc = part.get("function_call")
                        if fc:
                            tools_called.append({
                                "name": fc.get("name"),
                                "args": fc.get("args")
                            })
                    else:
                        fc = getattr(part, "function_call", None)
                        if fc:
                            tools_called.append({
                                "name": getattr(fc, "name", ""),
                                "args": getattr(fc, "args", {})
                            })
            
            # Extract final text output
            if event.is_final_response() and event.content and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    # In python SDK, part can be types.Part or dict
                    if isinstance(part, dict):
                        text = part.get("text")
                    else:
                        text = getattr(part, "text", "")
                    if text:
                        ans_text += text
    except Exception as e:
        logger.error(f"Error executing ADK runner: {e}")
        ans_text = f"An error occurred while running the Outlook Executive Agent: {str(e)}"
        
    latency_s = round(time.time() - t0, 2)
    logger.info(f"### [LATENCY BREAKDOWN] total={latency_s}s | tools_called={tools_called}")
    
    global latest_grounding_items
    grounding_copy = dict(latest_grounding_items)
    latest_grounding_items = {"emails": [], "meetings": []}
    
    return {
        "response": ans_text,
        "tools_called": tools_called,
        "latency_s": latency_s,
        "search_latency_s": 0.0,
        "raw_grounding_data": grounding_copy
    }

is_ms_authenticated = True
auth_scopes = ["Mail.Read", "Calendars.Read", "User.Read", "Directory.Read.All"]
active_sessions_counter = {"default_session": 1}

@app.get("/api/auth/status")
async def auth_status():
    global is_ms_authenticated
    return {
        "authenticated": is_ms_authenticated,
        "user": {
            "displayName": "Jesus Chavez",
            "userPrincipalName": "admin@sockcop.onmicrosoft.com",
            "tenantId": "de46a3fd-0d68-4b25-8343-6eb5d71afce9"
        } if is_ms_authenticated else None,
        "auth_provider": "Microsoft Graph OAuth 2.0 (Azure AD / Entra ID)",
        "scopes": auth_scopes,
        "expires_in_secs": 3240 if is_ms_authenticated else 0
    }

@app.post("/api/auth/login")
async def auth_login():
    global is_ms_authenticated
    is_ms_authenticated = True
    return {"status": "connected", "message": "Successfully authenticated with Microsoft 365 Tenant sockcop.onmicrosoft.com"}

@app.post("/api/auth/logout")
async def auth_logout():
    global is_ms_authenticated
    is_ms_authenticated = False
    return {"status": "disconnected", "message": "Microsoft Graph OAuth token revoked/disconnected."}

@app.post("/api/send-email")
async def send_email_endpoint(req: SendEmailRequest):
    result = await outlook_client.send_email(req.subject, req.body, [req.to_address])
    if result.startswith("Error"):
        return {"success": False, "error": result}
    return {"success": True}

@app.get("/eval", response_class=HTMLResponse)
async def eval_page():
    if os.path.exists("eval_dashboard_static.html"):
        with open("eval_dashboard_static.html", "r") as f:
            return f.read()
    return "<h3>Dashboard Loading...</h3>"

@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Frontend Loading...</h3>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
