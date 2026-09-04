"""
FastAPI Backend for Google ADK Workspace MCP Showcase
Integrates Google ADK (Agent Development Kit) with Google Workspace remote MCP servers.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import httpx
import google.auth
from google.auth.transport.requests import Request
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk_workspace_mcp")

# Environment Defaults
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

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

app = FastAPI(
    title="Google ADK Workspace MCP Assistant",
    description="Minimalist API and UI connecting Google ADK to Workspace Remote MCP Servers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom token override (if user inputs token via UI)
custom_oauth_token: Optional[str] = None


def get_active_credentials():
    """Retrieves active OAuth credentials and project ID."""
    global custom_oauth_token
    if custom_oauth_token:
        project_id = "vtxdemos"
        return custom_oauth_token, project_id, "Custom Provided Bearer Token"
    
    try:
        creds, project_id = google.auth.default()
        if not creds.valid:
            creds.refresh(Request())
        return creds.token, project_id or "vtxdemos", getattr(creds, "service_account_email", "ADC User")
    except Exception as e:
        logger.error(f"Error resolving ADC: {e}")
        return None, "vtxdemos", "Unauthenticated"


class TokenRequest(BaseModel):
    token: Optional[str] = Field(None, description="Custom OAuth access token or empty to reset to ADC")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt")
    service: str = Field(default="gmail", description="Target Workspace service")


@app.get("/api/auth")
async def get_auth_status():
    token, project_id, identity = get_active_credentials()
    fingerprint = f"{token[:8]}...{token[-4:]}" if token and len(token) > 12 else "Not Set"
    return {
        "authenticated": token is not None,
        "project_id": project_id,
        "identity": identity,
        "token_fingerprint": fingerprint,
        "is_custom_token": custom_oauth_token is not None,
    }


@app.post("/api/auth/token")
async def set_auth_token(req: TokenRequest):
    global custom_oauth_token
    if req.token and req.token.strip():
        custom_oauth_token = req.token.strip()
        msg = "Custom token saved successfully."
    else:
        custom_oauth_token = None
        msg = "Reset to default Application Default Credentials (ADC)."
    
    token, project_id, identity = get_active_credentials()
    fingerprint = f"{token[:8]}...{token[-4:]}" if token and len(token) > 12 else "Not Set"
    return {
        "message": msg,
        "authenticated": token is not None,
        "project_id": project_id,
        "identity": identity,
        "token_fingerprint": fingerprint,
    }


@app.get("/api/mcp/tools")
async def list_mcp_tools(service: str = Query("gmail")):
    if service not in WORKSPACE_ENDPOINTS:
        raise HTTPException(status_code=400, detail=f"Unsupported service: {service}")
    
    token, project_id, _ = get_active_credentials()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. No ADC or token found.")
    
    endpoint_url = WORKSPACE_ENDPOINTS[service]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
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
                        "clientInfo": {"name": "adk-workspace-ui", "version": "1.0"},
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
async def chat_with_agent(req: ChatRequest):
    token, project_id, _ = get_active_credentials()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    service = req.service if req.service in WORKSPACE_ENDPOINTS else "gmail"
    endpoint_url = WORKSPACE_ENDPOINTS[service]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

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

        agent = Agent(
            name="workspace_adk_agent",
            model="gemini-3.7-flash",
            instruction=(
                f"You are a Google Workspace AI assistant connected to {service.upper()} via the Model Context Protocol. "
                "You have access to native Workspace tools. Answer accurately and explain any actions clearly."
            ),
            tools=[workspace_toolset],
        )

        runner = InMemoryRunner(agent=agent)
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="web_user"
        )

        response_chunks = []
        tool_activity = []

        async for event in runner.run_async(
            session_id=session.id,
            user_id="web_user",
            new_message=types.Content(parts=[types.Part.from_text(text=req.message)]),
        ):
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if p.text:
                        response_chunks.append(p.text)
                    if hasattr(p, "function_call") and p.function_call:
                        tool_activity.append({
                            "type": "call",
                            "name": p.function_call.name,
                            "args": dict(p.function_call.args or {}),
                        })
                    if hasattr(p, "function_response") and p.function_response:
                        tool_activity.append({
                            "type": "response",
                            "name": p.function_response.name,
                            "response": str(p.function_response.response),
                        })

        full_reply = "".join(response_chunks).strip()
        if not full_reply:
            full_reply = "I processed your request using the Workspace MCP integration."

        return {
            "reply": full_reply,
            "service": service,
            "tool_activity": tool_activity,
        }
    except Exception as e:
        logger.error(f"Chat execution error: {e}")
        return {
            "reply": f"An error occurred while executing the ADK agent: {str(e)}",
            "service": service,
            "tool_activity": [],
            "error": True,
        }


# Mount Static Files for Minimalist Frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. Please verify frontend/index.html"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
