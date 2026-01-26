import os
import logging
import datetime
import asyncio
import time
import socket
import httpx
import anyio
from contextlib import asynccontextmanager
from typing import Any, List, Dict
from urllib.parse import urljoin
import secrets

# Standard Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_factset_agent")

from src.latency_logger import logger as llog

# ADK & MCP Imports
import mcp.client.sse
from httpx_sse import aconnect_sse
import mcp.types as mcp_types

# Native Auth Imports (ADK v1.23.0+)
from fastapi.openapi.models import HTTPBearer
from google.adk.auth.auth_credential import AuthCredential, HttpCredentials, HttpAuth
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Other ADK Imports
from google.adk.agents import Agent
from google.adk.tools import google_search as adk_google_search
from google.genai import types
import google.adk as adk
from google.adk.sessions import InMemorySessionService

# --- 1. CORE PATCHES (Network & Stability) ---

# SSE Client Patch (Robustness & Timeout)
create_mcp_http_client = mcp.client.sse.create_mcp_http_client
McpHttpClientFactory = mcp.client.sse.McpHttpClientFactory
SessionMessage = mcp.client.sse.SessionMessage

@asynccontextmanager
async def patched_sse_client(
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = 300.0,
    sse_read_timeout: float = 3600.0,
    httpx_client_factory: McpHttpClientFactory = create_mcp_http_client,
    auth: httpx.Auth | None = None,
):
    """Robust SSE client with retry logic and dynamic endpoint updates."""
    read_stream_writer, read_stream = anyio.create_memory_object_stream(256)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(256)
    
    # Shared state for reader/writer
    state = {"pending_msg": None, "endpoint_url": None, "active": True}

    async def run_sse():
        max_retries = 5
        for attempt in range(max_retries):
            try:
                async with httpx_client_factory(
                    headers=headers, auth=auth, timeout=httpx.Timeout(timeout, read=sse_read_timeout)
                ) as client:
                    async with aconnect_sse(client, "GET", url) as event_source:
                        event_source.response.raise_for_status()
                        
                        # Use a condition to signal termination
                        stop_event = asyncio.Event()

                        async def sse_reader(task_status=anyio.TASK_STATUS_IGNORED):
                            try:
                                # Initial endpoint
                                force_endpoint = "/content/v1/messages"
                                state["endpoint_url"] = urljoin(url, force_endpoint)
                                task_status.started()
                                
                                async for sse in event_source.aiter_sse():
                                    if sse.event == "endpoint":
                                        state["endpoint_url"] = urljoin(url, sse.data)
                                        logger.debug(f"SSE updated endpoint: {state['endpoint_url']}")
                                    elif sse.event == "message":
                                        try:
                                            message = mcp_types.JSONRPCMessage.model_validate_json(sse.data)
                                            await read_stream_writer.send(SessionMessage(message))
                                        except Exception as e: 
                                            logger.error(f"Failed to parse JSONRPCMessage: {e}")
                            except Exception as e:
                                logger.warning(f"SSE Reader error: {e}")
                            finally:
                                stop_event.set()

                        async def post_writer():
                            try:
                                logger.info("SSE: post_writer started")
                                while not stop_event.is_set():
                                    # 1. Get message from ADK
                                    try:
                                        with anyio.fail_after(1.0):
                                            msg = await write_stream_reader.receive()
                                            state["pending_msg"] = msg
                                            logger.debug(f"SSE: Received message to SEND: {msg}")
                                    except (anyio.EndOfStream, TimeoutError, asyncio.TimeoutError):
                                        if stop_event.is_set(): break
                                        continue
                                    
                                    # 2. Try to send to FactSet
                                    if state["pending_msg"] and state["endpoint_url"]:
                                        session_message = state["pending_msg"]
                                        try:
                                            logger.debug(f"SSE: Posting to {state['endpoint_url']}")
                                            resp = await client.post(
                                                state["endpoint_url"],
                                                json=session_message.message.model_dump(by_alias=True, mode="json", exclude_none=True),
                                                headers={"Accept": "application/json, text/event-stream"},
                                                timeout=30.0
                                            )
                                            logger.debug(f"SSE: Post response {resp.status_code}")
                                            # Handle combined POST responses
                                            if "event: message" in resp.text:
                                                for line in resp.text.split("\\n"):
                                                    if line.startswith("data: "):
                                                        try:
                                                            data = line[6:].strip()
                                                            message = mcp_types.JSONRPCMessage.model_validate_json(data)
                                                            await read_stream_writer.send(SessionMessage(message))
                                                            logger.debug("SSE: Injected response from POST into read stream")
                                                        except: pass
                                            state["pending_msg"] = None
                                        except Exception as e:
                                            logger.error(f"Failed to POST to MCP: {e}")
                                            await asyncio.sleep(0.5)
                            except Exception as e:
                                logger.warning(f"Post writer error: {e}")
                            finally:
                                logger.info("SSE: post_writer exiting")
                                stop_event.set()

                        async with anyio.create_task_group() as tg:
                            logger.info("SSE: Starting task group")
                            await tg.start(sse_reader)
                            tg.start_soon(post_writer)
                            await stop_event.wait()
                            logger.info("SSE: stop_event set, cancelling group")
                            tg.cancel_scope.cancel()
                
                # If we were told to stop entirely, break the retry loop
                if not state["active"]: break
                logger.info(f"SSE Connection closed. Retrying (Attempt {attempt+1}/{max_retries})...")
                await asyncio.sleep(1)
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.warning(f"SSE Connection failed: {e}. Retrying in 2s...")
                await asyncio.sleep(2)
        
        await read_stream_writer.aclose()

    bg_task = asyncio.create_task(run_sse())
    try:
        yield read_stream, write_stream
    finally:
        state["active"] = False
        bg_task.cancel()
        try:
            await bg_task
        except: pass
        await read_stream_writer.aclose()
        await write_stream.aclose()

