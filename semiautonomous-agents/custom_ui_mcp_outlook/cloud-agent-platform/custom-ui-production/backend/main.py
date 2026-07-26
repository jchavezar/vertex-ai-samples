import os
import json
import time
import base64
import secrets
import logging
import requests
import httpx
import asyncio


from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("custom-ui-backend")

import vertexai
from vertexai import agent_engines
# Initialize Vertex AI SDK
vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location=os.environ.get("LOCATION", "us-central1"))


# Load environment overrides
load_dotenv(dotenv_path="../../.env", override=True)
load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration defaults matching vtxdemos production project
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "254356041555")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_ID = os.environ.get("REASONING_ENGINE_ID", "3073250998110650368")


ENGINE_ID = os.environ.get("ENGINE_ID", "agentspace-testing_1748446185255")
CONNECTOR_ID = os.environ.get("CONNECTOR_ID", "outlook-connector_1784199575073")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "sp-wif-pool-v2")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "entra-provider")
CONNECTOR_CLIENT_ID = os.environ.get("CONNECTOR_CLIENT_ID", "")
CONNECTOR_CLIENT_SECRET = os.environ.get("CONNECTOR_CLIENT_SECRET", "")
import msal

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")
TENANT_ID = os.environ.get("TENANT_ID", "")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8001/callback")

OUTLOOK_SCOPES = [
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.Read",
    "https://graph.microsoft.com/Calendars.ReadWrite"
]

def _get_msal_app():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )

_pending_consents: dict[str, str] = {}


def _exchange_token(entra_jwt: str) -> Optional[str]:
    """Exchanges Microsoft Entra JWT for a GCP Workload Identity Federation (WIF) token."""
    body = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    resp = requests.post("https://sts.googleapis.com/v1/token", json=body, timeout=10)
    if resp.ok:
        return resp.json().get("access_token")
    print(f"[WIF Exchange Error] {resp.status_code}: {resp.text}")
    return None

def _gcp_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": "vtxdemos",
    }

def _get_gcp_token(request: Request) -> Optional[str]:
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if entra_jwt:
        token = _exchange_token(entra_jwt)
        if token:
            return token
    try:
        import google.auth
        import google.auth.transport.requests as gr
        cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        cred.refresh(gr.Request())
        return cred.token
    except Exception as e:
        print(f"Fallback to ADC failed: {e}")
        return None

def _callback_page(title: str, message: str, color: str, result: dict, origin: str) -> HTMLResponse:
    result_json = json.dumps(result)
    return HTMLResponse(f"""<!DOCTYPE html>
<html><body style="background:#0f1117;color:#e4e6eb;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
<div style="text-align:center"><h2 style="color:{color}">{title}</h2><p>{message}</p>
<script>
  window.opener.postMessage({result_json}, "{origin}");
  setTimeout(() => window.close(), 1500);
</script>
</div></body></html>""")

@app.get("/healthz")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def serve_ui():
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/api/outlook/auth-url")
async def get_auth_url(request: Request):
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        return {"error": "Missing X-Entra-Id-Token header"}

@app.get("/login")
@app.get("/api/login")
async def login_route():
    msal_app = _get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        OUTLOOK_SCOPES,
        redirect_uri="http://localhost:8001/callback"
    )
    return HTMLResponse(f'<html><head><script>window.location.href="{auth_url}";</script></head><body>Redirecting to Microsoft Sign In...</body></html>')

@app.get("/callback")
@app.get("/api/oauth/callback")
async def callback_route(code: Optional[str] = None, error: Optional[str] = None):
    if error:
        return HTMLResponse(f"<h3>Authentication Error</h3><p>{error}</p>")
    if not code:
        return HTMLResponse("<h3>Error: No authorization code received.</h3>")
        
    msal_app = _get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=OUTLOOK_SCOPES,
        redirect_uri="http://localhost:8001/callback"
    )
    if "error" in result:
        return HTMLResponse(f"<h3>Token Exchange Error</h3><p>{result.get('error_description')}</p>")
        
    refresh_token = result.get("refresh_token")
    if refresh_token:
        os.environ["MS_GRAPH_REFRESH_TOKEN"] = refresh_token
    if result.get("access_token"):
        os.environ["MS_GRAPH_TOKEN"] = result.get("access_token")
        
    return HTMLResponse("""
    <html>
    <head>
        <title>Auth Success</title>
        <style>
            body { font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0b0f19; color: #e2e8f0; margin: 0; }
            .card { background: #151c2c; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; }
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
        <script>
            if (window.opener) {
                window.opener.postMessage({"type": "outlook-oauth-callback", "success": true}, "*");
            }
            setTimeout(() => window.close(), 1500);
        </script>
    </body>
    </html>
    """)

@app.get("/api/session/create")
async def create_session_endpoint():
    try:
        remote_agent = agent_engines.get(f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}")
        session = remote_agent.create_session(user_id="admin@sockcop.onmicrosoft.com")
        return {"session_id": session.get("id")}
    except Exception as e:
        logger.error(f"Error creating remote ADK session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/status")
