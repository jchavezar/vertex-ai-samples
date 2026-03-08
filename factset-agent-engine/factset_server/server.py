import asyncio
import contextvars
import os
import uuid
import uvicorn
import httpx
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import mcp.client.sse
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
import nest_asyncio

# --- 0. Initialization ---
nest_asyncio.apply()
logging.basicConfig(level=logging.DEBUG) # Set to DEBUG for testing
logger = logging.getLogger("factset-proxy-server")

# --- 1. Multi-Tenancy Token Management ---
user_token_var = contextvars.ContextVar("user_token", default=None)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1].strip()
            user_token_var.set(token)
            logger.debug(f"Middleware: Captured token (prefix: {token[:10]}...)")
        else:
            user_token_var.set(None)
            logger.debug("Middleware: No token captured.")
        return await call_next(request)

# --- 2. FactSet Connector ---

def custom_http_client_factory(headers=None, auth=None, timeout=None, http2=True):
    return httpx.AsyncClient(headers=headers, auth=auth, timeout=timeout, http2=http2, follow_redirects=True)

from contextlib import asynccontextmanager

@asynccontextmanager
async def patched_streamable_client(url, headers=None, timeout=300.0, sse_read_timeout=3600.0, httpx_client_factory=None, auth=None):
    logger.info(f"FactSet Connector: Connecting to {url}...")
    try:
        async with streamablehttp_client(
            url=url, headers=headers, timeout=timeout, sse_read_timeout=sse_read_timeout,
            httpx_client_factory=custom_http_client_factory, auth=auth, terminate_on_close=True
        ) as (read_stream, write_stream, get_session_id):
            logger.info(f"FactSet Connector: Connected! Session ID: {get_session_id()}")
            yield read_stream, write_stream
    except Exception as e:
        logger.error(f"FactSet Connector Error: {e}")
        raise e

# --- 3. MCP Proxy Server ---

app = FastAPI(title="FactSet Proxy MCP")
app.add_middleware(AuthMiddleware)
mcp_server = Server("factset-proxy")
sessions = {}

# Enhanced Schema Cache
def load_enhanced_schemas():
    schema_path = "factset_tools_schema.json"
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            return {s['name']: s for s in json.load(f)}
    return {}

ENHANCED_SCHEMAS = load_enhanced_schemas()

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    token = user_token_var.get()
    
    # Return static enhanced list for discovery if no token yet
    # This prevents blocking the Agent Engine during initialization
    tools = []
    for name, schema in ENHANCED_SCHEMAS.items():
        tools.append(Tool(
            name=name,
            description=schema.get("description", ""),
            inputSchema=schema.get("inputSchema", {"type": "object"})
        ))
    
    if tools:
        return tools
        
    return [Tool(name="FactSet_GlobalPrices", description="Get prices", inputSchema={"type": "object"})]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    token = user_token_var.get()
    if not token:
        logger.error("CallTool: Denied - No token in context.")
        return [TextContent(type="text", text="Error: FactSet Authentication Required. Please login via the UI.")]

    url = "https://mcp.factset.com/content/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "x-custom-auth": token,
        "Accept": "text/event-stream"
    }
    
    try:
        async with patched_streamable_client(url, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                logger.info(f"CallTool: Proxying {name} with args {arguments}")
                result = await session.call_tool(name, arguments)
                return result.content
    except Exception as e:
        logger.error(f"CallTool: Proxy Error for {name}: {e}")
        return [TextContent(type="text", text=f"FactSet Proxy Error: {str(e)}")]

# --- 4. SSE Endpoints ---
from starlette.responses import Response as StarletteResponse

class ASGIResponse(StarletteResponse):
    def __init__(self, app):
        self.app = app
        self.background = None
        self.body = b""
        self.status_code = 200
    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

@app.get("/sse")
async def handle_sse(request: Request):
    session_id = str(uuid.uuid4())
    logger.info(f"New SSE Session: {session_id}")
    transport = SseServerTransport(f"/messages/{session_id}")
    sessions[session_id] = transport
    async def sse_handler(scope, receive, send):
        async with transport.connect_sse(scope, receive, send) as (read, write):
            await mcp_server.run(read, write, mcp_server.create_initialization_options())
    return ASGIResponse(sse_handler)

@app.post("/messages/{session_id}")
async def handle_messages(request: Request, session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session expired")
    return ASGIResponse(sessions[session_id].handle_post_message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
