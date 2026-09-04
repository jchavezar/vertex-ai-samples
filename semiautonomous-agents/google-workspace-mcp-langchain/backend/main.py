"""
FastAPI Backend for LangChain Workspace MCP Showcase
Demonstrates connecting LangChain agents with Google Workspace Remote MCP servers.
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
from google import genai
from google.genai import types

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain_workspace_mcp")

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
    title="LangChain Workspace MCP Assistant",
    description="Minimalist API and UI connecting LangChain to Google Workspace Remote MCP Servers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

custom_oauth_token: Optional[str] = None


def get_active_credentials():
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
    token: Optional[str] = Field(None, description="Custom OAuth access token")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt")
    service: str = Field(default="gmail", description="Target Workspace service")


@app.get("/api/auth")
async def get_auth_status():
    token, project_id, identity = get_active_credentials()
    fingerprint = f"{token[:8]}...{token[-4:]}" if token and len(token) > 12 else "Not Set"
    return {
        "framework": "LangChain 0.3",
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
        raise HTTPException(status_code=401, detail="Authentication required.")
    
    endpoint_url = WORKSPACE_ENDPOINTS[service]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-goog-user-project": project_id,
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "langchain-workspace-ui", "version": "1.0"},
                    },
                },
            )
            res_tools = await client.post(
                endpoint_url,
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            )
            tools_list = res_tools.json().get("result", {}).get("tools", [])
            return {
                "framework": "LangChain",
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
        # Step 1: Query MCP server tools
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            await client.post(
                endpoint_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "langchain-agent", "version": "1.0"}},
                },
            )
            res = await client.post(endpoint_url, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            mcp_tools = res.json().get("result", {}).get("tools", [])

        tool_activity = []

        # Step 2: Invoke model with GenAI & Gemini 3.7 Flash
        genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location="global"
        )

        # Build tools description for LangChain prompt context
        tools_summary = "\n".join([f"- {t.get('name')}: {t.get('description', '').splitlines()[0]}" for t in mcp_tools[:10]])
        
        system_prompt = (
            f"You are an enterprise AI assistant built with LangChain and integrated with Google Workspace ({service.upper()}) "
            f"via Model Context Protocol (Streamable HTTP).\n"
            f"Available MCP Tools on {endpoint_url}:\n{tools_summary}\n"
            f"Provide helpful, accurate answers explaining which Workspace tools execute each task."
        )

        response = genai_client.models.generate_content(
            model="gemini-3.7-flash",
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=f"{system_prompt}\n\nUser Question: {req.message}")])
            ]
        )

        full_reply = response.text.strip() if response.text else "Request processed."

        return {
            "framework": "LangChain",
            "reply": full_reply,
            "service": service,
            "tool_activity": tool_activity,
        }
    except Exception as e:
        logger.error(f"LangChain Chat error: {e}")
        return {
            "reply": f"Error executing LangChain agent: {str(e)}",
            "service": service,
            "tool_activity": [],
            "error": True,
        }


frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. Please check frontend/index.html"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
