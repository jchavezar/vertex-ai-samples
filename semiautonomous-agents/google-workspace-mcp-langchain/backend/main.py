"""
FastAPI Backend for LangChain Workspace MCP Showcase
Provides complete AuthN (Sign In with Google) and AuthZ (Workspace Scopes Consent & Refresh)
so each customer can authenticate with their own credentials.
"""

import os
import time
import uuid
import json
import asyncio
import logging
import operator
from typing import Optional, Dict, Any, List, Sequence, Annotated, TypedDict
from pathlib import Path
from urllib.parse import urlencode
import copy
import subprocess

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
from google import genai
from google.genai import types
import dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END

# Automatically load .env from project root with override=True
dotenv.load_dotenv(Path(__file__).parent.parent / ".env", override=True)
dotenv.load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain_workspace_mcp")

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
DEFAULT_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
os.environ["GOOGLE_CLOUD_PROJECT"] = DEFAULT_PROJECT_ID
os.environ["CLOUDSDK_CORE_PROJECT"] = DEFAULT_PROJECT_ID
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

oauth_config = {
    "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID", ""),
    "client_secret": os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", ""),
    "project_id": DEFAULT_PROJECT_ID,
    "redirect_uri": os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", ""),
}

oauth_pending_states: Dict[str, Dict[str, Any]] = {}

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

user_sessions: Dict[str, Dict[str, Any]] = {}
custom_test_token: Optional[str] = None
SESSION_CACHE_FILE = Path(__file__).parent / ".session_tokens.json"


def load_cached_sessions():
    if SESSION_CACHE_FILE.exists():
        try:
            with open(SESSION_CACHE_FILE, "r") as f:
                data = json.load(f)
                user_sessions.update(data)
                logger.info(f"Loaded {len(data)} cached session(s) from {SESSION_CACHE_FILE}")
        except Exception as e:
            logger.warning(f"Failed to load session cache: {e}")


def save_cached_sessions():
    try:
        with open(SESSION_CACHE_FILE, "w") as f:
            json.dump(user_sessions, f)
    except Exception as e:
        logger.warning(f"Failed to save session cache: {e}")


load_cached_sessions()

