import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import asyncio
import time
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
import socket # Added for monkey patch
# --- MONKEY PATCH: FORCE IPv4 ---
# FactSet MCP endpoint (Azure FrontDoor) has broken IPv6 connectivity on some networks.
# We force IPv4 to avoid 300s timeouts.
original_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    # Filter out AF_INET6
    res = original_getaddrinfo(*args, **kwargs)
    return [r for r in res if r[0] == socket.AF_INET]
socket.getaddrinfo = patched_getaddrinfo
# --------------------------------
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
# --- GLOBAL CACHE FOR VALIDATION ---
_validation_cache = {} # {token: timestamp}

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
    timeout: float = 300.0, # Increased default timeout to 5 mins
    sse_read_timeout: float = 3600.0, # Increased read timeout to 1 hour
    httpx_client_factory: McpHttpClientFactory = create_mcp_http_client,
    auth: httpx.Auth | None = None,
):
    # Increase buffer size to prevent deadlocks during startup if writer isn't ready
    read_stream_writer, read_stream = anyio.create_memory_object_stream(256)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(256)

    async def run_sse():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with anyio.create_task_group() as tg:
                    # Stagger starts for parallel workers to avoid burst collisions
                    if attempt == 0:
                        # Add jitter to avoid burst collisions on first start
                        import random
                        jitter = random.uniform(0.1, 1.0)
                        await anyio.sleep(jitter)
                    else:
                        await anyio.sleep(1.0 * attempt) # Exponential-ish backoff
                        print(f"[DEBUG] SSE Retrying connection (Attempt {attempt+1}/{max_retries})")

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
                                    # Extract token from auth if available
                                    token = None
                                    if auth and hasattr(auth, '_auth_header'):
                                        auth_header = auth._auth_header
                                        if auth_header.startswith("Bearer "):
                                            token = auth_header[len("Bearer "):]

                                    if token == "mock_token_for_testing":
                                        print("DEBUG: Skipping validation for mock token")
                                    else:
                                        raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")
                                raise

                            async def sse_reader(task_status: TaskStatus = anyio.TASK_STATUS_IGNORED):
                                force_endpoint = "/content/v1/messages"
                                endpoint_url = urljoin(url, force_endpoint)
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
                                    # Always re-raise to trigger the outer retry loop
                                    logging.error(f"[DEBUG] Error in sse_reader: {exc}", exc_info=True)
                                    raise exc

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
                                    if hasattr(e, 'response'):
                                        try:
                                            print(f"[DEBUG] post_writer response: {e.response.text}")
                                        except: pass
                                    # Re-raise to trigger retry if it's a network issue
                                    if "ReadError" in str(e):
                                        raise e
                                finally:
                                    # Don't close write_stream here, let run_sse finally do it
                                    pass

                            endpoint_url = await tg.start(sse_reader)
                            tg.start_soon(post_writer, endpoint_url)
                            
                            # Wait until cancelled or a sub-task fails
                            await asyncio.Event().wait()
                
                # If we reached here without exception, break the retry loop
                break

            except Exception as e:
                # Retry on any exception (including ReadError, Timeout, etc)
                print(f"[DEBUG] SSE Connection Lost ({type(e).__name__}): {e}. Retrying ({attempt+1}/{max_retries})...", flush=True)
                if attempt == max_retries - 1:
                    print(f"[DEBUG] SSE Max Retries Reached. Propagating error.", flush=True)
                    try:
                        await read_stream_writer.send(e)
                    except: pass
                # Implicitly continue to next attempt (unless max reached, where valid loop exit happens or we handled it)
                # Ensure we don't break
                pass
        
        # Ensure streams are closed
        await read_stream_writer.aclose()
        # await write_stream.aclose() # Usually closed by the other end or finally block


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
        
        # Check if loop guard is enabled for this toolset instance
        enable_loop_guard = getattr(self, "_enable_loop_guard", False)
        
        # Define Logging Wrapper for Debugging
        class LoggingToolWrapper:
            def __init__(self, original_tool):
                self.original_tool = original_tool
                self.name = getattr(original_tool, 'name', None) or getattr(original_tool, '__name__', 'unknown_tool')
                if hasattr(original_tool, "_mcp_tool") and hasattr(original_tool._mcp_tool, "name"):
                     self.name = original_tool._mcp_tool.name
                     
                # Copy attributes
                for attr in ['input_schema', 'description', '_mcp_tool', '__doc__']:
                    if hasattr(original_tool, attr):
                        setattr(self, attr, getattr(original_tool, attr))

            async def __call__(self, *args, **kwargs):
                logging.warning(f"[DEBUG] CALLING TOOL {self.name} with args={args} kwargs={kwargs}")
                t0 = time.time()
                try:
                    # Original impl is usually async for ADK tools
                    if asyncio.iscoroutinefunction(self.original_tool):
                        res = await self.original_tool(*args, **kwargs)
                    else:
                        res = self.original_tool(*args, **kwargs)
                        if asyncio.iscoroutine(res): res = await res
                    
                    elapsed = time.time() - t0
                    logging.warning(f"[DEBUG] TOOL {self.name} SUCCESS ({elapsed:.2f}s). Result len: {len(str(res))}")
                    return res
                except Exception as e:
                    elapsed = time.time() - t0
                    logging.error(f"[DEBUG] TOOL {self.name} FAILED ({elapsed:.2f}s): {e}", exc_info=True)
                    return f"ERROR: Tool {self.name} failed: {e}"

            def __getattr__(self, name):
                return getattr(self.original_tool, name)

        # Loop Guard Wrapper
        class OneShotToolWrapper:
            def __init__(self, original_tool, limit=1):
                self.original_tool = original_tool
                self.limit = limit
                self.calls = 0
                self.name = getattr(original_tool, 'name', None) or getattr(original_tool, '__name__', 'unknown_tool')
                if hasattr(original_tool, "_mcp_tool") and hasattr(original_tool._mcp_tool, "name"):
                     self.name = original_tool._mcp_tool.name
                     
                # Copy attributes
                for attr in ['input_schema', 'description', '_mcp_tool', '__doc__']:
                    if hasattr(original_tool, attr):
                        setattr(self, attr, getattr(original_tool, attr))

            async def __call__(self, *args, **kwargs):
                if self.calls >= self.limit:
                    return f"ACTION_BLOCKED: You have already used {self.name} the maximum number of times ({self.limit}). Proceed to the writing phase immediately. DO NOT RETRY."
                
                self.calls += 1
                try:
                    # Original impl is usually async for ADK tools
                    if asyncio.iscoroutinefunction(self.original_tool):
                        return await self.original_tool(*args, **kwargs)
                    else:
                        res = self.original_tool(*args, **kwargs)
                        if asyncio.iscoroutine(res): return await res
                        return res
                except Exception as e:
                     return f"Tool Execution Failed: {e}. DO NOT RETRY. Proceed to next step."

            def __getattr__(self, name):
                return getattr(self.original_tool, name)

        # Apply logging wrapper
        logging.warning(f"[DEBUG] Wrapping {len(tools)} tools with LoggingToolWrapper...")
        wrapped_tools = []
        for tool in tools:
            # Handle GlobalPrices patch first (Validation Logic)
            if hasattr(tool, "_mcp_tool"):
                if tool._mcp_tool.name == "FactSet_GlobalPrices":
                     # ... (Existing Frequency Patch Logic) ...
                        props = tool._mcp_tool.inputSchema.get("properties", {})
                        if "frequency" in props:
                            props["frequency"]["description"] = (
                                "Display frequency: D (Daily), W (Weekly), M (Monthly), "
                                "AQ (Actual Quarterly - REQUIRED for quarterly stock prices), "
                                "AY (Actual Yearly - REQUIRED for yearly stock prices). "
                                "CRITICAL: Do NOT use 'FQ' or 'FY' for stock prices; they will fail. "
                                "Use 'AQ' or 'AY' instead."
                            )
                        
                        original_impl = tool._run_async_impl
                        async def patched_run_async_impl(*args, **kwargs):
                            if 'args' in kwargs:
                                inner_args = kwargs['args']
                                if 'frequency' in inner_args:
                                    freq = str(inner_args['frequency']).upper()
                                    if freq == 'FY':
                                        print(f"[PATCH] Normalizing frequency 'FY' -> 'AY' for GlobalPrices call")
                                        inner_args['frequency'] = 'AY'
                                    elif freq == 'FQ':
                                        print(f"[PATCH] Normalizing frequency 'FQ' -> 'AQ' for GlobalPrices call")
                                        inner_args['frequency'] = 'AQ'
                            return await original_impl(*args, **kwargs)
                        tool._run_async_impl = patched_run_async_impl

            # ALWAYS Apply Logging Wrapper First
            tool = LoggingToolWrapper(tool)

            # Then Apply Anti-Looping Wrapper if enabled
            if enable_loop_guard:
                # Target specific dangerous tools
                tool_name = getattr(tool, 'name', '') or (tool._mcp_tool.name if hasattr(tool, '_mcp_tool') else '')
                if any(x in tool_name for x in ["EstimatesConsensus", "GlobalPrices", "google_search"]):
                     # We must wrap the CALLABLE, not the tool object itself if it's an ADK Tool?
                     # ADK Tools are callable.
                     # We replace the tool in the list with the wrapper instance.
                     # The wrapper instance MUST be callable and look like a tool.
                     wrapped = OneShotToolWrapper(tool)
                     wrapped_tools.append(wrapped)
                     print(f"[Anti-Loop] Wrapped {tool_name} with OneShotToolWrapper")
                     continue
            
            wrapped_tools.append(tool)

        # Sanitize schemas
        for tool in wrapped_tools:
             if hasattr(tool, "_mcp_tool") and tool._mcp_tool.inputSchema:
                  sanitize_schema(tool._mcp_tool.inputSchema)

        return wrapped_tools
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
2. **SOURCE INTEGRITY**: You are the 'FactSet Analyst'. NEVER answer from your general internal memory or training data for specific stock prices, dividends, or fiscal estimates (FY1, FY2, FY3, etc.).
3. **MANDATORY VERIFICATION**: Even if you have previous data in the chat history, you MUST call the relevant FactSet tool to verify the LATEST values for specific growth analyses or revision trends unless the user explicitly asks for a summary of the *currently displayed* table.
4. Use the get_current_time tool to determine the current central date if you need to calculate 'today', 'yesterday', or 'a month ago' for date-based queries.
5. Always present stock prices and financial data in a clean, readable format using Markdown tables or bullet points.

