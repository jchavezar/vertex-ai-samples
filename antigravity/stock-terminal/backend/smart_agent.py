import simple_factset_agent # Apply patches immediately (Must be FIRST)
from simple_factset_agent import check_factset_health
import os
import logging
import datetime
import mcp.client.sse
from typing import Any, List
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.sessions import InMemorySessionService
import google.adk as adk
from google.genai import types
import secrets

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_agent")

# --- TOOLS ---

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
    # This tool doesn't actually plot in backend, it emits a tag for the frontend to render.
    # Return a structured JSON for the frontend to parse easily.
    import json
    try:
        # Verify if data_json is valid JSON or load it if string
        if isinstance(data_json, str):
            try:
                # Try to parse to ensure it's valid, but return the string for the tag
                _ = json.loads(data_json)
                actual_data = data_json
            except:
                # If not valid JSON, wrap it as a string
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
        result = await simple_factset_agent.google_search(query)
        if "No properties" in result or "disabled" in result:
             raise ValueError("Search disabled or empty")
        return result
    except Exception as e:
        logger.warning(f"Search tool failed: {e}")
        # Return a system hint instead of a user-facing error
        return f"[SYSTEM] Search unavailable. Error: {str(e)}"

# --- INSTRUCTIONS ---

SMART_INSTRUCTIONS = """
You are the **FactSet Smart Terminal Agent**.
Your mission is to provide accurate financial insights, real-time data, and intelligent analysis.

### CORE BEHAVIORS
1.  **Be Proactive & Conversational**:
    - **never say "I allow you to..." or "I need to determine...".** Just DO it.
    - If the user asks for "top tech company", **SEARCH for it** immediately using the `google_search` tool.
    - **CRITICAL**: If `google_search` fails or returns an error, **DO NOT APOLOGIZE**. Immediately fallback to your internal knowledge.
    - Say: "I couldn't verify the absolute live ranking, but typically **Apple, Microsoft, and NVIDIA** are the top contenders. Let's look at Apple (AAPL)."
    - **Then CALL `factset_prices` or `plot_financial_data` for Apple IMMEDIATELY.** Do not wait for permission.

2.  **Tool Usage Strategy**:
    - **Google Search**: Use for qualitative info OR as a FALLBACK if FactSet fails.
      - **Latency Protocol**: If FactSet tools fail or take >10s, IMMEDIATELY Use `google_search` for the price/data.
      - Do not apologize for using search. Just get the answer.
    - **Dates & Freshness**: 
      - Call `get_current_datetime` FIRST if the user asks for relative dates.
      - **ALWAYS check the date of the data you retrieve.**
      - If the data is from yesterday or older (e.g. closing price), **SAY SO CONVERSATIONALLY**: "The last available closing price from yesterday, Jan 23rd, was..."
      - Do not present old data as "current" without qualification.

3.  **Visuals First**:
    - If you retrieve time-series data (prices, history) or segments (revenue by region), you **MUST** use `plot_financial_data` to visualize it.
    - Users love charts.

4.  **Handling "Alphabet" / Ambiguity**:
    - "Alphabet" usually triggers a clarification between GOOGL (Class A) and GOOG (Class C).
    - If unsure, ASK or show both if easy.

5.  **Responsiveness**:
    - Be concise.
    - If data is not available, say so immediately. Do not loop.

### TONE
- Professional, insightful, and helpful.
- "I'll check the latest market cap rankings for you."
- "Here is the data for Apple, the current leader."
""".strip()

# --- FACTORY ---