app = FastAPI(
    title="LangChain Workspace MCP Assistant - Multi-Tenant Auth",
    description="Enterprise LangChain assistant supporting per-customer AuthN/AuthZ and Remote Workspace MCP servers.",
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
    # 1. Query parameter override
    query_session = request.query_params.get("session_id")
    if query_session and query_session in user_sessions:
        response.set_cookie(
            key="mcp_session_id_langchain",
            value=query_session,
            httponly=False,
            samesite="lax",
            max_age=30 * 24 * 3600,
        )
        return query_session

    # 2. Existing cookie matching active session
    session_id = request.cookies.get("mcp_session_id_langchain")
    if session_id and session_id in user_sessions:
        return session_id

    # 3. Default to active authenticated session if available
    auth_sessions = [sid for sid, s in user_sessions.items() if s.get("user_info")]
    if auth_sessions:
        latest = auth_sessions[-1]
        response.set_cookie(
            key="mcp_session_id_langchain",
            value=latest,
            httponly=False,
            samesite="lax",
            max_age=30 * 24 * 3600,
        )
        return latest

    # 4. Generate new anonymous session
    session_id = str(uuid.uuid4())
    response.set_cookie(
        key="mcp_session_id_langchain",
        value=session_id,
        httponly=False,
        samesite="lax",
        max_age=30 * 24 * 3600,
    )
    return session_id


async def refresh_access_token(session: Dict[str, Any]) -> Optional[str]:
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
                logger.info(f"Refreshed token for {session.get('user_info', {}).get('email')}")
                return new_access_token
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
    return None


async def resolve_credentials(session_id: Optional[str] = None):
    global custom_test_token

    target_project = oauth_config.get("project_id") or DEFAULT_PROJECT_ID or "vtxdemos"

    if session_id and session_id in user_sessions:
        session = user_sessions[session_id]
        access_token = session.get("access_token")
        expires_at = session.get("expires_at", 0)

        if access_token and (time.time() > (expires_at - 120)):
            refreshed = await refresh_access_token(session)
            if refreshed:
                access_token = refreshed

        if access_token:
            user = session.get("user_info", {})
            identity = user.get("email", "Authenticated Customer User")
            return access_token, target_project, identity, "oauth2_user", session

    if custom_test_token:
        return custom_test_token, target_project, "Custom Bearer Token", "custom_token", None

    try:
        creds, proj = google.auth.default()
        if not creds.valid:
            creds.refresh(GoogleAuthRequest())
        resolved_project = target_project or proj or "vtxdemos"

        # Determine user account email for ADC
        adc_email = None
        try:
            acc_proc = subprocess.run(
                ["gcloud", "config", "get-value", "account"],
                capture_output=True,
                text=True,
                timeout=1.5,
            )
            if acc_proc.returncode == 0 and acc_proc.stdout.strip():
                lines = [l.strip() for l in acc_proc.stdout.strip().splitlines() if "@" in l]
                if lines:
                    adc_email = lines[-1]
        except Exception:
            pass

        if not adc_email:
            adc_email = getattr(creds, "service_account_email", None) or "admin@jesusarguelles.altostrat.com"

        name_part = adc_email.split("@")[0].replace(".", " ").title() if adc_email else "ADC Host"
        user_info = {
            "name": name_part,
            "email": adc_email,
            "picture": None,
        }
        adc_session = {
            "user_info": user_info,
            "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
        }
        return creds.token, resolved_project, adc_email, "adc", adc_session
    except Exception as e:
        logger.warning(f"ADC fallback unavailable: {e}")
        return None, target_project, "Unauthenticated", "none", None


class ConfigUpdateRequest(BaseModel):
    client_id: Optional[str] = Field(None, description="Google OAuth 2.0 Web Client ID")
    client_secret: Optional[str] = Field(None, description="Google OAuth 2.0 Web Client Secret")
    project_id: Optional[str] = Field(None, description="Google Cloud Project ID")
    redirect_uri: Optional[str] = Field(None, description="Custom OAuth redirect URI override")


class TokenRequest(BaseModel):
    token: Optional[str] = Field(None, description="Custom OAuth access token")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt")
    service: str = Field(default="gmail", description="Target Workspace service")
    stream: Optional[bool] = Field(default=None, description="Stream response as SSE")


def get_effective_redirect_uri(request: Optional[Request] = None, override_uri: Optional[str] = None) -> str:
    # 1. Explicit override from function parameter
    if override_uri and override_uri.strip():
        return override_uri.strip()
    # 2. Query param from request (e.g., /api/auth/login?redirect_uri=...)
    if request:
        req_uri = request.query_params.get("redirect_uri")
        if req_uri and req_uri.strip():
            return req_uri.strip()
    # 3. Environment or UI configured redirect_uri
    configured = (oauth_config.get("redirect_uri") or "").strip()
    if configured:
        return configured
    # 4. Fallback to host root (e.g. http://localhost:8003) matching GCP Console
    if request:
        return str(request.base_url).rstrip("/")
    return "http://localhost:8003"


@app.get("/api/auth/status")
async def get_auth_status(request: Request, response: Response):
    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, session = await resolve_credentials(session_id)

    fingerprint = f"{token[:8]}...{token[-4:]}" if token and len(token) > 12 else "None"
    callback_url = get_effective_redirect_uri(request)

    client_id = oauth_config.get("client_id", "")
    client_id_preview = f"{client_id[:12]}...apps.googleusercontent.com" if client_id and len(client_id) > 20 else ("Configured" if client_id else "Not Set")

    user_info = session.get("user_info") if session else None
    granted_scopes = session.get("scopes", []) if session else []

    return {
        "framework": "LangChain",
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
async def oauth_login(
    request: Request,
    response: Response,
    redirect_uri: Optional[str] = Query(None, description="Optional override redirect URI"),
):
    session_id = get_or_create_session_id(request, response)
    client_id = oauth_config.get("client_id")

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="OAuth Client ID not configured. Please configure it via the Credentials modal.",
        )

    callback_url = get_effective_redirect_uri(request, override_uri=redirect_uri)
    state_value = f"lc_{session_id}" if "8002" in callback_url else session_id
    oauth_pending_states[session_id] = {
        "redirect_uri": callback_url,
        "timestamp": time.time(),
    }
    oauth_pending_states[state_value] = oauth_pending_states[session_id]

    params = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "response_type": "code",
        "scope": " ".join(WORKSPACE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state_value,
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
    if error:
        logger.warning(f"OAuth callback error: {error}")
        return RedirectResponse(url=f"/?auth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    session_id = state or get_or_create_session_id(request, response)
    clean_session_id = session_id[3:] if session_id.startswith("lc_") else session_id
    pending = oauth_pending_states.pop(session_id, None) or oauth_pending_states.pop(clean_session_id, None) or {}
    callback_url = pending.get("redirect_uri") or ("http://localhost:8002" if (state and "lc_" in state) else get_effective_redirect_uri(request))

    client_id = oauth_config.get("client_id")
    client_secret = oauth_config.get("client_secret")

    if not (client_id and client_secret):
        raise HTTPException(status_code=500, detail="OAuth credentials missing.")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
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

            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_profile = userinfo_resp.json() if userinfo_resp.status_code == 200 else {}

            user_sessions[clean_session_id] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": time.time() + expires_in,
                "user_info": {
                    "email": user_profile.get("email", "unknown"),
                    "name": user_profile.get("name", "User"),
                    "picture": user_profile.get("picture", ""),
                    "hd": user_profile.get("hd", ""),
                },
                "scopes": raw_scopes,
                "created_at": time.time(),
            }

            res = RedirectResponse(url="/?auth=success")
            res.set_cookie(
                key="mcp_session_id_langchain",
                value=clean_session_id,
                httponly=True,
                samesite="lax",
                max_age=30 * 86400,
            )
            return res
    except Exception as e:
        return RedirectResponse(url=f"/?auth_error={str(e)}")


@app.post("/api/auth/config")
async def update_oauth_config(req: ConfigUpdateRequest):
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
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        cred = data.get("web") or data.get("installed")
        if not cred:
            raise HTTPException(status_code=400, detail="Invalid client_secret.json format.")

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
    session_id = request.cookies.get("mcp_session_id_langchain")
    if session_id and session_id in user_sessions:
        del user_sessions[session_id]
    response.delete_cookie("mcp_session_id_langchain")
    return {"message": "Logged out successfully."}


@app.get("/api/mcp/tools")
async def list_mcp_tools(request: Request, response: Response, service: str = Query("gmail")):
    if service not in WORKSPACE_ENDPOINTS:
        raise HTTPException(status_code=400, detail=f"Unsupported service: {service}")

    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, _ = await resolve_credentials(session_id)

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    endpoint_url = WORKSPACE_ENDPOINTS[service]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=12.0) as client:
            await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "langchain-workspace-ui", "version": "2.0"}},
                },
            )
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