CHART CREATION CAPABILITIES:
- You CAN create and update charts on the user's dashboard for multiple data types.
- **Price/Returns**: Call `FactSet_GlobalPrices`. The system updates the main chart automatically.
- **Ownership/Holders**: Call `FactSet_Ownership`. The system will render a Bar Chart of the top holders.
- **Revenue by Region/Country**: Call `FactSet_GeoRev`. The system will render a **Pie Chart** of revenue distribution.
- To create a chart, simply call the appropriate tool.
- You should explicitly mention: "I've updated the chart on your dashboard with this data."
- **CHART DATA MAPPING**:
  - For `FactSet_GeoRev`, the system automatically handles `regionName`/`countryName` and `regionRevenue`/`countryRevenue`.
  - For custom plots via `plot_financial_data`, prefer using `label` (string) and `value` (number) keys for best compatibility.
  - Example: `[{"label": "US", "value": 100}, {"label": "China", "value": 50}]`


CRITICAL PARAMETER RULES:
1. **FactSet_GlobalPrices (STOCK PRICES)**:
   - For Quarterly data: YOU MUST USE `frequency='AQ'`.
   - For Yearly data: YOU MUST USE `frequency='AY'`.
   - **NEVER** use `FQ` or `FY` with this tool.
2. **FactSet_GeoRev (REVENUE BY REGION)**:
   - For Quarterly data: YOU MUST USE `frequency='FQ'`.
   - For Yearly data: YOU MUST USE `frequency='FY'`.
