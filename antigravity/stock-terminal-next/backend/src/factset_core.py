import os
import logging
import datetime
print("DEBUG: factset_core.py TOP-LEVEL LOADED", flush=True)
import asyncio
import time
import socket
import httpx
import anyio
from contextlib import asynccontextmanager
from typing import Any, List, Dict
from urllib.parse import urljoin
import secrets
import json

# Standard Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_factset_agent")
# logging.getLogger("mcp").setLevel(logging.DEBUG) # Optional

from src.latency_logger import logger as llog

# --- 1. CORE PATCHES (Transport Replacement) ---
# We replace the standard SSE client with StreamableHTTP client (with underscore)
# ensuring we use the HTTP/2 client we configure manually.
import mcp.client.sse
from mcp.client.streamable_http import streamablehttp_client

import mcp.types as mcp_types

# SSE Client Patch (Robustness & Timeout)
McpHttpClientFactory = mcp.client.sse.McpHttpClientFactory

@asynccontextmanager
async def custom_http_client_factory(
    headers: dict[str, Any] | None = None,
    auth: httpx.Auth | None = None,
    timeout: httpx.Timeout | None = None,
    http2: bool = False
):
    # This factory is used by ADK defaults, but we override sse_client
    # so we might use this logic inside our patch.
    async with httpx.AsyncClient(
        headers=headers, auth=auth, timeout=timeout, http2=True,
        follow_redirects=True
    ) as client:
        yield client

# Apply nest_asyncio to allow nested loops if needed (common in MCP/AnyIO + Uvicorn)
import nest_asyncio
try:
    nest_asyncio.apply()
except:
    pass

@asynccontextmanager
async def patched_streamable_client(
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = 300.0,
    sse_read_timeout: float = 3600.0,
    httpx_client_factory: McpHttpClientFactory = custom_http_client_factory,
    auth: httpx.Auth | None = None,
):
    """
    Patched client that uses streamable_http_client (underscore) with a manually 
    created httpx client (HTTP/2, headers, etc.).
    Adapts signature to match mcp.client.sse.sse_client.
    """
    logger.info(f"StreamableHTTP (Patched): Starting connection attempt to {url}")
    
    # 1. Inject Authentication / Headers
    if hasattr(auth, "http") and hasattr(auth.http, "credentials"):
         token = auth.http.credentials.token
         if token:
             if headers is None: headers = {}
             headers["Authorization"] = f"Bearer {token}"
             headers["x-custom-auth"] = token 
             logger.info("StreamableHTTP: Injected x-custom-auth header")
             auth = None # Handled key via headers
    
    # 2. Use streamable_http_client with our custom factory to ensure HTTP/2
    # We DO NOT create the client here; we pass the factory.
    logger.info("StreamableHTTP: entering streamable_http_client with custom factory...")
    
    try:
        async with streamablehttp_client(
            url=url, 
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            httpx_client_factory=custom_http_client_factory, # Enforce HTTP/2 via factory
            auth=auth,
            terminate_on_close=True
        ) as (read_stream, write_stream, get_session_id):
            
            sid = get_session_id()
            logger.info(f"StreamableHTTP: Connected! Session ID: {sid}")
            
            yield read_stream, write_stream
            
            logger.info("StreamableHTTP: Session cleanup")
    except Exception as inner_e:
         logger.error(f"StreamableHTTP Inner Error: {inner_e}")
         raise inner_e

# Apply patch
mcp.client.sse.sse_client = patched_streamable_client
logger.info("Replaced mcp.client.sse.sse_client with patched_streamable_client (explicit client)")


# --- 2. ADK IMPORTS (Must be AFTER patch) ---

from google.adk.auth.auth_credential import AuthCredential, HttpCredentials, HttpAuth
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

from google.adk.agents import Agent
from google.adk.tools import google_search as adk_google_search
from google.genai import types
import google.adk as adk
from google.adk.sessions import InMemorySessionService


# --- 3. CUSTOM TOOLS ---

GLOBAL_TOOLSET_CACHE = {} 

def get_current_datetime(query: str = "") -> str:
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
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
    return f"[CHART] {data_json} [/CHART] I've plotted the {title} as a {chart_type} chart."

async def google_search(query: str) -> str:
    print(f"[Search] {query}")
    llog.start(f"Search: {query[:20]}")
    try:
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

# --- 4. INSTRUCTIONS ---

SIMPLE_INSTRUCTIONS = """
You are a Smart Financial Agent connected to FactSet. 
Your goal is to answer financial queries accurately using your tools.

### TOOLS & USAGE
1. **FactSet_GlobalPrices**: For stock prices. 
   - **CRITICAL**: Use `frequency='AQ'` for Quarterly, `'AY'` for Yearly. Never `FQ/FY`.
   - Default to 1 year range if not specified.
2. **FactSet_Fundamentals**: For metrics like sales, eps, etc.
   - If `FactSet_Fundamentals` returns empty/null, IMMEDIATELY try `FactSet_EstimatesConsensus` which often has the latest actuals.
    - For "Last 5 Years", calculate the years using `get_current_datetime` and set specific `fiscalYear` ranges.
3. **FactSet_EstimatesConsensus**: For analyst estimates, target prices, and ratings.
4. **FactSet_Ownership**: For institutional holders and funds.
5. **FactSet_People**: For leadership, board, and compensation.
6. **FactSet_MergersAcquisitions**: For M&A deals.
7. **FactSet_CalendarEvents**: For earnings calls.
8. **FactSet_SupplyChain**: For customers/suppliers.
9. **FactSet_GeoRev**: For geographic revenue exposure.
10. get_current_datetime: Use this FIRST for any date-related query ("yesterday", "last quarter") to derive exact dates.

### STRICT RULES
1. **NO GOOGLE SEARCH**. You generally do not have internet search access. Use ONLY the FactSet tools provided.
2. If a tool is missing or returns an error, use your internal knowledge or admit you cannot answer. DO NOT hallucinate a tool named "google_search".
3. **Run Real-Time**: Always use `get_current_datetime` to get today's date for `endDate` params.

### CHARTING
- If you retrieve a table of data (history, segments), ALWAYS output a [CHART] tag using plot_financial_data or standard tool chart capabilities if available.
- Visuals are high priority.
""".strip()

