from src import factset_core # Apply patches immediately (Must be FIRST)
from src.factset_core import check_factset_health, GLOBAL_TOOLSET_CACHE
import os
import logging
import datetime
import asyncio
import functools
import mcp.client.sse
from typing import Any, List
from google.adk.agents import Agent
# from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.sessions import InMemorySessionService
import google.adk as adk
from google.genai import types
import secrets
from google.adk.models.anthropic_llm import Claude
from google.adk.models.registry import LLMRegistry

# Register Anthropic Models
LLMRegistry.register(Claude)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_agent")

# --- CONFIG ---

FACTSET_TOOL_MAPPING = {
    "factset_fundamentals": "FactSet_Fundamentals",
    "factset_estimates": "FactSet_EstimatesConsensus",
    "factset_estimatesconsensus": "FactSet_EstimatesConsensus", 
    "factset_globalprices": "FactSet_GlobalPrices",
    "factset_global_prices": "FactSet_GlobalPrices",
    "factset_ownership": "FactSet_Ownership",
    "factset_mergersacquisitions": "FactSet_MergersAcquisitions",
    "factset_mergers_acquisitions": "FactSet_MergersAcquisitions", # Keep both just in case
    "factset_people": "FactSet_People",
    "factset_calendarevents": "FactSet_CalendarEvents",
    "factset_calendar_events": "FactSet_CalendarEvents", # Keep both
    "factset_metrics": "FactSet_Metrics",
    "factset_georev": "FactSet_GeoRev",
    "factset_supplychain": "FactSet_SupplyChain",
    "factset_supply_chain": "FactSet_SupplyChain", # Keep both
}

# --- TOOLS ---

def get_current_datetime(query: str = "") -> str:
    """
    Returns the current date and time in ISO format, plus smart relative dates.
    Useful for 'yesterday', 'last quarter', 'last year' logic.
    """
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    return f"""
    Current Time: {now.isoformat()}
    Today: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})
    Yesterday: {yesterday.strftime('%Y-%m-%d')}
    Year: {now.year}
    """

async def plot_financial_data(title: str, chart_type: str, data_json: str) -> str:
    """
    PLOTS a custom chart on the dashboard. 
    Call this whenever the user asks for a visualization or when you retrieve time-series data (prices, revenue execution) that is best shown as a chart.
    Args:
        title: Chart title (e.g. 'Apple Stock Price 1Y').
        chart_type: 'line' (time series), 'bar' (categories/comparison), 'pie' (segments).
        data_json: JSON string representation of the data.
    """
    import json
    try:
        if isinstance(data_json, str):
            try:
                _ = json.loads(data_json)
                actual_data = data_json
            except:
                actual_data = json.dumps(data_json)
        else:
            actual_data = json.dumps(data_json)
            
        payload = json.dumps({"title": title, "chartType": chart_type, "data": json.loads(actual_data)})
        return f"[CHART]{payload}[/CHART] I've generated the {chart_type} chart for {title}."
    except Exception as e:
        logger.error(f"Chart payload error: {e}")
        return f"Error generating chart: {e}"



async def analyze_pdf_url(url: str, query: str = "Summarize this document") -> str:
    """
    Downloads a PDF from a URL and analyzes it using Gemini's multimodal capabilities.
    Use this when you need to read a specific PDF document (e.g. Earnings Report, 10-K) to answer a question.
    Args:
        url: The direct URL to the PDF.
        query: Specific question to answer from the PDF.
    """
    import httpx
    from google.genai import Client, types
    import os
    
    try:
        # 1. Download PDF
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True, timeout=15.0)
            if resp.status_code != 200:
                return f"Error downloading PDF: {resp.status_code}"
            pdf_bytes = resp.content

        # 2. Analyze with Gemini
        # We create a temporary client just for this tool execution
        api_key = os.getenv("GOOGLE_API_KEY") 
        if not api_key: return "Error: GOOGLE_API_KEY not found."
        
        client = Client(api_key=api_key)
        
        prompt = f"Analyze the attached PDF and answer this question: {query}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ]
        )
        
        return f"[PDF ANALYSIS of {url}]\\n{response.text}"

    except Exception as e:
        logger.error(f"PDF Analysis failed: {e}")
        return f"Error analyzing PDF: {str(e)}"