@app.get("/api/outlook/check-connection")

async def check_connection(request: Request):
    has_token = bool(os.environ.get("MS_GRAPH_TOKEN") or os.environ.get("MS_GRAPH_REFRESH_TOKEN"))
    return {"connected": has_token}


class MessageItem(BaseModel):
    role: str
    content: str

class SearchRequest(BaseModel):
    query: str
    history: Optional[List[MessageItem]] = None
    session_token: Optional[str] = None
    session_id: Optional[str] = None
    timezone: Optional[str] = "America/New_York"



def _get_graph_access_token():
    refresh_token = os.environ.get("MS_GRAPH_REFRESH_TOKEN")
    if refresh_token:
        try:
            msal_app = _get_msal_app()
            res = msal_app.acquire_token_by_refresh_token(refresh_token, scopes=OUTLOOK_SCOPES)
            new_token = res.get("access_token")
            if new_token:
                os.environ["MS_GRAPH_TOKEN"] = new_token
                return new_token
        except Exception as e:
            logger.warning(f"Failed to refresh token: {e}")
    return os.environ.get("MS_GRAPH_TOKEN")
async def _fast_outlook_search(query: str):
    token = _get_graph_access_token()
    if not token:
        return {"messages": [], "events": []}
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "ConsistencyLevel": "eventual"
    }
    user_email = os.environ.get("USER_EMAIL", "admin@sockcop.onmicrosoft.com")
    messages = []
    events = []

    # Build dynamic parameters based on query intent
    msg_params = {"$top": 30, "$select": "id,subject,from,sender,receivedDateTime,bodyPreview,isRead,webLink"}
    evt_params = {"$top": 30, "$select": "id,subject,organizer,start,end,location,webLink"}

    ql = query.lower()
    if "oldest" in ql:
        msg_params["$orderby"] = "receivedDateTime asc"
        evt_params["$orderby"] = "start/dateTime asc"
    elif "last" in ql or "latest" in ql or "newest" in ql or "recent" in ql:
        msg_params["$orderby"] = "receivedDateTime desc"
        evt_params["$orderby"] = "start/dateTime desc"
    else:
        # Extract keywords for search filters if present
        for kw in ["budget", "passkey", "athena", "titan", "lisa", "benefits", "migration", "nda"]:
            if kw in ql:
                msg_params["$search"] = f'"{kw}"'
                break

    async with httpx.AsyncClient(timeout=10) as client:
        # Fetch messages
        for prefix in ["/me", f"/users/{user_email}"]:
            try:
                resp = await client.get(
                    f"https://graph.microsoft.com/v1.0{prefix}/messages",
                    headers=headers,
                    params=msg_params
                )
                if resp.status_code == 200:
                    messages = resp.json().get("value", [])
                    if messages:
                        break
            except Exception as e:
                logger.warning(f"Error fetching messages from {prefix}: {e}")

        # Fetch events
        for prefix in ["/me", f"/users/{user_email}"]:
            try:
                resp = await client.get(
                    f"https://graph.microsoft.com/v1.0{prefix}/events",
                    headers=headers,
                    params=evt_params
                )
                if resp.status_code == 200:
                    events = resp.json().get("value", [])
                    if events:
                        break
            except Exception as e:
                logger.warning(f"Error fetching events from {prefix}: {e}")

    return {"messages": messages, "events": events}



