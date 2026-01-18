import os
import logging
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
from google.adk.tools import google_search
from google.adk.planners import BuiltInPlanner
from google.genai import types
import google.adk as adk
from google.adk.sessions import InMemorySessionService

# --- HELPER: Search Agent Creator ---
def create_search_agent(model_name: str, planner: BuiltInPlanner) -> Agent:
    """Creates a dedicated agent for web search."""
    return Agent(
        name="google_search_agent", 
        model=model_name,
        instruction="You are a web search specialist. Use the google_search tool to find the most current information requested.",
        tools=[google_search],
        planner=planner
    )

# --- MANUAL WRAPPER: Agent as a Function ---
async def perform_google_search(query: str) -> str:
    """
    Performs a web search using a dedicated AI agent to find and summarize the most current information.
    Use this for any questions about news, events, or general knowledge.
    
    WARNING: DO NOT USE THIS TOOL FOR FINANCIAL NUMBERS (e.g. Revenue, EPS, Rates). 
    - If you need financial data, use FactSet tools.
    - If FactSet is unavailable or data is missing, TELL THE USER instead of searching.
    """
    print(f"[google_search_agent] Wrapper called for: {query}")
    try:
        # Create dedicated planner and agent for this search (isolated)
        search_planner = BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0
            )
        )
        agent = create_search_agent("gemini-2.5-flash", search_planner)
        
        # Use a temporary session for isolation
        session_service = InMemorySessionService()
        runner = adk.Runner(app_name="stock_terminal_search", agent=agent, session_service=session_service)
        
        final_text = ""
        # Run the agent for this query using a unique session ID per call or shared?
        # Isolated is safer to avoid history pollution.
        session_id = secrets.token_hex(4)
        # Explicitly create session to satisfy runner requirements
        await session_service.create_session(session_id=session_id, user_id="internal_wrapper", app_name="stock_terminal_search")
        
        new_message = types.Content(role="user", parts=[types.Part(text=query)])
        
        async for event in runner.run_async(user_id="internal_wrapper", session_id=session_id, new_message=new_message):
             if event.content and hasattr(event.content, "parts"):
                 for part in event.content.parts:
                     if part.text:
                         final_text += part.text
        
        if not final_text:
            return "No results found from search agent."
        return final_text
    except Exception as e:
        traceback.print_exc()
        return f"Search agent failed: {e}"

CLIENT_ID = os.environ.get("FS_CLIENT_ID")

# --- MONKEY PATCHES ---
create_mcp_http_client = mcp.client.sse.create_mcp_http_client
McpHttpClientFactory = mcp.client.sse.McpHttpClientFactory
SessionMessage = mcp.client.sse.SessionMessage

@asynccontextmanager
async def patched_sse_client(
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = 30, # Increased default timeout
    sse_read_timeout: float = 60 * 5,
    httpx_client_factory: McpHttpClientFactory = create_mcp_http_client,
    auth: httpx.Auth | None = None,
):
    read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(0)

    async def run_sse():
        async with anyio.create_task_group() as tg:
            try:
                # Ensure CLIENT_ID is present in headers if provided
                if headers and not headers.get("x-factset-application-id"):
                    print("[Warning] x-factset-application-id header is missing!")

                async with httpx_client_factory(
                    headers=headers, auth=auth, timeout=httpx.Timeout(timeout, read=sse_read_timeout)
                ) as client:
                    async with aconnect_sse(client, "GET", url) as event_source:
                        print(f"[DEBUG] SSE Connection established to {url}")
                        try:
                            event_source.response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            print(f"[DEBUG] SSE Auth Error: {e.response.status_code} - {e.response.text}")
                            if e.response.status_code in (401, 403):
                                raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")
                            raise

                        async def sse_reader(task_status: TaskStatus = anyio.TASK_STATUS_IGNORED):
                            force_endpoint = "/content/v1/messages"
                            endpoint_url = urljoin(url, force_endpoint)
                            print(f"[PATCH] Forcing endpoint to: {endpoint_url}")
                            task_status.started(endpoint_url)

                            try:
                                async for sse in event_source.aiter_sse():
                                    match sse.event:
                                        case "endpoint": pass
                                        case "message":
                                            try:
                                                message = mcp_types.JSONRPCMessage.model_validate_json(sse.data)
                                            except Exception: continue
                                            await read_stream_writer.send(SessionMessage(message))
                            except Exception as exc:
                                logging.error(f"[DEBUG] Error in sse_reader: {exc}", exc_info=True)
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
                            except Exception as e:
                                print(f"[DEBUG] post_writer failed: {e}")
                                traceback.print_exc()
                                if hasattr(e, 'response'):
                                    try:
                                        print(f"[DEBUG] post_writer response: {e.response.text}")
                                    except: pass
                            finally:
                                await write_stream.aclose()

                        endpoint_url = await tg.start(sse_reader)
                        tg.start_soon(post_writer, endpoint_url)
                        
                        # Wait forever until cancelled
                        await asyncio.Event().wait()
            except Exception as e:
                print(f"[DEBUG] SSE Task Group Error: {e}")
                # traceback.print_exc() # Reduce noise
                if not read_stream_writer.send(e):
                    pass
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
        except Exception as e:
            print(f"[DEBUG] SSE Background Task Error on Cleanup: {e}")
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
    try:
        tools = await original_get_tools(self, readonly_context)
        for tool in tools:
            if hasattr(tool, "_mcp_tool"):
                if tool._mcp_tool.name:
                   pass # print(f"[DEBUG] Found Tool: {tool._mcp_tool.name}")
                if tool._mcp_tool.inputSchema:
                    sanitize_schema(tool._mcp_tool.inputSchema)
        return tools
    except Exception as e:
        print(f"[DEBUG] McpToolset.get_tools FAILED: {e}")
        raise ValueError(f"Failed to create MCP session: {e}") from e