async def get_market_sentiment(ticker: str) -> str:
    """
    Returns a custom qualitative sentiment analysis for a ticker (Demo Custom Tool).
    """
    # Mock logic for demo
    return f"[CUSTOM TOOL] {ticker} sentiment is currently BULLISH based on recent social volume."

async def consult_analyst_copilot(query: str = "Research macro investability context") -> str:
    """
    Delegates complex macro, sector, or 'investability' research to the Analyst Copilot sub-agent.
    Use this when the user asks for high-level strategy, sector switch, or market 'opinions'.
    """
    from src.analyst_copilot import create_analyst_copilot
    import google.adk as adk
    from google.adk.sessions import InMemorySessionService
    import secrets
    
    copilot = create_analyst_copilot()
    session_service = InMemorySessionService()
    runner = adk.Runner(app_name="copilot", agent=copilot, session_service=session_service)
    session_id = secrets.token_hex(4)
    await session_service.create_session(session_id=session_id, user_id="main_agent", app_name="copilot")
    
    final_result = ""
    msg = types.Content(role="user", parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id="main_agent", session_id=session_id, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_result += part.text
                    
    return f"[ANALYST COPILOT DELEGATION]\\n{final_result}"

def fix_tool_params(tool_name: str, kwargs: dict) -> dict:
    """
    Fixes common parameter naming issues between ADK/Agent and actual Tool/API expectations.
    """
    # 1. Handle 'ids' vs 'tickers'
    # FactSet tools often expect 'ids', but Agent/LLM might generate 'tickers'.
    if "ids" in kwargs and not kwargs["ids"]:
        if "tickers" in kwargs:
            kwargs["ids"] = kwargs.pop("tickers")
    
    if "tickers" in kwargs and "ids" not in kwargs:
         kwargs["ids"] = kwargs.pop("tickers")
         
    # 2. Handle 'start_date' vs 'startDate'
    # API expects camelCase 'startDate', Agent might send snake_case
    if "start_date" in kwargs:
        kwargs["startDate"] = kwargs.pop("start_date")
    if "end_date" in kwargs:
        kwargs["endDate"] = kwargs.pop("end_date")
        
    return kwargs

# --- INSTRUCTIONS ---

SMART_INSTRUCTIONS = """
You are the **FactSet Smart Terminal Agent**.
Your mission is to provide accurate financial insights, real-time data, and intelligent analysis.

### CORE BEHAVIORS
1.  **Strict Financial Data Protocol (CRITICAL)**:
    - **FORBIDDEN**: Do NOT use your internal knowledge or Google Search for **specific financial numbers** (Stock Price, P/E Ratio, Revenue, EPS, Dividend Yield, etc.).
    - **MANDATORY**: You **MUST** use the provided **FactSet MCP Tools** (e.g., `FactSet_GlobalPrices`, `FactSet_Fundamentals`, `FactSet_EstimatesConsensus`) to retrieve this data.
    - If a tool fails, **DO NOT HALLUCINATE** a number. State clearly: "I cannot retrieve the real-time data right now."
    - **No Internet Search**: You do not have access to Google Search. Do not attempt to use it.

2.  **Be Proactive & Conversational**:
    - **never say "I allow you to..." or "I need to determine...".** Just DO it.
    - If the user asks for "top tech company", **Use your internal knowledge** to identify leaders (AAPL, NVDA, MSFT).
    - **Then CALL `FactSet_GlobalPrices` or `plot_financial_data` for those tickers IMMEDIATELY.** Do not wait for permission.

3.  **Tool Usage Strategy**:
    - **Dates & Freshness**: 
      - Call `get_current_datetime` FIRST if the user asks for relative dates.
      - **ALWAYS check the date of the data you retrieve.**
      - If the data is from yesterday or older (e.g. closing price), **SAY SO CONVERSATIONALLY**: "The last available closing price from yesterday, Jan 23rd, was..."
      - Do not present old data as "current" without qualification.

4.  **Visuals First**:
    - If you retrieve time-series data (prices, history) or segments (revenue by region), you **MUST** use `plot_financial_data` to visualize it.
    - **Trigger**: If user asks for "history", "trend", "performance", or "chart", you **MUST** call `plot_financial_data`.
    - Users love charts.
    - **Data Efficiency**: When using `FactSet_GlobalPrices` for periods longer than 1 year, prefer Weekly (`W`) or Monthly (`M`) frequency to reduce data volume and avoid resource limits, unless Daily (`D`) is explicitly requested.

5.  **Handling "Alphabet" / Ambiguity**:
    - "Alphabet" usually triggers a clarification between GOOGL (Class A) and GOOG (Class C).
    - If unsure, ASK or show both if easy.

6.  **Analyst Copilot (Strategic Research)**:
    - If the user asks about **"investability"**, **"market trends"**, **"macro environment"**, or to **"switch sector/view"**, you **MUST** call `consult_analyst_copilot`.
    - Example: "I want to get up to speed on the investability of NVDA" -> Call `consult_analyst_copilot`.
    - This specialist has access to web news and macro strategy tools you do not.

7.  **Multimodal Analysis (YouTube/Video) - MANDATORY**:
    - If a **YouTube URL** or **Video file** is attached to the message, you **MUST** analyze its content (visuals and audio).
    - **YOU HAVE NATIVE ACCESS**: Do not claim you cannot process video. You can see the video stream and hear the audio perfectly.
    - **Visual & Audio Context**: Use the visuals (charts on screen, speakers, demos) and audio (interviews, narration) to answer user questions.
    - **MANDATORY ACKNOWLEDGEMENT**: Your response MUST begin with: "Analyzing the attached video: [Summary of what you see/hear]...".
    - **Example**: "Analyzing the attached video: I see a technical presentation about NVIDIA's new Blackwell architecture. The speaker is discussing the energy efficiency of the new H100 GPUs..."
    - **Context Priority**: Information extracted from the video should be treated as primary context. If it contradicts your general knowledge, trust the video.
    - **No Hallucinations**: If the video really doesn't contain the info, say: "The video doesn't show that specific data point."

8.  **Responsiveness**:
    - Be concise.
    - If data is not available, say so immediately. Do not loop.

### TONE
- Professional, insightful, and helpful.
- "I'll check the latest market cap rankings for you."
- "Here is the data for Apple, the current leader."

### TOOL SCHEMAS
(Use these signatures as the ground truth for tool arguments)
"""

# Load Schema dynamically if available
import json
schema_path = os.path.join(os.path.dirname(__file__), "../mcp_tools_schema.json")
if os.path.exists(schema_path):
    try:
        with open(schema_path, "r") as f:
            schemas = json.load(f)
            # Compact formatted string
            schema_str = json.dumps(schemas, indent=2)
            SMART_INSTRUCTIONS += f"\n{schema_str}"
    except Exception as e:
        logger.warning(f"Failed to load schema for instructions: {e}")

from google.adk.tools.base_tool import BaseTool
from google.genai import types

class DelegatingTool(BaseTool):
    @property
    def parameters(self):
        """
        Hack to satisfy google.adk.models.google_llm._build_function_declaration_log
        which expects a 'parameters' attribute with a 'properties' attribute.
        """
        class MockParams:
            @property
            def properties(self):
                return {}
        return MockParams()

    def __init__(self, target_tool, schema_override=None, observer=None):
        name = getattr(target_tool, "name", getattr(target_tool, "__name__", "UNKNOWN"))
        description = getattr(target_tool, "description", getattr(target_tool, "__doc__", ""))
        super().__init__(name=name, description=description)
        
        self._target = target_tool
        self._observer = observer
        
        # Set Schema
        if schema_override:
            self.input_schema = schema_override
        elif hasattr(target_tool, "input_schema"):
            self.input_schema = target_tool.input_schema
        else:
            # Vertex AI requires parameters to be an OBJECT even if empty
            self.input_schema = {"type": "object", "properties": {}}

    def _get_declaration(self):
        # Explicitly construct the declaration
        # We need to handle recursion if Schema is nested? 
        # types.Schema(**dict) usually works for simple schemas.
        # But we must be careful with 'type' vs 'type_'. attributes.
        # The ADK/GenAI SDK usually prefers we use the efficient constructor.
        
        # Using Client-compatible declaration construction
        try:
             # Convert dict schema to types.Schema
             # We rely on the fact that the JSON structure matches the Schema fields
             # (type, format, description, nullable, enum, properties, required, items)
             
             # Note: google.genai.types.Schema takes fields directly.
             # We might need to recursively convert 'properties' and 'items' if the constructor doesn't.
             # But typically the SDK Helper 'from_json_schema' or similar is best if available.
             # Since we don't have that, we try basic dict passing or raw access.
             
             # Safest: Use the ADK automatic util if accessible, OR
             # Just return a TOOL object with the raw dict if the SDK supports it.
             # The SDK often supports passing the dict directly for parameters.
             
             # Let's try passing the dict directly to FunctionDeclaration(..., parameters=...)
             # If that fails, we might need types.Schema
             
             from google.genai import types
             return types.FunctionDeclaration(
                 name=self.name,
                 description=self.description,
                 parameters=self.input_schema # Pass dict directly (often supported)
             )
        except Exception as e:
            logger.error(f"DelegatingTool Declaration Error: {e}")
            raise e

    async def run_async(self, *args, **kwargs):
        try:
            # Determine the actual callable method
            method = None
            if hasattr(self._target, 'run_async'):
                method = self._target.run_async
            elif asyncio.iscoroutinefunction(self._target) or hasattr(self._target, '__call__'):
                method = self._target
            else:
                method = self._target

            # Inspect signature to decide on unpacking and filtering
            should_unpack = True
            allowed_keys = None # None means allow all
            
            import inspect
            try:
                sig = inspect.signature(method)
                params = sig.parameters
                
                # If target explicitly accepts 'args', do NOT unpack properties into kwargs
                if "args" in params:
                    should_unpack = False
                
                # Determine allowed keys for filtering
                has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
                if not has_var_keyword:
                    allowed_keys = set(params.keys())
            except Exception as e:
                logger.warning(f"Signature inspection failed for {self.name}: {e}")

            # Smart Unpacking
            if "args" in kwargs and isinstance(kwargs["args"], dict):
                if should_unpack:
                    tool_args = kwargs.pop("args")
                    kwargs.update(tool_args)
            
            # 1. FIX PARAMS (After unpacking)
            kwargs = fix_tool_params(self.name, kwargs)
            
            # 2. FILTER KWARGS
            if allowed_keys is not None:
                kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}

            # Execute
            if asyncio.iscoroutinefunction(method):
                 res = await method(*args, **kwargs)
            else:
                 res = method(*args, **kwargs)

            # Observe
            if self._observer:
                 try:
                     if asyncio.iscoroutinefunction(self._observer):
                         await self._observer(self.name, args, kwargs, res)
                     else:
                         self._observer(self.name, args, kwargs, res)
                 except Exception as oe:
                     logger.error(f"Observer Error: {oe}")
            return res
            
        except Exception as e:
            # Observe Error
            if self._observer:
                 try:
                     err_res = f"Error: {e}"
                     if asyncio.iscoroutinefunction(self._observer):
                         await self._observer(self.name, args, kwargs, err_res)
                     else:
                         self._observer(self.name, args, kwargs, err_res)
                 except: pass
            raise e

    def __call__(self, *args, **kwargs):
        # For non-async execution if needed
        raise NotImplementedError("Sync execution not supported in this wrapper")