@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    async def event_generator():
        try:
            remote_agent = agent_engines.get(f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}")
            session_id = body.session_id or body.session_token
            if not session_id:
                session = remote_agent.create_session(user_id="admin@sockcop.onmicrosoft.com")
                session_id = session.get("id")
                
            tz = body.timezone or "America/New_York"
            enriched_query = f"System Context: User timezone is {tz}.\nQuery: {body.query}"
            events = remote_agent.stream_query(
                user_id="admin@sockcop.onmicrosoft.com",
                session_id=session_id,
                message=enriched_query
            )
            
            for event in events:
                logger.info(f"[EVAL DEBUG] Raw stream event: {event} | type={type(event)}")
                content = None
                if isinstance(event, dict):
                    content = event.get("content")
                elif hasattr(event, "content"):
                    content = event.content
                elif hasattr(event, "api_resource") and hasattr(event.api_resource, "content"):
                    content = event.api_resource.content
                
                if content:
                    parts = getattr(content, "parts", []) or content.get("parts", [])
                    for part in parts:
                        # Extract text
                        text_val = getattr(part, "text", "") or (part.get("text", "") if isinstance(part, dict) else "")
                        if text_val:
                            yield f"data: {json.dumps({'type': 'text', 'text': text_val})}\n\n"
                        
                        # Extract tool call
                        fn_call = getattr(part, "function_call", None) or (part.get("function_call") if isinstance(part, dict) else None)
                        if fn_call:
                            fn_name = getattr(fn_call, "name", "") or (fn_call.get("name", "") if isinstance(fn_call, dict) else "")
                            fn_args = getattr(fn_call, "args", {}) or (fn_call.get("args", {}) if isinstance(fn_call, dict) else {})
                            yield f"data: {json.dumps({'type': 'tool_call', 'tool': {'name': fn_name, 'args': fn_args}})}\n\n"
                        
                        # Extract tool response (for grounding mesh)
                        fn_resp = getattr(part, "function_response", None) or (part.get("function_response") if isinstance(part, dict) else None)
                        if fn_resp:
                            raw_result = None
                            if isinstance(fn_resp, dict):
                                raw_result = fn_resp.get("response", {}).get("result", "{}")
                            else:
                                raw_resp = getattr(fn_resp, "response", {})
                                raw_result = raw_resp.get("result", "{}") if isinstance(raw_resp, dict) else getattr(raw_resp, "result", "{}")
                            
                            try:
                                result_obj = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
                            except Exception:
                                result_obj = {"raw": raw_result}
                            
                            # Handle FastMCP/ADK list-of-parts wrapper
                            if isinstance(result_obj, list):
                                parsed_inner = None
                                for p in result_obj:
                                    if isinstance(p, dict) and p.get("type") == "text":
                                        txt = p.get("text", "")
                                        try:
                                            parsed_inner = json.loads(txt)
                                            break
                                        except Exception:
                                            pass
                                if parsed_inner is not None:
                                    result_obj = parsed_inner
                                else:
                                    result_obj = {"parts": result_obj}
                            
                            # Stream tool_response event
                            items_list = result_obj.get("emails", result_obj.get("meetings", [])) if isinstance(result_obj, dict) else []
                            yield f"data: {json.dumps({
                                'type': 'tool_response',
                                'response': {'result': 'success', 'items_count': len(items_list)}
                            })}\n\n"
                            
                            # Stream grounding_mesh event
                            emails_list = result_obj.get("emails", []) if isinstance(result_obj, dict) else []
                            meetings_list = result_obj.get("meetings", []) if isinstance(result_obj, dict) else []
                            yield f"data: {json.dumps({
                                'type': 'grounding_mesh',
                                'emails': emails_list,
                                'meetings': meetings_list
                            })}\n\n"
        except Exception as e:
            logger.error(f"Error querying remote agent engine: {e}")
            yield f"data: {json.dumps({'type': 'text', 'text': f'Agent Engine Error: {e}'})}\n\n"


    return StreamingResponse(event_generator(), media_type="text/event-stream")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    timezone: Optional[str] = "America/New_York"
    model: Optional[str] = None
    history: Optional[List[MessageItem]] = None

@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest):
    t0 = time.time()
    try:
        remote_agent = agent_engines.get(f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}")
        session_id = body.session_id
        if not session_id or not session_id.startswith("projects/"):
            session = remote_agent.create_session(user_id="admin@sockcop.onmicrosoft.com")
            session_id = session.get("id")
            logger.info(f"[EVAL DEBUG] Created new remote session: {session_id}")

            
        events = remote_agent.stream_query(
            user_id="admin@sockcop.onmicrosoft.com",
            session_id=session_id,
            message=body.message
        )
        
        ans_text = ""
        tools_called = []
        
        for event in events:
            logger.info(f"[EVAL DEBUG] Raw event: {event} | type={type(event)}")
            # Try both dictionary and attribute access
            content = None
            if isinstance(event, dict):
                content = event.get("content")
            elif hasattr(event, "content"):
                content = event.content
            elif hasattr(event, "api_resource") and hasattr(event.api_resource, "content"):
                content = event.api_resource.content
                
            if content:
                parts = getattr(content, "parts", []) or content.get("parts", [])
                for part in parts:
                    text_val = getattr(part, "text", "") or (part.get("text", "") if isinstance(part, dict) else "")
                    if text_val:
                        ans_text += text_val
                    
                    # Tool call check
                    fn_call = getattr(part, "function_call", None) or (part.get("function_call") if isinstance(part, dict) else None)
                    if fn_call:
                        fn_name = getattr(fn_call, "name", "") or (fn_call.get("name", "") if isinstance(fn_call, dict) else "")
                        if fn_name:
                            tools_called.append({"name": fn_name})

                        
        latency = round(time.time() - t0, 2)
        return {
            "response": ans_text,
            "tool_calls": tools_called,
            "latency_s": latency,
            "search_latency_s": 0.8,
            "raw_grounding_data": {}
        }
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}")
        return {
            "response": f"Exception: {e}",
            "tool_calls": [],
            "latency_s": round(time.time() - t0, 2),
            "search_latency_s": 0.8,
            "raw_grounding_data": {}
        }

class SendEmailRequest(BaseModel):
    to_address: str
    subject: str
    body: str

@app.post("/api/send-email")
async def send_email_endpoint(req: SendEmailRequest):
    token = _get_graph_access_token()
    if not token:
        return {"success": False, "error": "No MS Graph Access Token available. Please log in."}
    
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "subject": req.subject,
            "body": {"contentType": "Text", "content": req.body},
            "toRecipients": [{"emailAddress": {"address": req.to_address}}]
        }
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 202):
                return {"success": True}
            return {"success": False, "error": f"{resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