McpToolset.get_tools = patched_get_tools

# --- AGENT INSTRUCTIONS ---
FACTSET_INSTRUCTIONS = """
You are a financial analyst connected to the FactSet MCP Server.
Use the available FactSet tools to answer questions about stock prices, financials, and market data.

MULTIMODAL CAPABILITIES:
- You can SEE and ANALYZE images provided by the user (e.g., stock charts, financial reports, or screenshots).
- You can WATCH and ANALYZE YouTube videos provided via link.
- If the user provides an image or video, extract relevant data and use it to help you formulate tools calls or explain terminal screens.

CRITICAL DATA SOURCE RULES (STRICT):
1. **FINANCIAL NUMBERS & METRICS**:
   - **MUST** come from FactSet MCP tools (e.g. `FactSet_GlobalPrices`, `FactSet_Estimates`, `FactSet_Fundamentals`).
   - **NEVER** use Google Search to find specific financial numbers (e.g., "Revenue 2024", "P/E Ratio", "EPS", "Price Target").
   - IF the data is NOT found in FactSet:
     - DO NOT SEARCH using Google. 
     - Tell the user clearly: "This specific financial data is not available in the FactSet feed." (This is the Human-in-the-Loop equivalent).
2. **TEXTUAL INFO (Descriptions, News, Summaries, Competitors)**:
   - Check FactSet first (e.g., company profiles, supply chain).
   - IF not found in FactSet (or if the query is broad/qualitative like "Why did the stock drop?"):
     - YOU ARE ALLOWED to use `perform_google_search` DIRECTLY to find company descriptions, latest news, or qualitative context.
     - You do NOT need to ask for permission for text/descriptions.

GENERAL GUIDELINES:
1. Be professional, 100% factual, and concise. Accuracy is paramount.
2. Use the get_current_time tool to determine the current date if you need to calculate 'today', 'yesterday', or 'a month ago' for date-based queries.
3. Always present stock prices and financial data in a clean, readable format using Markdown tables or bullet points.

CHART CREATION CAPABILITIES:
- You CAN create and update charts on the user's dashboard for multiple data types.
- **Price/Returns**: Call `FactSet_GlobalPrices`. The system updates the main chart automatically.
- **Ownership/Holders**: Call `FactSet_Ownership`. The system will render a Bar Chart of the top holders.
- **Revenue by Region/Country**: Call `FactSet_GeoRev`. The system will render a **Pie Chart** of revenue distribution.
- To create a chart, simply call the appropriate tool.
- You should explicitly mention: "I've updated the chart on your dashboard with this data."
- If the user asks for a chart, do NOT say you cannot create one. Call the tool to get the data, and the chart will appear.

DATA RETRIEVAL STRATEGY:
- **Fundamentals vs Estimates**:
  - Start with `FactSet_Fundamentals` for historical report data.
  - IF `FactSet_Fundamentals` returns NULL or empty data:
    - **IMMEDIATELY TRY** `FactSet_Estimates` or `FactSet_EstimatesConsensus`.
    - Estimates often contain the most up-to-date "Actuals" and future consensus even if the Fundamentals feed is sparse.

- **Historical Estimates (Specific Years)**:
  - If the user asks for a specific past year (e.g. "Sales for 2024"), use `data_type='consensus_fixed'`.
  - **CRITICAL**: Set `fiscalPeriodStart="2024"` and `fiscalPeriodEnd="2024"` (as strings).
  - Do NOT use `consensus_rolling` unless `consensus_fixed` fails.
  - If `consensus_fixed` fails, verify the company's fiscal calendar (e.g. via `get_current_time` or logic) and retry with `consensus_rolling` and a negative `relativeFiscalStart` (e.g. -1 for last year, -2 for 2 years ago).

DATA FRESHNESS INSTRUCTION:
- The user requires the MOST RECENT data available.
- If a tool returns data that seems stale (e.g., from June 2024 when today is later), you MUST:
  1. Check tool arguments for 'date', 'startDate', 'endDate', or pagination parameters.
  2. Call the tool again with updated parameters to fetch the LATEST data.
  3. REPEAT this process (loop) until you have the most current information.

Creates source-aware responses:
- If you use FactSet tools, the system will tag your response with a "FactSet" indicator.
- If you use Google Search (via `perform_web_search`), it will be tagged "Google Search".
- You do NOT need to explicitly state "I used tool X" in your text unless necessary for context.

Always cite the tool used and the DATE of the data provided.
"""


