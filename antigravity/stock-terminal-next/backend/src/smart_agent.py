from src import factset_core # Apply patches immediately (Must be FIRST)
from src.factset_core import check_factset_health, GLOBAL_TOOLSET_CACHE
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
        result = await simple_factset_agent.google_search(query)
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
        
        return f"[PDF ANALYSIS of {url}]\n{response.text}"

    except Exception as e:
        logger.error(f"PDF Analysis failed: {e}")
        return f"Error analyzing PDF: {str(e)}"

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

async def create_smart_agent(token: str, model_name: str = "gemini-3-flash-preview") -> Agent:
    """
    Creates a Context-Aware Smart Agent using Gemini 3.0.
    """
    tools = [get_current_datetime, google_search, plot_financial_data, analyze_pdf_url]
    
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
                        async def safe_tool_wrapper(*args, **kwargs):
                            try:
                                return await tool(*args, **kwargs)
                            except Exception as e:
                                logger.error(f"MCP Tool Execution Failed ({tool.name}): {e}")
                                return f"Error executing {tool.name}: {str(e)}"
                        
                        safe_tool_wrapper.__name__ = tool.name
                        safe_tool_wrapper.__doc__ = tool.description
                        if hasattr(tool, "input_schema"):
                            safe_tool_wrapper.input_schema = tool.input_schema
                        
                        safe_mcp_tools.append(safe_tool_wrapper)

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

                    fallback_tools = [
                        create_error_tool("factset_global_prices"),
                        create_error_tool("factset_fundamentals"),
                        create_error_tool("factset_estimates"),
                        create_error_tool("FactSet_Prices")
                    ]
                    tools.extend(fallback_tools)
                    if token in GLOBAL_TOOLSET_CACHE: del GLOBAL_TOOLSET_CACHE[token]
            
        except Exception as e:
            logger.error(f"Failed to configure FactSet MCP: {e}")

    # Mock Mode Fallback
    if not token or "mock" in token:
        logger.info("Smart Agent: Enabling MOCK tools")
        def FactSet_Prices(ticker: str): return {"ticker": ticker, "price": 150.0, "currency": "USD", "time": get_current_datetime()}
        def FactSet_GlobalPrices(ticker: str, startDate: str = None, endDate: str = None, frequency: str = "D"):
             return {"ticker": ticker, "history": [{"date": "2025-01-21", "close": 150.0}, {"date": "2025-01-22", "close": 152.0}]}
        
        tools.extend([FactSet_Prices, FactSet_GlobalPrices])

    return Agent(
        name="factset_analyst", 
        model=model_name,
        instruction=SMART_INSTRUCTIONS,
        tools=tools
    )