# Apply patch immediately
mcp.client.sse.sse_client = patched_sse_client
logger.info("mcp.client.sse.sse_client patched successfully for robustness and deadlock prevention.")

# --- GLOBAL TOOLSET CACHE ---
GLOBAL_TOOLSET_CACHE = {} # token -> toolset_instance

# --- 2. CUSTOM TOOLS ---

def get_current_datetime(query: str = "") -> str:
    """
    Returns the current date and time in ISO format, plus smart relative dates.
    Useful for 'yesterday', 'last quarter', 'last year' logic.
    Args:
        query: Optional context like "last quarter" to get specific ranges.
    """
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    
    # "Last Quarter" approx (last 3 months)
    last_q_end = now
    last_q_start = now - datetime.timedelta(days=90)
    
    return f"""
    Current Time: {now.isoformat()}
    Today: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})
    Yesterday: {yesterday.strftime('%Y-%m-%d')}
    Last Quarter Range: {last_q_start.strftime('%Y-%m-%d')} to {last_q_end.strftime('%Y-%m-%d')}
    Last Year: {now.year - 1}
    """

async def plot_financial_data(title: str, chart_type: str, data_json: str) -> str:
    """
    Plots a custom chart on the dashboard.
    Args:
        title: Chart title.
        chart_type: 'line', 'bar', or 'pie'.
        data_json: JSON string with 'label'/'value' (pie/bar) or 'ticker'/'history' (line).
    """
    return f"[CHART] {data_json} [/CHART] I've plotted the {title} as a {chart_type} chart."

