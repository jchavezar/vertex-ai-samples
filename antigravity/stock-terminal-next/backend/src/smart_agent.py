from src import factset_core # Apply patches immediately (Must be FIRST)
from src.factset_core import check_factset_health, GLOBAL_TOOLSET_CACHE
import os
import logging
import datetime
import asyncio
import functools
import mcp.client.sse
from typing import Any, List
# ... (lines 7-199 are unchanged, I will use precise context replacement for the wrapper function)
from google.adk.agents import Agent
from google.adk.tools import google_search
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

async def google_search(query: str) -> str:
    """
    Performs a live Google Search for detailed world knowledge, news, or recent events.
    Use this for: "Who is CEO of X?", "Recent news about Y", "What does Z do?".
    Do NOT use for stock prices unless FactSet fails.
    """
    try:
        # Try robust search
        # Using a simple isolated agent here instead of assuming simple_factset_agent is imported from main context
        # Actually factset_core has google_search implementation too, but we can reuse it or implement here.
        # User's code for smart_agent calls `simple_factset_agent.google_search` which implies circular dependency?
        # WAIT. The user's code for smart_agent calls `simple_factset_agent.google_search(query)`.
        # `simple_factset_agent` looks like the logger name in `factset_core`.
        # Ah, the user might have had `import src.factset_core as simple_factset_agent` or similar.
        # BUT `factset_core.py` DOES have `async def google_search`. 
        # I will use `factset_core.google_search` directly.
        from src import factset_core
        result = await factset_core.google_search(query)
        if "No properties" in result or "disabled" in result:
             raise ValueError("Search disabled or empty")
        return result
    except Exception as e:
        logger.warning(f"Search tool failed: {e}")
        return f"[SYSTEM] Search unavailable. Error: {str(e)}"

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
            model="gemini-2.0-flash-exp",
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

# --- INSTRUCTIONS ---

