"""
FastAPI Backend for Google ADK Workspace MCP Showcase
Provides complete AuthN (Sign In with Google) and AuthZ (Workspace Scopes Consent & Refresh)
so each customer can authenticate with their own credentials.
"""

import os
import time
import uuid
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlencode

import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from fastapi import FastAPI, HTTPException, Request, Response, Depends, Cookie, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, Field
import httpx
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types
import dotenv

# Automatically load .env from project root with override=True
dotenv.load_dotenv(Path(__file__).parent.parent / ".env", override=True)
dotenv.load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk_workspace_mcp")

# Environment & Default Settings
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
DEFAULT_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
os.environ["GOOGLE_CLOUD_PROJECT"] = DEFAULT_PROJECT_ID
os.environ["CLOUDSDK_CORE_PROJECT"] = DEFAULT_PROJECT_ID
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

# Customer OAuth App Credentials (configurable via UI or env)
oauth_config = {
    "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID", ""),
    "client_secret": os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", ""),
    "project_id": DEFAULT_PROJECT_ID,
    "redirect_uri": os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", ""),
}

oauth_pending_states: Dict[str, Dict[str, Any]] = {}

# Standard Google Workspace Scopes
WORKSPACE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# Remote MCP Endpoints
WORKSPACE_ENDPOINTS = {
    "gmail": "https://gmailmcp.googleapis.com/mcp/v1",
    "drive": "https://drivemcp.googleapis.com/mcp/v1",
    "docs": "https://docsmcp.googleapis.com/mcp/v1",
    "sheets": "https://sheetsmcp.googleapis.com/mcp/v1",
    "slides": "https://slidesmcp.googleapis.com/mcp/v1",
    "calendar": "https://calendarmcp.googleapis.com/mcp/v1",
    "chat": "https://chatmcp.googleapis.com/mcp/v1",
    "people": "https://people.googleapis.com/mcp/v1",
}

# In-Memory Customer User Sessions: session_id -> session_data
user_sessions: Dict[str, Dict[str, Any]] = {}
custom_test_token: Optional[str] = None

app = FastAPI(
    title="Google ADK Workspace MCP Assistant - Multi-Tenant Auth",
    description="Enterprise Google ADK assistant supporting per-customer AuthN/AuthZ and Remote Workspace MCP servers.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_or_create_session_id(request: Request, response: Response) -> str:
    """Extracts session ID from cookie or generates a new one."""
    session_id = request.cookies.get("mcp_session_id")
    if not session_id or session_id not in user_sessions:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="mcp_session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=30 * 24 * 3600,
        )
    return session_id


