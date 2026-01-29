import os
import asyncio
import requests
import secrets
import hashlib
import base64
import traceback
import mcp.client.sse
from typing import Any
from contextlib import asynccontextmanager
from urllib.parse import urljoin, urlparse
import anyio
import httpx
from anyio.abc import TaskStatus
from httpx_sse import aconnect_sse
import mcp.types as mcp_types
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# --- MONKEY PATCHES ---
create_mcp_http_client = mcp.client.sse.create_mcp_http_client
McpHttpClientFactory = mcp.client.sse.McpHttpClientFactory
SessionMessage = mcp.client.sse.SessionMessage

@asynccontextmanager
async def patched_sse_client(
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = 5,
    sse_read_timeout: float = 60 * 5,
    httpx_client_factory: McpHttpClientFactory = create_mcp_http_client,
    auth: httpx.Auth | None = None,
):
    read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(0)

    async def run_sse():
        async with anyio.create_task_group() as tg:
            try:
                async with httpx_client_factory(
                    headers=headers, auth=auth, timeout=httpx.Timeout(timeout, read=sse_read_timeout)
                ) as client:
                    async with aconnect_sse(client, "GET", url) as event_source:
                        print(f"[DEBUG] SSE Connection established to {url}")
                        try:
                            event_source.response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            if e.response.status_code in (401, 403):
                                raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")
                            raise

                        async def sse_reader():
                            force_endpoint = "/content/v1/messages"
                            endpoint_url = urljoin(url, force_endpoint)
                            print(f"[PATCH] Forcing endpoint to: {endpoint_url}")
                            
                            try:
                                async for sse in event_source.aiter_sse():
                                    match sse.event:
                                        case "endpoint": pass
                                        case "message":
                                            try:
                                                message = mcp_types.JSONRPCMessage.model_validate_json(sse.data)
                                            except Exception: continue
                                            await read_stream_writer.send(SessionMessage(message))
                                        case _: pass
                            except Exception as exc:
                                print(f"[DEBUG] Error in sse_reader: {exc}")
                                await read_stream_writer.send(exc)
                            finally:
                                await read_stream_writer.aclose()

                        async def post_writer(endpoint_url: str):
                            try:
                                async for session_message in write_stream_reader:
                                    response = await client.post(
                                        endpoint_url,
                                        json=session_message.message.model_dump(by_alias=True, mode="json", exclude_none=True),
                                        headers={"Accept": "application/json, text/event-stream"}
                                    )
                                    response.raise_for_status()
                                    if response.text and "event: message" in response.text:
                                        for line in response.text.splitlines():
                                            if line.startswith("data:"):
                                                try:
                                                    message = mcp_types.JSONRPCMessage.model_validate_json(line[5:].strip())
                                                    await read_stream_writer.send(SessionMessage(message))
                                                except: pass
                            except Exception: pass
                            finally:
                                await write_stream.aclose()

                        endpoint_url = urljoin(url, "/content/v1/messages")
                        tg.start_soon(sse_reader)
                        tg.start_soon(post_writer, endpoint_url)
                        
                        # Wait forever until cancelled
                        await asyncio.Event().wait()
            except Exception as e:
                print(f"[DEBUG] SSE Task Group Error: {e}")
                if not read_stream_writer.extra(anyio.abc.MemoryObjectStream.CLOSED, False):
                    await read_stream_writer.send(e)
            finally:
                await read_stream_writer.aclose()
                await write_stream.aclose()

    # Start the SSE background processing
    bg_task = asyncio.create_task(run_sse())
    try:
        yield read_stream, write_stream
    finally:
        bg_task.cancel()
        try:
            await bg_task
        except asyncio.CancelledError:
            pass
        finally:
            await read_stream_writer.aclose()
            await write_stream.aclose()

import google.adk.tools.mcp_tool.mcp_session_manager
google.adk.tools.mcp_tool.mcp_session_manager.sse_client = patched_sse_client

# Schema Sanitization Patch
original_get_tools = McpToolset.get_tools
def sanitize_schema(schema):
    if not isinstance(schema, dict): return
    if "anyOf" in schema:
        del schema["anyOf"]
        schema["type"] = "string"
    if "oneOf" in schema:
        del schema["oneOf"]
        schema["type"] = "string"
    if "properties" in schema:
        for prop in schema["properties"].values():
            sanitize_schema(prop)

async def patched_get_tools(self, readonly_context=None):
    tools = await original_get_tools(self, readonly_context)
    for tool in tools:
        if hasattr(tool, "_mcp_tool"):
            if tool._mcp_tool.name:
                print(f"[DEBUG] Found Tool: {tool._mcp_tool.name}")
            if tool._mcp_tool.inputSchema:
                sanitize_schema(tool._mcp_tool.inputSchema)
                print(f"[DEBUG] Tool Schema ({tool._mcp_tool.name}): {tool._mcp_tool.inputSchema}")
    return tools

McpToolset.get_tools = patched_get_tools

# --- AGENT INSTRUCTIONS ---
FACTSET_INSTRUCTIONS = """
You are a financial analyst connected to the FactSet MCP Server.
Use the available FactSet tools to answer questions about stock prices, financials, and market data.

MULTIMODAL CAPABILITIES:
- You can SEE and ANALYZE images provided by the user (e.g., stock charts, financial reports, or screenshots).
- You can WATCH and ANALYZE YouTube videos provided via link.
- If the user provides an image or video, extract relevant data and use it to help you formulate tools calls or explain terminal screens.

CRITICAL GUIDELINES:
1. For any questions about financial figures, numbers, or company-specific data that can be retrieved via the FactSet MCP tools, you MUST use those tools. 
2. Do NOT invent or estimate financial information. If you do not have access to the data through your tools, state that clearly.
3. Use your general knowledge ONLY for broad financial concepts, general market history, or banal conversation.
4. Be professional, 100% factual, and concise. Accuracy is paramount.
5. Use the get_current_time tool to determine the current date if you need to calculate 'today', 'yesterday', or 'a month ago' for date-based queries.
6. Always present stock prices and financial data in a clean, readable format using Markdown tables or bullet points.

DATA FRESHNESS INSTRUCTION:
- The user requires the MOST RECENT data available.
- If a tool returns data that seems stale (e.g., from June 2024 when today is later), you MUST:
  1. Check tool arguments for 'date', 'startDate', 'endDate', or pagination parameters.
  2. Call the tool again with updated parameters to fetch the LATEST data.
  3. REPEAT this process (loop) until you have the most current information.

Always cite the tool used and the DATE of the data provided.
"""

# --- AGENT FACTORY ---
CLIENT_ID = os.getenv("FS_CLIENT_ID")
FACTSET_MCP_URL = "https://mcp.factset.com/content/v1/sse"

def get_current_time() -> str:
    """Returns the current central date and time in ISO format. Use this to determine 'today', 'yesterday', or relative dates."""
    import datetime
    return datetime.datetime.now().isoformat()

def create_factset_agent(token: str, model_name: str = "gemini-2.5-flash") -> Agent:
    print(f"[FactSet Agent] Creating agent with token: {token[:10]}...")
    mcp_tools = McpToolset(
        connection_params=SseConnectionParams(
            url=FACTSET_MCP_URL,
            timeout=120,
            headers={
                "Authorization": f"Bearer {token}",
                "x-factset-application-id": CLIENT_ID,
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            }
        )
    )
    
    return Agent(
        name="factset_analyst",
        model=model_name,
        instruction=FACTSET_INSTRUCTIONS,
        tools=[mcp_tools, get_current_time]
    )