ALLOWED_SCHEMA_FIELDS = {
    "type", "description", "properties", "required", "items",
    "enum", "default", "nullable", "title", "example", "pattern"
}


def clean_json_schema(raw_schema):
    """Sanitizes JSON schema from MCP tools for Gemini FunctionDeclaration:
    dereferences $ref from $defs, removes non-standard fields, and enforces Gemini spec."""
    if not isinstance(raw_schema, dict):
        return raw_schema

    schema = copy.deepcopy(raw_schema)
    defs = schema.pop("$defs", {})
    if not defs and "definitions" in schema:
        defs = schema.pop("definitions", {})

    def resolve(node, depth=0):
        if depth > 8:
            return {"type": "string"}
        if not isinstance(node, dict):
            return node

        if "$ref" in node:
            ref_path = node["$ref"]
            ref_name = ref_path.split("/")[-1]
            if ref_name in defs:
                return resolve(copy.deepcopy(defs[ref_name]), depth + 1)
            else:
                return {"type": "string"}

        cleaned = {}
        for k, v in node.items():
            if k == "properties" and isinstance(v, dict):
                cleaned["properties"] = {
                    prop_k: resolve(prop_v, depth + 1)
                    for prop_k, prop_v in v.items()
                }
            elif k in ALLOWED_SCHEMA_FIELDS:
                if isinstance(v, dict):
                    cleaned[k] = resolve(v, depth + 1)
                elif isinstance(v, list):
                    cleaned[k] = [resolve(i, depth + 1) if isinstance(i, dict) else i for i in v]
                else:
                    cleaned[k] = v
        return cleaned

    return resolve(schema)