# --- 5. FACTORY ---

async def create_mcp_toolset_for_token(token: str) -> List[Any]:
    import sys
    sys.stderr.write(f"DEBUG: create_mcp_toolset_for_token CALLED\n")
    
    if token in GLOBAL_TOOLSET_CACHE:
         # return await GLOBAL_TOOLSET_CACHE[token].get_tools()
         # force fresh for now for safety
         pass 

    # --- 1. Create Toolset (Restored Logic) ---
    sys.stderr.write("DEBUG: creating http credentials...\n")
    http_creds = HttpCredentials(token=token)
    http_auth = HttpAuth(scheme="Bearer", credentials=http_creds)
    credential = AuthCredential(authType="http", http=http_auth)

    # Use BASE URL /content/v1 as per user examples for StreamableHTTP
    conn_params = SseConnectionParams(
        url="https://mcp.factset.com/content/v1",
        headers={
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {token}",
            "x-custom-auth": token
        },
        timeout=60.0,
        sse_read_timeout=900.0,
        reconnection_time=2.0
    )

    sys.stderr.write("DEBUG: Instantiating McpToolset...\n")
    toolset = McpToolset(
        connection_params=conn_params,
        auth_credential=credential
    )
    
    # GLOBAL_TOOLSET_CACHE[token] = toolset # uncomment if caching desired

    sys.stderr.write("DEBUG: Calling toolset.get_tools()...\n")
    tools = await toolset.get_tools()
    sys.stderr.write(f"DEBUG: MCP Server returned {len(tools)} tools\n")

    # --- HARDCODED SCHEMA PATCH (SAFETY NET) ---
    HARDCODED_ESTIMATES_SCHEMA = {
      "type": "object",
      "properties": {
          "ids": {"type": "array", "items": {"type": "string"}},
          "metrics": {"type": "array", "items": {"type": "string"}},
          "estimate_type": {
            "type": "string", 
            "enum": ["consensus_fixed", "consensus_rolling", "surprise", "ratings", "segments", "guidance"]
          },
          "fiscalPeriodStart": {"type": "string"},
          "fiscalPeriodEnd": {"type": "string"},
          "relativeFiscalStart": {"type": "string"},
          "relativeFiscalEnd": {"type": "string"}
      },
      "required": ["ids", "estimate_type"]
    }

    # --- SCHEMA OVERRIDE (LOAD FROM FILE) ---
    schema_lookup = {}
    try:
        # Look in parent directory (backend root) for mcp_tools_schema.json
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp_tools_schema.json"))
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schemas = json.load(f)
                for s in schemas:
                    if "name" in s:
                        norm_name = s["name"].lower().replace("-", "_")
                        
                        if "inputSchema" in s:
                            final_schema = s["inputSchema"]
                        elif "parameters" in s:
                            final_schema = s["parameters"]
                        else:
                            continue 
                            
                        schema_lookup[norm_name] = final_schema
                        schema_lookup[s["name"]] = final_schema
                        
                # --- ALIASES ---
                if "factset_estimatesconsensus" in schema_lookup:
                     schema_lookup["factset_estimates"] = schema_lookup["factset_estimatesconsensus"]
                     sys.stderr.write("DEBUG: Aliased factset_estimates -> factset_estimatesconsensus\n")
                
                if "factset_globalprices" in schema_lookup:
                    schema_lookup["factset_global_prices"] = schema_lookup["factset_globalprices"]
                    
            sys.stderr.write(f"DEBUG: Schema Patch Loaded {len(schemas)} schemas from {schema_path}\n")
        else:
            sys.stderr.write(f"DEBUG: Schema Patch File NOT FOUND at {schema_path}\n")
    except Exception as e:
        sys.stderr.write(f"DEBUG: Schema Patch Error: {e}\n")

    logger = logging.getLogger("uvicorn")

    return tools

# --- 6. HEALTH CHECK ---
async def check_factset_health(token: str) -> bool:
    """
    Pings FactSet MCP endpoint to verify connectivity.
    """
    try:
        url = "https://mcp.factset.com/content/v1"
        # We need headers for health check too
        headers = {
            "Authorization": f"Bearer {token}",
            "x-custom-auth": token,
            "Accept": "text/event-stream"
        }
        async with httpx.AsyncClient(timeout=10.0, http2=True, verify=True, follow_redirects=True) as client:
            resp = await client.post(url, headers=headers, json={"jsonrpc":"2.0","method":"ping","id":99})
            # POST should return 200 or 202
            if resp.status_code in [200, 202]:
                return True
            logger.warning(f"Health Check Status: {resp.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"FactSet Health Check Failed: {repr(e)}")
        return False