async def refresh_access_token(session: Dict[str, Any]) -> Optional[str]:
    """Refreshes the OAuth access token if a refresh token is present."""
    refresh_token = session.get("refresh_token")
    client_id = oauth_config.get("client_id")
    client_secret = oauth_config.get("client_secret")

    if not (refresh_token and client_id and client_secret):
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                new_access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                session["access_token"] = new_access_token
                session["expires_at"] = time.time() + expires_in
                logger.info(f"Successfully refreshed OAuth token for {session.get('user_info', {}).get('email')}")
                return new_access_token
            else:
                logger.warning(f"Failed to refresh token: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
    return None


async def resolve_credentials(session_id: Optional[str] = None):
    """
    Resolves the active credential according to priority:
    1. Customer OAuth Session (User AuthN + Workspace AuthZ)
    2. Manually provided custom Bearer Token (for quick testing)
    3. Application Default Credentials (ADC) from host environment
    """
    global custom_test_token

    target_project = oauth_config.get("project_id") or DEFAULT_PROJECT_ID or "vtxdemos"

    # 1. Check Customer OAuth Session
    if session_id and session_id in user_sessions:
        session = user_sessions[session_id]
        access_token = session.get("access_token")
        expires_at = session.get("expires_at", 0)

        # Auto-refresh if token expires within 2 minutes
        if access_token and (time.time() > (expires_at - 120)):
            refreshed = await refresh_access_token(session)
            if refreshed:
                access_token = refreshed

        if access_token:
            user = session.get("user_info", {})
            identity = user.get("email", "Authenticated Customer User")
            return access_token, target_project, identity, "oauth2_user", session

    # 2. Check Custom Test Token
    if custom_test_token:
        return custom_test_token, target_project, "Custom Bearer Token", "custom_token", None

    # 3. Fallback to ADC
    try:
        creds, proj = google.auth.default()
        if not creds.valid:
            creds.refresh(GoogleAuthRequest())
        resolved_project = target_project or proj or "vtxdemos"
        identity = getattr(creds, "service_account_email", None) or getattr(creds, "quota_project_id", None) or "ADC Host Principal"
        return creds.token, resolved_project, identity, "adc", None
    except Exception as e:
        logger.warning(f"ADC fallback unavailable: {e}")
        return None, target_project, "Unauthenticated", "none", None


# Request Models
class ConfigUpdateRequest(BaseModel):
    client_id: Optional[str] = Field(None, description="Google OAuth 2.0 Web Client ID")
    client_secret: Optional[str] = Field(None, description="Google OAuth 2.0 Web Client Secret")
    project_id: Optional[str] = Field(None, description="Google Cloud Project ID")
    redirect_uri: Optional[str] = Field(None, description="Custom OAuth redirect URI override")


class TokenRequest(BaseModel):
    token: Optional[str] = Field(None, description="Custom OAuth access token or empty to clear")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt")
    service: str = Field(default="gmail", description="Target Workspace service")


# ---------------------------------------------------------------------------
# AuthN / AuthZ Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/auth/status")
async def get_auth_status(request: Request, response: Response):
    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, session = await resolve_credentials(session_id)

    fingerprint = f"{token[:8]}...{token[-4:]}" if token and len(token) > 12 else "None"
    callback_url = oauth_config.get("redirect_uri") or f"{str(request.base_url).rstrip('/')}/api/auth/callback"

    client_id = oauth_config.get("client_id", "")
    client_id_preview = f"{client_id[:12]}...apps.googleusercontent.com" if client_id and len(client_id) > 20 else ("Configured" if client_id else "Not Set")

    user_info = session.get("user_info") if session else None
    granted_scopes = session.get("scopes", []) if session else []

    return {
        "authenticated": token is not None,
        "auth_type": auth_type,
        "identity": identity,
        "project_id": project_id,
        "token_fingerprint": fingerprint,
        "user_info": user_info,
        "scopes": granted_scopes,
        "oauth_configured": bool(oauth_config.get("client_id") and oauth_config.get("client_secret")),
        "client_id_preview": client_id_preview,
        "redirect_uri": callback_url,
    }


@app.get("/api/auth/login")
async def oauth_login(request: Request, response: Response):
    """
    Initiates Google OAuth 2.0 flow for Customer AuthN + Workspace AuthZ.
    Redirects user to Google Consent Screen.
    """
    session_id = get_or_create_session_id(request, response)
    client_id = oauth_config.get("client_id")

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="OAuth Client ID not configured. Please configure it via the UI Settings modal.",
        )

    callback_url = oauth_config.get("redirect_uri") or f"{str(request.base_url).rstrip('/')}/api/auth/callback"
    oauth_pending_states[session_id] = {
        "redirect_uri": callback_url,
        "timestamp": time.time(),
    }

    params = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "response_type": "code",
        "scope": " ".join(WORKSPACE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": session_id,
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@app.get("/api/auth/callback")
async def oauth_callback(
    request: Request,
    response: Response,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Handles redirect from Google OAuth consent screen.
    Exchanges authorization code for access_token & refresh_token.
    """
    if error:
        logger.warning(f"OAuth callback error: {error}")
        return RedirectResponse(url=f"/?auth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    session_id = state or get_or_create_session_id(request, response)
    pending = oauth_pending_states.pop(session_id, None) or {}
    callback_url = pending.get("redirect_uri") or oauth_config.get("redirect_uri") or f"{str(request.base_url).rstrip('/')}/api/auth/callback"

    client_id = oauth_config.get("client_id")
    client_secret = oauth_config.get("client_secret")

    if not (client_id and client_secret):
        raise HTTPException(status_code=500, detail="OAuth credentials missing during code exchange.")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. Exchange code for tokens
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": callback_url,
                    "grant_type": "authorization_code",
                },
            )

            if token_resp.status_code != 200:
                logger.error(f"Failed token exchange: {token_resp.text}")
                return RedirectResponse(url=f"/?auth_error=token_exchange_failed")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            raw_scopes = token_data.get("scope", "").split()

            # 2. Retrieve User Identity (AuthN)
            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_profile = userinfo_resp.json() if userinfo_resp.status_code == 200 else {}

            # 3. Store in Session
            user_sessions[session_id] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": time.time() + expires_in,
                "user_info": {
                    "email": user_profile.get("email", "unknown"),
                    "name": user_profile.get("name", "User"),
                    "picture": user_profile.get("picture", ""),
                    "hd": user_profile.get("hd", ""),  # Google Workspace domain
                },
                "scopes": raw_scopes,
                "created_at": time.time(),
            }

            logger.info(f"User {user_profile.get('email')} successfully authenticated and authorized.")
            
            res = RedirectResponse(url="/?auth=success")
            res.set_cookie(
                key="mcp_session_id",
                value=session_id,
                httponly=True,
                samesite="lax",
                max_age=30 * 24 * 3600,
            )
            return res

    except Exception as e:
        logger.error(f"Exception during OAuth callback: {e}")
        return RedirectResponse(url=f"/?auth_error={str(e)}")


@app.post("/api/auth/config")
async def update_oauth_config(req: ConfigUpdateRequest):
    """Updates OAuth configuration (Client ID, Secret, GCP Project)."""
    if req.client_id is not None:
        oauth_config["client_id"] = req.client_id.strip()
    if req.client_secret is not None:
        oauth_config["client_secret"] = req.client_secret.strip()
    if req.project_id is not None and req.project_id.strip():
        oauth_config["project_id"] = req.project_id.strip()
        os.environ["GOOGLE_CLOUD_PROJECT"] = req.project_id.strip()
    if req.redirect_uri is not None:
        oauth_config["redirect_uri"] = req.redirect_uri.strip()

    return {
        "message": "OAuth configuration updated successfully.",
        "oauth_configured": bool(oauth_config.get("client_id") and oauth_config.get("client_secret")),
        "project_id": oauth_config["project_id"],
        "redirect_uri": oauth_config.get("redirect_uri") or "default (/api/auth/callback)",
    }


@app.post("/api/auth/upload-client-secret")
async def upload_client_secret(file: UploadFile = File(...)):
    """Accepts a downloaded client_secret_*.json file and configures OAuth."""
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        
        # Check standard Google Cloud JSON structures ('web' or 'installed')
        cred = data.get("web") or data.get("installed")
        if not cred:
            raise HTTPException(status_code=400, detail="Invalid client_secret.json format (missing 'web' or 'installed' block).")

        oauth_config["client_id"] = cred.get("client_id", "").strip()
        oauth_config["client_secret"] = cred.get("client_secret", "").strip()
        if cred.get("project_id"):
            oauth_config["project_id"] = cred.get("project_id").strip()
            os.environ["GOOGLE_CLOUD_PROJECT"] = cred.get("project_id").strip()

        return {
            "message": "client_secret.json imported successfully.",
            "client_id_preview": f"{oauth_config['client_id'][:12]}...apps.googleusercontent.com",
            "project_id": oauth_config["project_id"],
            "oauth_configured": True,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse credentials file: {str(e)}")


@app.post("/api/auth/token")
async def set_direct_token(req: TokenRequest):
    """Fallback: set or clear a direct Bearer token."""
    global custom_test_token
    if req.token and req.token.strip():
        custom_test_token = req.token.strip()
        msg = "Custom token saved."
    else:
        custom_test_token = None
        msg = "Custom token cleared."
    return {"message": msg, "custom_token_set": custom_test_token is not None}


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Logs out the active session."""
    session_id = request.cookies.get("mcp_session_id")
    if session_id and session_id in user_sessions:
        del user_sessions[session_id]
    response.delete_cookie("mcp_session_id")
    return {"message": "Logged out successfully."}


# ---------------------------------------------------------------------------
# MCP Tool Discovery & Chat
# ---------------------------------------------------------------------------

@app.get("/api/mcp/tools")
async def list_mcp_tools(request: Request, response: Response, service: str = Query("gmail")):
    if service not in WORKSPACE_ENDPOINTS:
        raise HTTPException(status_code=400, detail=f"Unsupported service: {service}")

    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, _ = await resolve_credentials(session_id)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please 'Sign in with Google' or configure credentials.",
        )

    endpoint_url = WORKSPACE_ENDPOINTS[service]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
            # 1. MCP initialize handshake
            await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "adk-workspace-ui", "version": "2.0"},
                    },
                },
            )
            # 2. Tools list
            res_tools = await client.post(
                endpoint_url,
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            )
            tools_list = res_tools.json().get("result", {}).get("tools", [])
            return {
                "service": service,
                "endpoint": endpoint_url,
                "auth_type": auth_type,
                "identity": identity,
                "tool_count": len(tools_list),
                "tools": [
                    {
                        "name": t.get("name"),
                        "description": t.get("description", "").splitlines()[0] if t.get("description") else "",
                        "full_description": t.get("description", ""),
                        "parameters": t.get("inputSchema", {}),
                    }
                    for t in tools_list
                ],
            }
    except Exception as e:
        logger.error(f"Error querying MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query MCP tools: {str(e)}")