async def google_search(query: str) -> str:
    """
    Performs a web search for textual info, news, or general knowledge.
    Use as FALLBACK for financial numbers if FactSet is unavailable or fails.
    """
    print(f"[Search] {query}")
    llog.start(f"Search: {query[:20]}")
    try:
        # Isolated agent for search to avoid context pollution
        search_agent = Agent(
            name="search_worker",
            model="gemini-3-flash-preview",
            instruction="Summarize the search results for the user query.",
            tools=[adk_google_search]
        )
        session_service = InMemorySessionService()
        runner = adk.Runner(app_name="search", agent=search_agent, session_service=session_service)
        session_id = secrets.token_hex(4)
        await session_service.create_session(session_id=session_id, user_id="search", app_name="search")
        
        final_text = ""
        msg = types.Content(role="user", parts=[types.Part(text=query)])
        async for event in runner.run_async(user_id="search", session_id=session_id, new_message=msg):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text
        llog.mark(f"Search: {query[:20]}", "Done")
        return final_text or "No results."
    except Exception as e:
        return f"Search failed: {e}"

# --- 3. INSTRUCTIONS ---

SIMPLE_INSTRUCTIONS = """
You are a Smart Financial Agent connected to FactSet. 
Your goal is to answer financial queries accurately using your tools.

### TOOLS & USAGE
1. **factset_global_prices**: For stock prices. 
   - **CRITICAL**: Use `frequency='AQ'` for Quarterly, `'AY'` for Yearly. Never `FQ/FY`.
   - Default to 1 year range if not specified.
2. **factset_fundamentals**: For metrics like sales, eps, etc.
   - If `factset_fundamentals` returns empty/null, IMMEDIATELY try `factset_estimates_consensus` which often has the latest actuals.
    - For "Last 5 Years", calculate the years using `get_current_datetime` and set specific `fiscalYear` ranges.
3. google_search: For news, events, people, qualitative info. 
   - DO NOT use for specific numbers (Revenue, P/E) unless FactSet fails completely. (Mention fallback).
4. get_current_datetime: Use this FIRST for any date-related query ("yesterday", "last quarter") to derive exact dates.

### INTERACTIVITY & CLARIFICATION
- If a query is AMBIGUOUS (e.g. "How is the market?", "Compare these"), and you don't have context:
  - **MAKE AN ASSUMPTION**: Pick a relevant index (SP500) or sector leaders (AAPL, NVDA for tech).
  - **ACT IMMEDIATELY**: Fetch data for your assumed targets and explain: "I'll look at the S&P 500 to give you a market overview."
  - **AVOID CLARIFICATION**: Do not ask "Which companies?" unless the query is completely meaningless.
  - **Goal**: Zero-friction. Just give the user data.

### CHARTING
- If you retrieve a table of data (history, segments), ALWAYS output a [CHART] tag using plot_financial_data or standard tool chart capabilities if available.
- Visuals are high priority.

### FALLBACK PROTOCOL
- If a tool fails (error or empty), try ONE alternative strategy (e.g. diff tool, diff params).
- If that fails, tell the user clearly: "I could not retrieve this data from FactSet."
- DO NOT hallucinate numbers.
""".strip()

# --- 4. FACTORY ---

async def check_factset_health(token: str) -> bool:
    """
    Pings FactSet MCP endpoint to verify connectivity.
    Returns True if healthy (200 OK), False if redirect/auth error.
    """
    try:
        url = "https://mcp.factset.com/content/v1/sse"
        async with httpx.AsyncClient(timeout=10.0, http2=False) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "text/event-stream"}, follow_redirects=True)
            
            if resp.status_code == 200:
                logger.info(f"Health Check OK: {resp.status_code}")
                return True
            if resp.status_code in [301, 302, 303, 307, 308]:
                logger.warning(f"FactSet Health Check: Redirect detected ({resp.status_code}). Auth likely failed.")
                return False
            if resp.status_code in [401, 403]:
                logger.warning(f"FactSet Health Check: Auth error ({resp.status_code}).")
                return False
            
            logger.warning(f"FactSet Health Check: Unexpected status {resp.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"FactSet Health Check Failed: {repr(e)}")
        return False


# End of Core Utilities