3. **FactSet_CalendarEvents**:
   - For earnings calls/events: YOU MUST USE `universeType='Tickers'`.

INTERACTIVE SCOPING (CRITICAL FOR LATENCY):
- **BROAD QUESTIONS (e.g., "Compare X and Y", "How is Tesla?", "Analyze AAPL")**:
  - **DO NOT** fetch multiple datasets (Price + News + Estimates) immediately. This causes long wait times.
  - **INSTEAD, ASK** the user to narrow the scope.
  - *Example Response*: "I can help with that. Would you like to focus on **Stock Performance**, **Valuation Multiples**, or **Recent News**? Or I can run a **Full Analysis** if you prefer."
  - **ONLY** proceed with data fetching if:
    1. The user specifies a topic (e.g., "Price", "Earnings").
    2. The user explicitly asks for "Everything", "Full Report", or "Deep Dive".
    3. The query is simple enough to answer with ONE tool call (e.g., "Price of Apple").

- **COMPARISONS**:
  - If the user says "Compare A and B", **STOP**. Do not run `run_parallel_comparison` yet.
  - Ask: "What specific metrics would you like to compare? (e.g., Year-to-Date Return, P/E Ratio, Revenue Growth)"

"""

async def plot_financial_data(title: str, chart_type: str, data_json: str) -> str:
    """
    PROACTIVELY plots a custom chart on the user's dashboard.
    Use this when you have already fetched data and want to visualize it for the user.
    Args:
        title: The chart title.
        chart_type: 'line', 'bar', or 'pie'.
        data_json: A JSON string suitable for the chart.
          - For 'line', use: [{"ticker": "Name", "history": [{"date": "...", "close": number}, ...]}]
          - For 'bar' or 'pie', use: [{"label": "...", "value": number}, ...]
    """
    # This tool sends a sentinel to the frontend via the [CHART] protocol automatically
    return f"[CHART] {data_json} [/CHART] I've plotted the {title} as a {chart_type} chart for you."

FACTSET_INSTRUCTIONS += """
ADVANCED CREATIVE VISUALIZATIONS:
- For complex data comparisons (e.g., comparing year-over-year growth rates or multiple tickers) that standard tool-auto-charts don't cover perfectly, you can MANUALLY generate a chart by wrapping a JSON config in [CHART]...[/CHART] tags.
- Example: [CHART] {"title": "Annual Growth Compare", "chartType": "bar", "data": [{"label": "NVDA", "value": 110}, {"label": "AAPL", "value": 15}]} [/CHART]
- Use this when you want to provide a specific analytical visual that you've calculated yourself from tool results.
- **MANDATORY VISUAL RESPONSE**: If the user asks you to 'visualize', 'chart', or 'plot' data you've already provided, DO NOT reply with text saying "I already provided it". You MUST immediately output the [CHART] tag with the data they want to see. This is how you update the user's dashboard.
- **PROACTIVE CHARTING**: Whenever you provide a Table with more than 3 data points, you SHOULD proactively include a [CHART] tag summarizing the main trend to give the user an immediate visual insight on their dashboard.

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