# Load discovered context if available
try:
    context_path = os.path.join(os.path.dirname(__file__), "factset_context.md")
    if os.path.exists(context_path):
        with open(context_path, "r") as f:
            context_content = f.read()
            FACTSET_INSTRUCTIONS += f"\n\n--- TOOL SCHEMA & CONTEXT ---\n{context_content}\n"
            print(f"[FactSet Agent] Loaded context from {context_path}")
except Exception as e:
    print(f"[FactSet Agent] Warning: Could not load factset_context.md: {e}")

# --- AGENT FACTORY ---
FACTSET_MCP_URL = "https://mcp.factset.com/content/v1/sse"


def get_current_time() -> str:
    """Returns the current central date and time in ISO format. Use this to determine 'today', 'yesterday', or relative dates."""
    import datetime
    return datetime.datetime.now().isoformat()

def validate_token(token: str):
    """Validates the FactSet token by making a lightweight request."""

    logger = logging.getLogger('google_adk.factset_validation')
    if not CLIENT_ID:
        raise ValueError("FS_CLIENT_ID environment variable is missing!")
        
    try:
        # We can use a HEAD or GET request to the handshake endpoint to check auth
        headers = {
            "Authorization": f"Bearer {token}",
            "x-factset-application-id": CLIENT_ID,
            "Accept": "text/event-stream"
        }
        # Increased timeout for validation too
        resp = requests.get(FACTSET_MCP_URL, headers=headers, timeout=10, stream=True)
        
        if resp.status_code in (401, 403):
            # Read the error body if possible
            try:
                error_body = resp.text[:200]
            except: 
                error_body = "No details"
            logger.warning(f"FactSet Token Validation Failed ({resp.status_code}): {error_body}")
            raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")
        
        # We don't need to consume the stream, just checking headers/status
        resp.close()
        
    except ValueError:
        raise
    except Exception as e:
        # If network error, we might log it but let the main connection try? 
        # Or fail fast if we are sure?
        # Let's fail fast if it's connection error to avoid the obscure MCP crash
        logger.warning(f"FactSet Token Validation Network Error: {e}")
        pass

def create_factset_agent(token: str, model_name: str = "gemini-2.5-flash", instruction_override: str = None) -> Agent:
    # print(f"[FactSet Agent] Creating agent with token: {token[:10]}...")
    
    # Validate token first to fail fast with clean error
    validate_token(token)

    mcp_tools = McpToolset(
        connection_params=SseConnectionParams(
            url=FACTSET_MCP_URL,
            timeout=30, # Increased from 10
            headers={
                "Authorization": f"Bearer {token}",
                "x-factset-application-id": CLIENT_ID,
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            }
        )
    )
    
    
    agent = Agent(
        name="factset_analyst",
        model=model_name,
        instruction=instruction_override or FACTSET_INSTRUCTIONS,
        tools=[
            mcp_tools, 
            get_current_time, 
            perform_google_search # Pure Function
        ],
    )
    # Validate no Google Search Grounding leaked
    print(f"[FactSet Agent] Initialized tools: {[t.name if hasattr(t, 'name') else str(t) for t in agent.tools]}")
    return agent