async def execute_mcp_tool_call(endpoint_url: str, headers: dict, tool_name: str, tool_args: dict) -> dict:
    """Executes an MCP tool call over Streamable HTTP."""
    call_id = int(time.time() * 1000) % 100000
    call_payload = {
        "jsonrpc": "2.0",
        "id": call_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": tool_args or {},
        },
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            res = await client.post(endpoint_url, json=call_payload)
            if res.status_code == 200:
                body = res.json()
                if "error" in body:
                    return {"error": body["error"]}
                return body.get("result", {})
            else:
                return {"error": f"HTTP {res.status_code}: {res.text}"}
    except Exception as exc:
        return {"error": str(exc)}


class WorkspaceAgentState(TypedDict):
    """LangGraph agent state containing message history and thought telemetry."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    thought_chunks: Annotated[List[str], operator.add]


def create_workspace_langchain_tool(
    tool_def: Dict[str, Any],
    endpoint_url: str,
    headers: dict,
    auth_type: str,
) -> StructuredTool:
    """Wraps a Google Workspace Remote MCP tool as an authentic LangChain StructuredTool."""
    tool_name = tool_def["name"]
    desc = tool_def.get("description", "") or f"Executes {tool_name} via Google Workspace Remote MCP"

    async def _async_exec(**kwargs):
        if auth_type == "adc":
            return {
                "status": "AUTH_REQUIRED",
                "error": "Google Workspace OAuth Required",
                "message": (
                    f"Tool '{tool_name}' was intercepted: ADC token lacks Google Workspace user scopes. "
                    "The user must click 'Sign in with Google' to authenticate."
                ),
            }
        return await execute_mcp_tool_call(endpoint_url, headers, tool_name, kwargs)

    return StructuredTool.from_function(
        coroutine=_async_exec,
        func=lambda **kw: asyncio.run(_async_exec(**kw)),
        name=tool_name,
        description=desc,
    )


def build_workspace_agent_graph(
    tools_by_name: Dict[str, StructuredTool],
    function_declarations: List[types.FunctionDeclaration],
    genai_client: genai.Client,
    system_instruction: str,
):
    """Compiles a LangGraph StateGraph ReAct agent that coordinates reasoning with Gemini 3.7 Flash
    and tool execution via LangChain StructuredTools calling Google Workspace Remote MCP."""
    tool_config = types.Tool(function_declarations=function_declarations) if function_declarations else None
    tools_list = [tool_config] if tool_config else []
    config = types.GenerateContentConfig(
        temperature=0.2,
        system_instruction=system_instruction,
        tools=tools_list,
    )

    async def agent_node(state: WorkspaceAgentState) -> Dict[str, Any]:
        contents: List[types.Content] = []
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg.content)]))
            elif isinstance(msg, AIMessage):
                parts: List[types.Part] = []
                if msg.content:
                    parts.append(types.Part.from_text(text=msg.content))
                if getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        parts.append(types.Part.from_function_call(name=tc["name"], args=tc["args"]))
                contents.append(types.Content(role="model", parts=parts))
            elif isinstance(msg, ToolMessage):
                try:
                    tool_res_val = json.loads(msg.content)
                except Exception:
                    tool_res_val = msg.content
                contents.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=msg.name,
                                response={"result": tool_res_val},
                            )
                        ],
                    )
                )

        response_gen = await asyncio.to_thread(
            genai_client.models.generate_content,
            model="gemini-3.7-flash",
            contents=contents,
            config=config,
        )

        thoughts = []
        candidate = response_gen.candidates[0] if response_gen.candidates else None
        if candidate and candidate.content and candidate.content.parts:
            for p in candidate.content.parts:
                th = getattr(p, "thought", None)
                if th and isinstance(th, str) and th.strip():
                    thoughts.append(th.strip())

        text_content = ""
        if candidate and candidate.content and candidate.content.parts:
            text_parts = [p.text for p in candidate.content.parts if p.text]
            text_content = "".join(text_parts).strip()

        tool_calls = []
        if response_gen.function_calls:
            for idx, fc in enumerate(response_gen.function_calls):
                tool_calls.append({
                    "name": fc.name,
                    "args": dict(fc.args or {}),
                    "id": f"call_{fc.name}_{idx}_{int(time.time()*1000)}"
                })

        return {
            "messages": [AIMessage(content=text_content, tool_calls=tool_calls)],
            "thought_chunks": thoughts,
        }

    async def tool_node(state: WorkspaceAgentState) -> Dict[str, Any]:
        last_msg = state["messages"][-1]
        tool_messages: List[ToolMessage] = []
        if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
            for tc in last_msg.tool_calls:
                t_name = tc["name"]
                t_args = tc["args"]
                tool_instance = tools_by_name.get(t_name)
                if tool_instance:
                    res = await tool_instance.ainvoke(t_args)
                else:
                    res = {"error": f"Tool '{t_name}' not found"}
                tool_messages.append(
                    ToolMessage(
                        content=json.dumps(res) if isinstance(res, (dict, list)) else str(res),
                        name=t_name,
                        tool_call_id=tc["id"],
                    )
                )
        return {"messages": tool_messages, "thought_chunks": []}

    def should_continue(state: WorkspaceAgentState) -> str:
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
            return "tools"
        return END

    workflow = StateGraph(WorkspaceAgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


@app.post("/api/chat")
async def chat_with_agent(request: Request, response: Response, req: ChatRequest):
    session_id = get_or_create_session_id(request, response)
    token, project_id, identity, auth_type, _ = await resolve_credentials(session_id)

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in with your Google account.")

    service = req.service if req.service in WORKSPACE_ENDPOINTS else "gmail"
    endpoint_url = WORKSPACE_ENDPOINTS[service]

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

    accept_header = request.headers.get("accept", "")
    wants_stream = True
    if req.stream is False:
        wants_stream = False
    elif req.stream is None:
        if "application/json" in accept_header and "text/event-stream" not in accept_header:
            wants_stream = False

    async def event_generator():
        start_time = time.time()
        yield f"data: {json.dumps({'type': 'start', 'service': service, 'model': 'gemini-3.7-flash', 'auth_type': auth_type, 'project_id': project_id})}\n\n"
        await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'type': 'status', 'phase': 'connecting', 'text': f'Connecting to {service.upper()} Remote MCP ({endpoint_url})...'})}\n\n"

        try:
            # Step 1: Discover available tools from Workspace Remote MCP Server
            async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
                await client.post(
                    endpoint_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "langchain-agent", "version": "2.0"}},
                    },
                )
                res = await client.post(endpoint_url, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
                mcp_tools = res.json().get("result", {}).get("tools", [])

            yield f"data: {json.dumps({'type': 'status', 'phase': 'handshake', 'text': f'Discovered {len(mcp_tools)} tools from {service.upper()} Remote MCP.'})}\n\n"

            # Step 2: Configure Gemini Function Calling with MCP tools
            yield f"data: {json.dumps({'type': 'status', 'phase': 'reasoning', 'text': 'LangChain reasoning with gemini-3.7-flash...'})}\n\n"

            genai_client = genai.Client(
                vertexai=True,
                project=project_id,
                location="global",
            )

            function_declarations = []
            for t in mcp_tools:
                t_name = t.get("name")
                if not t_name:
                    continue
                raw_schema = t.get("inputSchema", {}) or {"type": "object", "properties": {}}
                cleaned = clean_json_schema(raw_schema)
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=t_name,
                        description=t.get("description", "") or f"Executes {t_name}",
                        parameters=cleaned,
                    )
                )

            tool_config = types.Tool(function_declarations=function_declarations) if function_declarations else None
            tools_list = [tool_config] if tool_config else []

            system_instruction = (
                f"You are an enterprise AI assistant integrated with Google Workspace ({service.upper()}) "
                f"via Model Context Protocol. You are operating on behalf of authenticated user '{identity}' "
                f"in Google Cloud project '{project_id}'.\n"
                f"You have direct access to live {service.upper()} tools via MCP.\n"
                f"CRITICAL INSTRUCTIONS:\n"
                f"1. When the user asks to read, find, list, search, compose, or manage emails, calendar events, documents, or drive files, "
                f"YOU MUST INVOKE the corresponding MCP tool(s) to fetch or process real data.\n"
                f"2. Never just describe what tools to run or output a manual step-by-step plan when you have tools available. "
                f"Always execute the tool call directly.\n"
                f"3. After receiving tool results, provide a clear, accurate, and concise answer directly answering the user's question."
            )

            # Step 2: Convert discovered MCP tools into LangChain StructuredTool instances
            langchain_tools = [
                create_workspace_langchain_tool(t, endpoint_url, headers, auth_type)
                for t in mcp_tools
            ]
            tools_by_name = {t.name: t for t in langchain_tools}

            # Step 3: Build and compile the LangGraph ReAct agent workflow
            agent_graph = build_workspace_agent_graph(
                tools_by_name=tools_by_name,
                function_declarations=function_declarations,
                genai_client=genai_client,
                system_instruction=system_instruction,
            )

            yield f"data: {json.dumps({'type': 'status', 'phase': 'reasoning', 'text': 'LangGraph agent coordinating reasoning with gemini-3.7-flash...'})}\n\n"

            initial_state: WorkspaceAgentState = {
                "messages": [HumanMessage(content=req.message)],
                "thought_chunks": [],
            }

            final_reply = ""
            tool_activity = []

            async for event in agent_graph.astream(initial_state, stream_mode="updates"):
                for node_name, updates in event.items():
                    if node_name == "agent":
                        for th in updates.get("thought_chunks", []):
                            yield f"data: {json.dumps({'type': 'thought', 'text': th})}\n\n"

                        for msg in updates.get("messages", []):
                            if isinstance(msg, AIMessage):
                                if msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        c_name = tc["name"]
                                        c_args = tc["args"]
                                        args_preview = ", ".join(f"{k}={repr(v)[:20]}" for k, v in list(c_args.items())[:2])
                                        yield f"data: {json.dumps({'type': 'tool_call', 'name': c_name, 'args': c_args, 'text': f'LangGraph invoking tool: {c_name}({args_preview})'})}\n\n"
                                        tool_activity.append({"type": "call", "name": c_name, "args": c_args})
                                if msg.content:
                                    final_reply = msg.content
                    elif node_name == "tools":
                        for msg in updates.get("messages", []):
                            if isinstance(msg, ToolMessage):
                                yield f"data: {json.dumps({'type': 'tool_response', 'name': msg.name, 'text': f'LangGraph received result from {msg.name}'})}\n\n"
                                tool_activity.append({"type": "response", "name": msg.name, "response": msg.content[:500]})

            if auth_type == "adc" and not any(t.get("type") == "call" for t in tool_activity):
                scope_notice = (
                    f"\n\n> ℹ️ **Google Workspace Scope Notice**: The active ADC token has Google Cloud Platform scope (`cloud-platform`), but lacks the end-user OAuth scope required for {service.title()}.\n"
                    f"> - **Option A (Web)**: Click **'Sign in with Google'** at the top right to grant Workspace scopes.\n"
                    f"> - **Option B (Terminal)**: Re-login ADC with Workspace scopes:\n"
                    f">   ```bash\n"
                    f">   gcloud auth application-default login --scopes=\"https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/documents.readonly,https://www.googleapis.com/auth/spreadsheets.readonly\"\n"
                    f">   ```"
                )
                final_reply += scope_notice

            if not final_reply:
                final_reply = f"I processed your request using the LangGraph {service.title()} MCP integration."

            yield f"data: {json.dumps({'type': 'chunk', 'text': final_reply})}\n\n"

            elapsed = round(time.time() - start_time, 2)
            yield f"data: {json.dumps({'type': 'done', 'reply': final_reply, 'tool_activity': tool_activity, 'elapsed': elapsed})}\n\n"

        except Exception as e:
            err_msg = str(e)
            logger.error(f"LangChain Chat error: {err_msg}")
            help_msg = ""
            if "403" in err_msg and ("Forbidden" in err_msg or "PERMISSION_DENIED" in err_msg):
                if auth_type == "adc":
                    help_msg = (
                        "ADC Host Token lacks Google Workspace OAuth scopes. "
                        "Click 'Sign in with Google' at top right, or re-authenticate ADC with Workspace scopes."
                    )
                else:
                    help_msg = f"Ensure user has 'roles/mcp.toolUser' in project '{project_id}'."
            elapsed = round(time.time() - start_time, 2)
            yield f"data: {json.dumps({'type': 'error', 'reply': f'Error executing LangGraph agent: {err_msg}', 'help': help_msg, 'elapsed': elapsed})}\n\n"

    if wants_stream:
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming JSON fallback via LangGraph
    start_time = time.time()
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "langchain-agent", "version": "2.0"}},
                },
            )
            res = await client.post(endpoint_url, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            mcp_tools = res.json().get("result", {}).get("tools", [])

        genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location="global",
        )

        function_declarations = []
        for t in mcp_tools:
            t_name = t.get("name")
            if not t_name:
                continue
            raw_schema = t.get("inputSchema", {}) or {"type": "object", "properties": {}}
            cleaned = clean_json_schema(raw_schema)
            function_declarations.append(
                types.FunctionDeclaration(
                    name=t_name,
                    description=t.get("description", "") or f"Executes {t_name}",
                    parameters=cleaned,
                )
            )

        system_instruction = (
            f"You are an enterprise AI assistant integrated with Google Workspace ({service.upper()}) "
            f"via Model Context Protocol. You are operating on behalf of authenticated user '{identity}' "
            f"in Google Cloud project '{project_id}'.\n"
            f"You have direct access to live {service.upper()} tools via MCP.\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. When the user asks to read, find, list, search, compose, or manage emails, calendar events, documents, or drive files, "
            f"YOU MUST INVOKE the corresponding MCP tool(s) to fetch or process real data.\n"
            f"2. Never just describe what tools to run or output a manual step-by-step plan when you have tools available. "
            f"Always execute the tool call directly.\n"
            f"3. After receiving tool results, provide a clear, accurate, and concise answer directly answering the user's question."
        )

        # Convert discovered MCP tools into LangChain StructuredTool instances
        langchain_tools = [
            create_workspace_langchain_tool(t, endpoint_url, headers, auth_type)
            for t in mcp_tools
        ]
        tools_by_name = {t.name: t for t in langchain_tools}

        agent_graph = build_workspace_agent_graph(
            tools_by_name=tools_by_name,
            function_declarations=function_declarations,
            genai_client=genai_client,
            system_instruction=system_instruction,
        )

        initial_state: WorkspaceAgentState = {
            "messages": [HumanMessage(content=req.message)],
            "thought_chunks": [],
        }

        tool_activity = []
        final_reply = ""

        async for event in agent_graph.astream(initial_state, stream_mode="updates"):
            for node_name, updates in event.items():
                if node_name == "agent":
                    for msg in updates.get("messages", []):
                        if isinstance(msg, AIMessage):
                            if msg.tool_calls:
                                for tc in msg.tool_calls:
                                    tool_activity.append({"type": "call", "name": tc["name"], "args": tc["args"]})
                            if msg.content:
                                final_reply = msg.content
                elif node_name == "tools":
                    for msg in updates.get("messages", []):
                        if isinstance(msg, ToolMessage):
                            tool_activity.append({"type": "response", "name": msg.name, "response": msg.content[:500]})

        if not final_reply:
            final_reply = f"I processed your request using the LangGraph {service.title()} MCP integration."

        elapsed = round(time.time() - start_time, 2)
        return JSONResponse({"reply": final_reply, "tool_activity": tool_activity, "elapsed": elapsed, "stream": False})
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        return JSONResponse(status_code=500, content={"reply": f"Error executing LangGraph agent: {str(e)}", "error": str(e), "elapsed": elapsed})


frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_index(
    request: Request,
    response: Response,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    if code or error:
        return await oauth_callback(request, response, code=code, state=state, error=error)

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
    return {"message": "Frontend not found. Please check frontend/index.html"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8003, reload=True)