@app.post("/api/chat")
async def chat_with_agent(request: Request, response: Response, req: ChatRequest):
    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, _ = await resolve_credentials(session_id)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in with your Google account or configure credentials.",
        )

    service = req.service if req.service in WORKSPACE_ENDPOINTS else "gmail"
    endpoint_url = WORKSPACE_ENDPOINTS[service]

    # Set project in environment so Vertex AI client uses target project
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["CLOUDSDK_CORE_PROJECT"] = project_id
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

    async def event_generator():
        start_time = time.time()
        yield f"data: {json.dumps({'type': 'start', 'service': service, 'model': 'gemini-3.7-flash', 'auth_type': auth_type, 'project_id': project_id})}\n\n"
        await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'type': 'status', 'phase': 'connecting', 'text': f'Connecting to {service.upper()} Remote MCP ({endpoint_url})...'})}\n\n"

        try:
            # Create ADK McpToolset with Streamable HTTP parameters
            workspace_toolset = McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=endpoint_url,
                    headers=headers,
                    timeout=30.0,
                    sse_read_timeout=300.0,
                ),
            )

            yield f"data: {json.dumps({'type': 'status', 'phase': 'handshake', 'text': f'Negotiating MCP protocol & loading {service.upper()} tool declarations...'})}\n\n"

            agent = Agent(
                name="workspace_adk_agent",
                model="gemini-3.7-flash",
                instruction=(
                    f"You are a Google Workspace AI assistant connected to {service.upper()} via the Model Context Protocol. "
                    f"You are acting on behalf of user '{identity}' in Google Cloud project '{project_id}'. "
                    "You have access to native Workspace tools. Answer accurately and explain any actions clearly."
                ),
                tools=[workspace_toolset],
            )

            runner = InMemoryRunner(agent=agent)
            adk_session = await runner.session_service.create_session(
                app_name=runner.app_name, user_id=identity
            )

            yield f"data: {json.dumps({'type': 'status', 'phase': 'reasoning', 'text': 'Agent reasoning with gemini-3.7-flash chunk by event...'})}\n\n"

            response_chunks = []
            tool_activity = []

            async for event in runner.run_async(
                session_id=adk_session.id,
                user_id=identity,
                new_message=types.Content(parts=[types.Part.from_text(text=req.message)]),
            ):
                if event.content and event.content.parts:
                    for p in event.content.parts:
                        # Thinking / reasoning chunk text
                        thought_val = getattr(p, "thought", None)
                        if thought_val and isinstance(thought_val, str) and thought_val.strip():
                            yield f"data: {json.dumps({'type': 'thought', 'text': thought_val.strip()})}\n\n"

                        # Tool invocation
                        if hasattr(p, "function_call") and p.function_call:
                            c_name = p.function_call.name
                            c_args = dict(p.function_call.args or {})
                            tool_activity.append({"type": "call", "name": c_name, "args": c_args})
                            args_preview = ", ".join(f"{k}={repr(v)[:20]}" for k, v in list(c_args.items())[:2])
                            yield f"data: {json.dumps({'type': 'tool_call', 'name': c_name, 'args': c_args, 'text': f'Invoking tool: {c_name}({args_preview})'})}\n\n"

                        # Tool response
                        if hasattr(p, "function_response") and p.function_response:
                            r_name = p.function_response.name
                            r_data = p.function_response.response
                            tool_activity.append({"type": "response", "name": r_name, "response": str(r_data)})
                            yield f"data: {json.dumps({'type': 'tool_response', 'name': r_name, 'text': f'Received result from {r_name}'})}\n\n"

                        # Text chunk
                        if p.text:
                            response_chunks.append(p.text)
                            yield f"data: {json.dumps({'type': 'chunk', 'text': p.text})}\n\n"

            full_reply = "".join(response_chunks).strip()
            if not full_reply:
                full_reply = "I processed your request using the Workspace MCP integration."

            elapsed = round(time.time() - start_time, 2)
            yield f"data: {json.dumps({'type': 'done', 'reply': full_reply, 'tool_activity': tool_activity, 'elapsed': elapsed})}\n\n"

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Chat execution error: {err_msg}")
            help_msg = ""
            if "403" in err_msg and ("Forbidden" in err_msg or "PERMISSION_DENIED" in err_msg):
                if auth_type == "adc":
                    help_msg = (
                        "ADC Host Token lacks Google Workspace OAuth scopes (gmail.modify, drive.readonly, etc.). "
                        "Please click 'Sign in with Google' at the top right to authorize your Workspace user scopes, "
                        "or re-authenticate ADC with: "
                        'gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/documents.readonly,https://www.googleapis.com/auth/spreadsheets.readonly"'
                    )
                else:
                    help_msg = (
                        f"Google Workspace MCP requires IAM role 'roles/mcp.toolUser' in project '{project_id}'. "
                        f"Run: gcloud projects add-iam-policy-binding {project_id} --member=\"user:{identity}\" --role=\"roles/mcp.toolUser\""
                    )
            elapsed = round(time.time() - start_time, 2)
            yield f"data: {json.dumps({'type': 'error', 'reply': f'Execution error: {err_msg}', 'help': help_msg, 'elapsed': elapsed})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Mount Static Files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return {"message": "Frontend not found. Please verify frontend/index.html"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8002, reload=True)