DATA FRESHNESS & MISSING DATA INTELLIGENCE:
- The user requires the MOST RECENT data available.
- If a tool returns data that seems stale (e.g., from June 2024 when today is later), you MUST:
  1. Check tool arguments for 'date', 'startDate', 'endDate', or pagination parameters.
  2. Call the tool again with updated parameters to fetch the LATEST data.
  3. REPEAT this process (loop) until you have the most current information.

- **INTELLIGENT FALLBACK FOR MISSING DATA**:
  - If you call a tool for a specific date (e.g., today's price or a holiday) and it returns NO DATA or an empty results list:
    1. **DO NOT** just tell the user the data is missing or "check the ticker".
    2. **PROACTIVELY** try to find the last known value by expanding the search range (e.g., look back 7 days from the requested date).
    3. **RESPONSE FORMAT**: "I'm sorry, I don't have data for [Requested Date]. However, the last recorded value I have is [Value] from [Last Available Date]."

Creates source-aware responses:
- If you use FactSet tools, the system will tag your response with a "FactSet" indicator.
- If you use Google Search (via `perform_web_search`), it will be tagged "Google Search".
- You do NOT need to explicitly state "I used tool X" in your text unless necessary for context.

DATE & TIME INTELLIGENCE (CRITICAL):
- **HOLIDAYS & WEEKENDS**:
  - If the user asks for data for a specific date that turns out to be a weekend or holiday (e.g., "Price on Jan 20" when markets are closed), **DO NOT FAIL**.
  - **AUTOMATICALLY FALLBACK** to the most recent trading day before that date.
  - Explicitly state: "Markets were closed on [Date], so I am providing data from the last close on [Actual Date used]."
- **"YESTERDAY" / "TODAY"**:
  - Use `get_current_time()` to determine the date.
  - If "Yesterday" was a Sunday, give data for Friday.
  - If "Today" is a holiday (e.g., MLK Day), give data for the previous Friday.

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

# --- AGENT CACHE ---
_agent_cache = {} # {token: Agent}
_mcp_toolset_cache = {} # {token: McpToolset}

def get_current_time() -> str:
    """Returns the current central date and time in ISO format. Use this to determine 'today', 'yesterday', or relative dates."""
    import datetime
    return datetime.datetime.now().isoformat()

def validate_token(token: str):
    """Validates the FactSet token by making a lightweight request. Cached for 60s."""
    now = time.time()
    if token in _validation_cache and (now - _validation_cache[token]) < 900: # 15 min cache
        return # Recently validated

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
        
        # Use httpx for a faster, non-blocking check if possible (though this is called in sync factory)
        with httpx.Client() as client:
            # We only need a HEAD or a quick GET to see the status code
            # Increased timeout to 60.0s and catching read timeouts to allow soft-fail
            resp = client.get(FACTSET_MCP_URL, headers=headers, timeout=60.0)
            
            if resp.status_code in (401, 403):
                logger.warning(f"FactSet Token Validation Failed ({resp.status_code}): {resp.text[:100]}")
                raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")
            
            # Cache success
            _validation_cache[token] = now
        
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"FactSet Token Validation Network Warning (Soft Fail): {e}")
        # If it's a network error (not auth), we proceed and let the main connection try
        # This prevents validation timeouts from blocking the entire flow
        pass