# --- FACTORY ---

async def create_smart_agent(token: str, model_name: str = "gemini-2.5-flash", tool_observer: Any = None) -> Agent:
    print(f"!!! CREATE SMART AGENT: model={model_name}, token_present={bool(token)}")
    
    # Load Schemas for Injection
    loaded_schemas = {}
    schema_path = os.path.join(os.path.dirname(__file__), "../mcp_tools_schema.json")
    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r") as f:
                raw_schemas = json.load(f)
                for s in raw_schemas:
                    loaded_schemas[s["name"]] = s
        except Exception as e:
            logger.warning(f"Failed to load schema for injection: {e}")

    # Explicit Rules for Prompt
    CRITICAL_RULES = """
    
    ## CRITICAL TOOL PARAMETER RULES (MUST FOLLOW)
    
    When calling FactSet tools, you MUST use these EXACT parameter values:
    
    ### FactSet_Fundamentals
    - data_type: MUST be exactly "fundamentals" (no other value allowed)
    - metrics: Use FF_ prefix (FF_SALES, FF_EPS_BASIC, FF_NET_MGN, FF_DEBT, FF_ROE)
    
    ### FactSet_GlobalPrices
    - data_type: MUST be one of: "prices", "returns", "corporate_actions", "annualized_dividends", "shares_outstanding"
    
    ### FactSet_Ownership
    - data_type: MUST be one of: "fund_holdings", "security_holders", "insider_transactions", "institutional_transactions"
    
    ### FactSet_EstimatesConsensus
    - estimate_type: MUST be one of: "consensus_fixed", "consensus_rolling", "surprise", "ratings", "segments", "guidance"
    - metrics: NO FF_ prefix (use SALES, EPS, EBITDA, PRICE_TGT)
    
    ### FactSet_People
    - data_type: MUST be one of: "profiles", "jobs", "company_people", "company_positions", "company_compensation", "company_stats"
    
    ### FactSet_GeoRev
    - data_type: MUST be one of: "regions", "countries"
    
    ### FactSet_MergersAcquisitions
    - data_type: MUST be one of: "deals_by_company", "public_targets", "deal_details"
    
    ### FactSet_SupplyChain
    - relationshipType: MUST be one of: "COMPETITORS", "CUSTOMERS", "SUPPLIERS", "PARTNERS"
    
    ## PLOTTING OPTIMIZATION (CRITICAL)
    - When you retrieve a large dataset (e.g. from FactSet_GlobalPrices), the system caches it automatically.
    - To plot this data, call `plot_financial_data` with `use_last_data=True` and omit `data_json`.
    - **MULTI-METRIC SUPPORT**: If you call multiple tools (e.g. Sales then Net Income) and then call `plot_financial_data(use_last_data=True)`, the system will AUTOMATICALLY MERGE both tables into a grouped comparison chart.
    - **Trigger**: When comparing companies or metrics, fetch all data first, then call `plot_financial_data(chart_type="bar", use_last_data=True)`.
    - **NEVER** write out the full JSON data if you just retrieved it. It is too slow.
    
    FAILURE TO USE EXACT VALUES WILL CAUSE API ERRORS.
    """
    
    # Append to instructions
    global SMART_INSTRUCTIONS
    if "CRITICAL TOOL PARAMETER RULES" not in SMART_INSTRUCTIONS:
         SMART_INSTRUCTIONS += CRITICAL_RULES

    # Request-Scoped Data Cache
    request_data_cache = {"results": []}

    # Scoped Plot Tool
    async def plot_financial_data(title: str, chart_type: str, data_json: str = None, use_last_data: bool = False) -> str:
        """
        PLOTS a custom chart on the dashboard.
        Args:
            title: Chart title (e.g. 'Apple Stock Price 1Y').
            chart_type: 'line', 'bar', 'pie'.
            data_json: JSON string of data (Optional if use_last_data=True).
                       Preferred format for data items: {"label": "Name", "value": 100}.
            use_last_data: If True, uses the data from the most recent tool call(s) (e.g. Prices). 
                           If multiple data sources are found in the recent history, they will be MERGED.
        """
        import json
        try:
            actual_data = None
            
            if use_last_data:
                logger.info("Auto-merging cached data for plot...")
                results = request_data_cache.get("results", [])
                if not results:
                    return "Error: No cached data found. Please provide data_json."
                
                # Merge logic: if we have multiple tool results, we try to join them on ticker/date
                merged_data = []
                # Heuristic: find the results that contain lists (data)
                data_sources = []
                for res in results:
                    if isinstance(res, list): data_sources.append(res)
                    elif isinstance(res, dict) and "content" in res:
                        try:
                            text_body = res["content"][0]["text"]
                            parsed = json.loads(text_body) if isinstance(text_body, str) else text_body
                            d = parsed.get("data", parsed)
                            if isinstance(d, list): data_sources.append(d)
                        except: pass
                
                if len(data_sources) == 1:
                    actual_data = data_sources[0]
                elif len(data_sources) > 1:
                    # SMART MERGE: This is the 'Candid' capability fix.
                    # We merge multiple distinct tool outputs into one big list for the pivot tool.
                    actual_data = []
                    for ds in data_sources:
                        actual_data.extend(ds)
                
                if not actual_data:
                    return "Error: Could not extract valid data from cache."
            else:
                if not data_json: return "Error: data_json is required if use_last_data=False."
                if isinstance(data_json, str):
                    try:
                        actual_data = json.loads(data_json)
                    except:
                        actual_data = data_json 
                else:
                    actual_data = data_json
            
            # Ensure actual_data is serializable
            payload = json.dumps({"title": title, "chartType": chart_type, "data": actual_data})
            return f"[CHART]{payload}[/CHART] I've generated the {chart_type} chart for {title}."
        except Exception as e:
            logger.error(f"Chart payload error: {e}")
            return f"Error generating chart: {e}"

    # Wrapper Helper using DelegatingTool
    def wrap_tool(tool_func):
        t_name = getattr(tool_func, "name", getattr(tool_func, "__name__", "UNKNOWN"))
        schema = None
        if t_name in loaded_schemas:
             schema = loaded_schemas[t_name].get("parameters", {})
             logger.info(f"Smart Agent: Injected robust schema for {t_name}")
        
        # Intercept Result for Cache
        original_observer = tool_observer
        
        async def caching_observer(name, args, kwargs, result):
            # Cache the result if it looks like data
            request_data_cache["results"].append(result)
            # Chain to original
            if original_observer:
                if asyncio.iscoroutinefunction(original_observer):
                    await original_observer(name, args, kwargs, result)
                else:
                    original_observer(name, args, kwargs, result)

        return DelegatingTool(tool_func, schema_override=schema, observer=caching_observer)

    # 1. Base Tools (Wrapped)
    # REMOVED google_search as per user request to prevent fallback hallucinations
    base_tools = [get_current_datetime, plot_financial_data, analyze_pdf_url, get_market_sentiment, consult_analyst_copilot]
    tools = [wrap_tool(t) for t in base_tools]
    
    # Integrate FactSet/MCP if token is available
    if token and "mock" not in token:
        try:
            import traceback
            from src.factset_core import create_mcp_toolset_for_token
            
            # Use the shared, robust factory from factset_core
            logger.info(f"Smart Agent: Requesting MCP tools from factory. Token: {token[:10]}...")
            mcp_tools = await create_mcp_toolset_for_token(token)
            
            if mcp_tools:
                safe_mcp_tools = []
                for tool in mcp_tools:
                    # SAFE NAME RETRIEVAL
                    if hasattr(tool, 'name'):
                        name_attr = tool.name
                    elif hasattr(tool, '__name__'):
                        name_attr = tool.__name__
                    else:
                        name_attr = "UNKNOWN_TOOL"
                        
                    original_name = name_attr.lower()
                    original_name = name_attr.lower()
                    
                    if original_name.startswith("factset_"):
                        target_name = FACTSET_TOOL_MAPPING.get(original_name)
                        if target_name:
                             # Rename the tool safely
                             try:
                                 tool.name = target_name 
                             except:
                                 pass
                             
                             # Apply Wrapper (Schema Injection Happens Here)
                             wrapped_tool = wrap_tool(tool)
                             safe_mcp_tools.append(wrapped_tool)
                             continue
                        else:
                            # Skip unknown FactSet tools to prevent LLM confusion
                            logger.info(f"Skipping unknown FactSet tool: {original_name}")
                            continue
                    
                    # Also allow injected non-factset tools (e.g. google_search)
                    logger.info(f"Adding non-FactSet Tool: {name_attr}")
                    wrapped_tool = wrap_tool(tool)
                    safe_mcp_tools.append(wrapped_tool)
                    
                tools.extend(safe_mcp_tools)

            else:
                 raise Exception("No tools returned from MCP factory.")

        except Exception as e:
            logger.error(f"Smart Agent: Failed to configure FactSet MCP: {e}")
            traceback.print_exc()
            
            # FALLBACK: Use Yahoo Finance (market_data) instead of Error Message
            logger.info("Smart Agent: MCP Failed, switching to Yahoo Finance Fallback (Real Data)")
            from src import market_data
            
            def factset_global_prices(ids: List[str], startDate: str = None, endDate: str = None, frequency: str = "D"):
                 results = []
                 for t in ids:
                    val = market_data.get_real_history(t)
                    if val: results.append(val)
                 if not results: return "Error: Unable to fetch history from Yahoo Finance."
                 return results
            
            # Use strict name "FactSet_GlobalPrices"
            factset_global_prices.__name__ = "FactSet_GlobalPrices"

            fallback_tools = [
                wrap_tool(factset_global_prices)
            ]
            tools.extend(fallback_tools)

    # Yahoo Finance Fallback (Real Data)
    if not token or "mock" in token:
        logger.info("Smart Agent: Enabling Yahoo Finance Fallback tools (No FactSet Token)")
        from src import market_data
        
        def factset_global_prices(ids: List[str], startDate: str = None, endDate: str = None, frequency: str = "D"):
             results = []
             for t in ids:
                val = market_data.get_real_history(t)
                if val: results.append(val)
             if not results: return "Error: Unable to fetch history from Yahoo Finance."
             return results
        
        # Use strict name "FactSet_GlobalPrices"
        factset_global_prices.__name__ = "FactSet_GlobalPrices"

        tools.extend([
            wrap_tool(factset_global_prices)
        ])

    print(f"DEBUG: Final Agent Tools: {[getattr(t, 'name', getattr(t, '__name__', str(t))) for t in tools]}")
    for t in tools:
        t_name = getattr(t, 'name', getattr(t, '__name__', str(t)))
        print(f"  - {t_name}: Schema Present? {hasattr(t, 'input_schema')}")
        if hasattr(t, "input_schema"):
             try:
                 print(f"    Schema: {json.dumps(t.input_schema)[:100]}...")
             except: pass

    return Agent(
        name="factset_analyst", 
        model=model_name,
        instruction=SMART_INSTRUCTIONS,
        tools=tools
    )