SMART_INSTRUCTIONS = """
You are the **FactSet Smart Terminal Agent**.
Your mission is to provide accurate financial insights, real-time data, and intelligent analysis.

### CORE BEHAVIORS
1.  **Strict Financial Data Protocol (CRITICAL)**:
    - **FORBIDDEN**: Do NOT use your internal knowledge or Google Search for **specific financial numbers** (Stock Price, P/E Ratio, Revenue, EPS, Dividend Yield, etc.).
    - **MANDATORY**: You **MUST** use the provided **FactSet MCP Tools** (e.g., `factset_prices`, `factset_fundamentals`, `factset_estimates`) to retrieve this data.
    - If a tool fails, **DO NOT HALLUCINATE** a number. State clearly: "I cannot retrieve the real-time data right now."
    - **Google Search Usage**: Use ONLY for qualitative info (news, CEO names, product launches) or if FactSet tools explicitly return "Not Found" for a ticker.

2.  **Be Proactive & Conversational**:
    - **never say "I allow you to..." or "I need to determine...".** Just DO it.
    - If the user asks for "top tech company", **SEARCH for it** immediately using the `google_search` tool.
    - **CRITICAL**: If `google_search` fails or returns an error, **DO NOT APOLOGIZE**. Immediately fallback to your internal knowledge.
    - Say: "I couldn't verify the absolute live ranking, but typically **Apple, Microsoft, and NVIDIA** are the top contenders. Let's look at Apple (AAPL)."
    - **Then CALL `factset_prices` or `plot_financial_data` for Apple IMMEDIATELY.** Do not wait for permission.

3.  **Tool Usage Strategy**:
    - **Google Search**: Use for qualitative info OR as a FALLBACK if FactSet fails.
      - **Latency Protocol**: If FactSet tools fail or take >10s, IMMEDIATELY Use `google_search` for the price/data.
      - Do not apologize for using search. Just get the answer.
    - **Dates & Freshness**: 
      - Call `get_current_datetime` FIRST if the user asks for relative dates.
      - **ALWAYS check the date of the data you retrieve.**
      - If the data is from yesterday or older (e.g. closing price), **SAY SO CONVERSATIONALLY**: "The last available closing price from yesterday, Jan 23rd, was..."
      - Do not present old data as "current" without qualification.

4.  **Visuals First**:
    - If you retrieve time-series data (prices, history) or segments (revenue by region), you **MUST** use `plot_financial_data` to visualize it.
    - **Trigger**: If user asks for "history", "trend", "performance", or "chart", you **MUST** call `plot_financial_data`.
    - Users love charts.

5.  **Handling "Alphabet" / Ambiguity**:
    - "Alphabet" usually triggers a clarification between GOOGL (Class A) and GOOG (Class C).
    - If unsure, ASK or show both if easy.

6.  **Responsiveness**:
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

# --- FACTORY ---

async def create_smart_agent(token: str, model_name: str = "gemini-3-flash-preview", tool_observer: Any = None) -> Agent:
    """
    Creates a Context-Aware Smart Agent using Gemini 3.0.
    """
    # Helper to wrap tools with observation
    def wrap_tool_with_observer(tool_func):
        @functools.wraps(tool_func)
        async def obs_wrapper(*args, **kwargs):
            try:
                # Execute
                if asyncio.iscoroutinefunction(tool_func):
                    res = await tool_func(*args, **kwargs)
                else:
                    res = tool_func(*args, **kwargs)
                
                # Observe
                if tool_observer:
                    try:
                        name = getattr(tool_func, "name", tool_func.__name__)
                        if asyncio.iscoroutinefunction(tool_observer):
                            await tool_observer(name, args, kwargs, res)
                        else:
                            tool_observer(name, args, kwargs, res)
                    except Exception as oe:
                        logger.error(f"Observer Error: {oe}")
                
                return res
            except Exception as e:
                # We can also observe errors if we want
                if tool_observer:
                    try:
                         name = getattr(tool_func, "name", tool_func.__name__)
                         err_res = f"Error: {e}"
                         if asyncio.iscoroutinefunction(tool_observer):
                            await tool_observer(name, args, kwargs, err_res)
                         else:
                            tool_observer(name, args, kwargs, err_res)
                    except: pass
                raise e
        
        # Copy metadata
        obs_wrapper.__name__ = getattr(tool_func, "__name__", "wrapper")
        obs_wrapper.__doc__ = getattr(tool_func, "__doc__", "")
        if hasattr(tool_func, "name"): obs_wrapper.name = tool_func.name
        if hasattr(tool_func, "description"): obs_wrapper.description = tool_func.description
        if hasattr(tool_func, "input_schema"): obs_wrapper.input_schema = tool_func.input_schema
        return obs_wrapper

    # 1. Base Tools (Wrapped)
    base_tools = [get_current_datetime, google_search, plot_financial_data, analyze_pdf_url, get_market_sentiment]
    tools = [wrap_tool_with_observer(t) for t in base_tools]
    
    # Integrate FactSet/MCP if token is available
    if token and "mock" not in token:
        try:
            import traceback
            from src.factset_core import GLOBAL_TOOLSET_CACHE
            
            # PRE-FLIGHT CHECK
            is_healthy = await check_factset_health(token)
            if not is_healthy:
                logger.warning("Smart Agent: FactSet Pre-flight failed. Attempting connection anyway.")

            toolset = None
            if token in GLOBAL_TOOLSET_CACHE:
                logger.info("Smart Agent: Using CACHED McpToolset.")
                toolset = GLOBAL_TOOLSET_CACHE[token]
            else:
                logger.info(f"Smart Agent: Creating NEW McpToolset with Native Auth. Token starting with: {token[:10]}")
                from fastapi.openapi.models import HTTPBearer
                from google.adk.auth.auth_credential import AuthCredential, HttpCredentials, HttpAuth
                from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

                auth_scheme = HTTPBearer(scheme="bearer")
                http_creds = HttpCredentials(token=token)
                http_auth = HttpAuth(scheme="Bearer", credentials=http_creds)
                credential = AuthCredential(authType="http", http=http_auth)

                mcp_config = SseConnectionParams(
                     url="https://mcp.factset.com/content/v1/sse",
                     headers={"Accept": "text/event-stream"},
                     timeout=10.0
                )
                toolset = McpToolset(
                    connection_params=mcp_config,
                    auth_scheme=auth_scheme,
                    auth_credential=credential
                )
                GLOBAL_TOOLSET_CACHE[token] = toolset
            
                try:
                    mcp_tools = await toolset.get_tools()
                    print(f"!!! SMART AGENT TOOLS FETCHED: {[t.name for t in mcp_tools]}", flush=True)
                    
                    safe_mcp_tools = []
                    for tool in mcp_tools:
                        # MCP tools are already async callables. We wrap them for safety AND observation.
                        # FIX: Bind tool immediately to avoid loop variable capture issues
                        async def safe_tool_wrapper(*args, _tool=tool, **kwargs):
                            try:
                                logger.info(f"Invoking MCP Tool: {_tool.name}")
                                # Add safety timeout to prevent infinite hanging
                                res = await asyncio.wait_for(_tool(*args, **kwargs), timeout=25.0)
                                logger.info(f"Finished MCP Tool: {_tool.name}")
                                # Observation is handled by the outer wrap, BUT we construct it here to ensure we capture native MCP execution
                                return res
                            except asyncio.TimeoutError:
                                logger.error(f"MCP Tool Execution Timed Out ({_tool.name}) after 25s")
                                return f"Error: Tool {_tool.name} timed out after 25 seconds. Please try again."
                            except Exception as e:
                                logger.error(f"MCP Tool Execution Failed ({_tool.name}): {e}")
                                return f"Error executing {_tool.name}: {str(e)}"
                        
                        safe_tool_wrapper.__name__ = tool.name
                        safe_tool_wrapper.__doc__ = tool.description
                        if hasattr(tool, "input_schema"):
                            safe_tool_wrapper.input_schema = tool.input_schema
                        
                        # Apply Observation Check
                        wrapped_mcp_tool = wrap_tool_with_observer(safe_tool_wrapper)
                        safe_mcp_tools.append(wrapped_mcp_tool)

                    tools.extend(safe_mcp_tools)
                except Exception as e:
                    logger.error(f"Smart Agent: Failed to fetch MCP tools: {e}")
                    traceback.print_exc()
                    
                    # FALLBACK: Register "Error Tools"
                    err_msg = "Connection Error: Unable to reach FactSet. Please try again."
                    def create_error_tool(tool_name):
                        def error_tool(*args, **kwargs): return err_msg
                        error_tool.__name__ = tool_name
                        return error_tool

                    # Fallbacks also need wrapping
                    fallback_tools = [
                        wrap_tool_with_observer(create_error_tool("factset_global_prices")),
                        wrap_tool_with_observer(create_error_tool("factset_fundamentals")),
                        wrap_tool_with_observer(create_error_tool("factset_estimates")),
                        wrap_tool_with_observer(create_error_tool("FactSet_Prices"))
                    ]
                    tools.extend(fallback_tools)
                    if token in GLOBAL_TOOLSET_CACHE: del GLOBAL_TOOLSET_CACHE[token]
            
        except Exception as e:
            logger.error(f"Failed to configure FactSet MCP: {e}")

    # Mock Mode Fallback
    if not token or "mock" in token:
        logger.info("Smart Agent: Enabling MOCK tools (backed by Yahoo Finance if available)")
        from src import mock_data
        
        def factset_prices(ticker: str): 
            return mock_data.get_mock_price_response(ticker)
            
        def factset_global_prices(ticker: str, startDate: str = None, endDate: str = None, frequency: str = "D"):
             return mock_data.get_mock_history_response(ticker)
        
        tools.extend([wrap_tool_with_observer(factset_prices), wrap_tool_with_observer(factset_global_prices)])

    return Agent(
        name="factset_analyst", 
        model=model_name,
        instruction=SMART_INSTRUCTIONS,
        tools=tools
    )