async def create_smart_agent(token: str, model_name: str = "gemini-2.5-pro") -> Agent:
    """
    Creates a Context-Aware Smart Agent using Gemini 3.0.
    """
    tools = [get_current_datetime, google_search, plot_financial_data]
    
    # Integrate FactSet/MCP if token is available
    if token and "mock" not in token:
        try:
            import traceback
            from simple_factset_agent import GLOBAL_TOOLSET_CACHE
            
            # PRE-FLIGHT CHECK
            is_healthy = await check_factset_health(token)
            if not is_healthy:
                logger.warning("Smart Agent: FactSet Pre-flight failed. Attempting connection anyway (could be just auth redirect).")
                # WE DO NOT RAISE HERE ANYMORE. Let McpToolset try and fail gracefully if needed.

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
                
                # Corrected Auth Structure based on Schema
                # AuthCredential -> http (HttpAuth) -> credentials (HttpCredentials) -> token
                http_creds = HttpCredentials(token=token)
                http_auth = HttpAuth(scheme="Bearer", credentials=http_creds)
                
                # authType="http" is required by the valid schema
                credential = AuthCredential(authType="http", http=http_auth)

                mcp_config = SseConnectionParams(
                     url="https://mcp.factset.com/content/v1/sse",
                     headers={"Accept": "text/event-stream"},
                     timeout=10.0  # Reduced to 10s to fail fast on auth redirects
                )
                toolset = McpToolset(
                    connection_params=mcp_config,
                    auth_scheme=auth_scheme,
                    auth_credential=credential
                )
                GLOBAL_TOOLSET_CACHE[token] = toolset
            
            # Fetch tools asynchronously
                try:
                    mcp_tools = await toolset.get_tools()
                    print(f"!!! SMART AGENT TOOLS FETCHED: {[t.name for t in mcp_tools]}", flush=True)
                    
                    # WRAP TOOLS FOR SAFETY (Prevent ConnectionError crash during execution)
                    safe_mcp_tools = []
                    for tool in mcp_tools:
                        # Capture tool in closure
                        async def safe_tool_wrapper(*args, **kwargs):
                            try:
                                return await tool(*args, **kwargs)
                            except Exception as e:
                                logger.error(f"MCP Tool Execution Failed ({tool.name}): {e}")
                                return f"Error executing {tool.name}: {str(e)}"
                        
                        # Copy metadata
                        safe_tool_wrapper.__name__ = tool.name
                        safe_tool_wrapper.__doc__ = tool.description
                        if hasattr(tool, "input_schema"):
                            safe_tool_wrapper.input_schema = tool.input_schema
                        
                        safe_mcp_tools.append(safe_tool_wrapper)

                    tools.extend(safe_mcp_tools)
                except Exception as e:
                    logger.error(f"Smart Agent: Failed to fetch MCP tools: {e}")
                    traceback.print_exc() # FORCE PRINT TRACEBACK
                    # FALLBACK: Register "Error Tools" to prevent "Tool Not Found" and show error to user
                    is_auth_error = False
                    # Check outer string
                    if "401" in str(e) or "Unauthorized" in str(e):
                        is_auth_error = True
                    # Check cause (ExceptionGroup from TaskGroup)
                    elif hasattr(e, "__cause__") and e.__cause__:
                        if "401" in str(e.__cause__) or "Unauthorized" in str(e.__cause__):
                            is_auth_error = True
                        elif hasattr(e.__cause__, "exceptions"):
                            for inner in e.__cause__.exceptions:
                                if "401" in str(inner) or "Unauthorized" in str(inner):
                                    is_auth_error = True
                                    break

                    if is_auth_error:
                        err_msg = "Authentication Failed: Your FactSet session has expired. Please click 'Connect' to login again."
                    else:
                        err_msg = f"Connection Error: Unable to reach FactSet ({str(e)}). Please try again."
                    
                    def create_error_tool(tool_name):
                        def error_tool(*args, **kwargs):
                            """Returns a connection error message."""
                            return err_msg
                        error_tool.__name__ = tool_name
                        return error_tool

                    # Register key tools so the agent can "call" them and get the error
                    fallback_tools = [
                        create_error_tool("factset_global_prices"),
                        create_error_tool("factset_fundamentals"),
                        create_error_tool("factset_estimates"),
                        create_error_tool("factset_estimates_consensus"),
                        create_error_tool("factset_prices"),
                        # CamelCase Aliases for robustness against hallucination
                        create_error_tool("FactSet_GlobalPrices"),
                        create_error_tool("FactSet_Fundamentals"),
                        create_error_tool("FactSet_Estimates"),
                        create_error_tool("FactSet_EstimatesConsensus"),
                        create_error_tool("FactSet_Prices")
                    ]
                    print(f"!!! REGISTERING FALLBACK ERROR TOOLS: {[t.__name__ for t in fallback_tools]}", flush=True)
                    tools.extend(fallback_tools)
                    
                    # If this fails, we can either remove from cache or just proceed with basic tools
                    if token in GLOBAL_TOOLSET_CACHE: del GLOBAL_TOOLSET_CACHE[token]
            
        except Exception as e:
            logger.error(f"Failed to configure FactSet MCP: {e}")

    # SELF-HEALING: Ensure robustness by checking if key tools exist. If not, register error fallbacks.
    # This runs regardless of whether the try/except block succeeded or failed.
    current_tool_names = {t.name if hasattr(t, 'name') else t.__name__ for t in tools}
    
    needed_fallbacks = []
    
    def create_error_tool(tool_name):
        def error_tool(*args, **kwargs):
            """Returns a connection error message."""
            return "Connection Error: Unable to reach FactSet live data. Please try again later."
        error_tool.__name__ = tool_name
        return error_tool

    # List of critical tools (snake_case and CamelCase aliases)
    critical_tools = [
        "factset_global_prices", "FactSet_GlobalPrices",
        "factset_fundamentals", "FactSet_Fundamentals",
        "factset_estimates", "FactSet_Estimates"
    ]

    for t_name in critical_tools:
        if t_name not in current_tool_names:
            print(f"!!! MISSING TOOL {t_name}, ADDING FALLBACK.", flush=True)
            needed_fallbacks.append(create_error_tool(t_name))
            
    if needed_fallbacks:
        tools.extend(needed_fallbacks)
            
    # Mock Mode Fallback (for testing without token or explicit mock)
    # We enable this if token is None or "mock" to ensure the agent ALWAYS has tools to satisfy its instructions.
    if not token or "mock" in token:
        logger.info("Smart Agent: Enabling MOCK tools (No valid FactSet token provided)")
        
        def FactSet_Prices(ticker: str):
             """
             Returns the real-time stock price.
             Use this for current price queries.
             """
             return {"ticker": ticker, "price": 150.00, "currency": "USD", "time": get_current_datetime()}

        def FactSet_GlobalPrices(ticker: str, startDate: str = None, endDate: str = None, frequency: str = "D"):
             """
             Fetches historical stock prices.
             REQUIRED for charts.
             """
             return {
                 "ticker": ticker,
                 "history": [
                     {"date": "2024-12-01", "close": 140.0},
                     {"date": "2025-01-01", "close": 145.0},
                     {"date": "2025-01-21", "close": 150.0}
                 ]
             }

        def FactSet_Fundamentals(ticker: str):
             """
             Fetches fundamental metrics (Sales, EPS).
             """
             return {
                 "ticker": ticker, 
                 "metrics": {"sales": 50000, "eps": 4.50},
                 "note": "Mock Data"
             }

        # Alias for hallucination resistance
        get_factset_prices = FactSet_Prices
        tools.extend([FactSet_Prices, FactSet_GlobalPrices, FactSet_Fundamentals, get_factset_prices])
        logger.info(f"Smart Agent: Tools registered: {[t.__name__ for t in tools]}")

    return Agent(
        name="factset_analyst", 
        model=model_name,
        instruction=SMART_INSTRUCTIONS,
        tools=tools
    )