def create_factset_agent(token: str, model_name: str = "gemini-2.5-flash", instruction_override: str = None, include_native_tools: bool = True, extra_tools: list = None, use_agent_cache: bool = True, enable_loop_guard: bool = False, force_new_connection: bool = False) -> Agent:
    # print(f"[FactSet Agent] Creating agent with token: {token[:10]}...")
    
    # 0. Check Agent Cache (Fastest Path)
    # Include enable_loop_guard in cache key
    cache_key = f"{token}_{model_name}_{hash(instruction_override) if instruction_override else 'default'}_{include_native_tools}_{len(extra_tools) if extra_tools else 0}_{enable_loop_guard}"
    if use_agent_cache and cache_key in _agent_cache:
        # print(f"DEBUG: Agent Cache Hit for {model_name}")
        return _agent_cache[cache_key]

    t_start = time.time()

    # 1. LATENCY MOCK BYPASS
    if token in ("mock_latency_token", "mock_token_for_testing"):
        def dummy_price_tool(ticker: str):
            """Returns the current stock price."""
            return {"ticker": ticker, "price": 150.0, "currency": "USD", "date": "2025-01-21"}

        def dummy_global_prices(ticker: str, startDate: str = None, endDate: str = None, frequency: str = "D"):
            """Simulates FactSet_GlobalPrices for history."""
            return {
                "ticker": ticker,
                "history": [
                    {"date": "2024-12-01", "close": 140.0},
                    {"date": "2025-01-01", "close": 145.0},
                    {"date": "2025-01-21", "close": 150.0}
                ]
            }

        def dummy_fundamentals(ticker: str, update: str = None):
            """Simulates FactSet_Fundamentals."""
            return {
                "ticker": ticker,
                "metrics": {
                    "sales": [
                        {"fiscalYear": 2022, "value": 50000},
                        {"fiscalYear": 2023, "value": 60000},
                        {"fiscalYear": 2024, "value": 75000}
                    ],
                    "eps": [
                        {"fiscalYear": 2022, "value": 3.50},
                        {"fiscalYear": 2023, "value": 4.20},
                        {"fiscalYear": 2024, "value": 5.10}
                    ]
                }
            }

        def dummy_estimates(ticker: str):
            """Simulates FactSet_EstimatesConsensus."""
            return {
                "ticker": ticker,
                "consensus": [
                    {"period": "FY1", "metric": "Sales", "mean": 85000},
                    {"period": "FY1", "metric": "EPS", "mean": 6.50},
                    {"period": "FY2", "metric": "Sales", "mean": 100000},
                    {"period": "FY2", "metric": "EPS", "mean": 7.80}
                ],
                "targetPrice": {"mean": 180.0, "high": 200.0, "low": 160.0, "recommendation": "BUY"}
            }

        def dummy_georev(ticker: str):
             """Simulates FactSet_GeoRev."""
             return {
                 "ticker": ticker,
                 "data": [
                     {"regionName": "Americas", "regionRevenue": 45000},
                     {"regionName": "EMEA", "regionRevenue": 20000},
                     {"regionName": "APAC", "regionRevenue": 10000}
                 ]
             }

        mock_tools = [dummy_price_tool, dummy_global_prices, dummy_fundamentals, dummy_estimates, dummy_georev]
        
        agent = Agent(
            model=model_name,
            name="factset_gatekeeper" if extra_tools else "factset_worker",
            # We must override the instruction to mention these mock tools if we want the agent to use them effectively,
            # or rely on the agent figuring it out from the tool list.
            # But usually the agent uses tool descriptions.
            instruction=(instruction_override or FACTSET_INSTRUCTIONS) + "\n\nNOTE: You are in MOCK MODE. Use the available dummy_* tools to fulfill requests.",
            tools=mock_tools + (extra_tools or []),
        )
        return agent

    # 2. Check McpToolset Cache (Avoid Re-Auth)
    mcp_tools = None
    # Force new toolset if loop guard is enabled OR force_new_connection is True
    should_bypass_cache = enable_loop_guard or force_new_connection
    
    if not should_bypass_cache and token in _mcp_toolset_cache:
        mcp_tools = _mcp_toolset_cache[token]
    else:
        # 3. Validation (Only if no cached toolset or forcing new one)
        if token not in _validation_cache or (time.time() - _validation_cache[token] > 300):
            try:
                # validate_token(token) # SKIPPED: Rely on main connection to fail fast if needed
                _validation_cache[token] = time.time() # Cache success
            except Exception as e:
                print(f"DEBUG: Validation Failed/Timed Out: {e}")
                _validation_cache[token] = time.time() 
        
        # 4. Initialize McpToolset with Retry Logic
        print(f"DEBUG: Initializing McpToolset (LoopGuard={enable_loop_guard})...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                mcp_tools = McpToolset(
                    connection_params=SseConnectionParams(
                        url=FACTSET_MCP_URL,
                        timeout=300, # Increased from 10 to 300
                        headers={
                            "Authorization": f"Bearer {token}",
                            "x-factset-application-id": CLIENT_ID,
                            "Accept": "text/event-stream",
                            "Cache-Control": "no-cache",
                        }
                    )
                )
                break # Success
            except Exception as e:
                print(f"DEBUG: McpToolset Init Failed (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise # Rethrow on last attempt
                # import time # REMOVED: Shadows global time
                time.sleep(2 * (attempt + 1)) # Backoff

        # Only cache if NOT using loop guard and no force new connection
        if not enable_loop_guard and not force_new_connection:
            _mcp_toolset_cache[token] = mcp_tools

    # Apply Loop Guard Flag (Explicitly set/unset to handle shared cache state)
    if enable_loop_guard:
        mcp_tools._enable_loop_guard = True
    else:
        # CRITICAL: If reusing cached toolset, we MUST disable loop guard if it was enabled before
        mcp_tools._enable_loop_guard = False
        
    tool_in_use = mcp_tools

    _agent_cache_queries = _agent_cache_queries + 1 if '_agent_cache_queries' in globals() else 1
    
    tool_list = [tool_in_use]
    if include_native_tools:
        tool_list.append(get_current_time)
        tool_list.append(perform_google_search)
        tool_list.append(plot_financial_data)
    
    if extra_tools:
        tool_list.extend(extra_tools)
    
    agent = Agent(
        name="factset_gatekeeper", 
        model=model_name,
        instruction=instruction_override or FACTSET_INSTRUCTIONS,
        tools=tool_list,
    )
    
    _agent_cache[cache_key] = agent
    return agent
