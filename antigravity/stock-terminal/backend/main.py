import os
import json
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()
import yfinance as yf
import requests
import base64
from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator

import google.adk as adk
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv

# Import the new FactSet Agent factory
# Import the new FactSet Agent factory
from factset_agent import create_factset_agent, google_search, perform_google_search

load_dotenv()

# Setup ADK components
session_service = InMemorySessionService()

# Token Persistence
TOKEN_FILE = "factset_tokens.json"

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tokens(tokens):
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)
    except Exception as e:
        print(f"Error saving tokens: {e}")

factset_tokens = load_tokens() 

# FactSet Config
FS_CLIENT_ID = os.getenv("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET")
FS_REDIRECT_URI = os.getenv("FS_REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")
FS_AUTH_URL = "https://auth.factset.com/as/authorization.oauth2"
FS_TOKEN_URL = "https://auth.factset.com/as/token.oauth2"

def get_stock_snapshot(symbol: str) -> dict:
    """
    Fetches a full snapshot of stock data including info, history, and key stats.
    """
    try:
        # Normalize symbol (remove -US if present for yfinance)
        yf_symbol = symbol.split('-')[0]
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        
        if not info or len(info) < 5:
            # Try again with the full symbol
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
        if not info or len(info) < 5:
            return {"error": f"Ticker '{symbol}' not found or no data available."}

        # Get recent history
        hist = ticker.history(period="1mo")
        history_data = []
        if not hist.empty:
            hist = hist.reset_index()
            for _, row in hist.iterrows():
                history_data.append({
                    "date": row['Date'].strftime('%Y-%m-%d'),
                    "close": round(float(row['Close']), 2)
                })

        return {
            "symbol": symbol.upper(),
            "name": info.get('longName', symbol.upper()),
            "price": info.get('currentPrice', info.get('regularMarketPrice', info.get('previousClose', 0))),
            "change": info.get('regularMarketChangePercent', 0),
            "currency": info.get('currency', 'USD'),
            "marketCap": info.get('marketCap'),
            "peRatio": info.get('trailingPE'),
            "dividendYield": info.get('dividendYield'),
            "summary": info.get('longBusinessSummary', 'No summary available.'),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh'),
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow'),
            "history": history_data,
            "lastUpdated": __import__('time').time()
        }
    except Exception as e:
        print(f"Error fetching yfinance data for {symbol}: {e}")
        return {"error": str(e)}

def create_summary_agent(model_name: str = "gemini-2.0-flash-exp"):
    return Agent(
        name="terminal_summarizer",
        model=model_name,
        instruction="""
        You are a financial news and dashboard summarizer.
        You will receive a JSON object representing the current state of a stock terminal dashboard.
        Your goal is to provide a concise, professional summary of the key findings.
        """
    )

# --- AGENT INSTRUCTIONS ---

CHAT_INSTRUCTIONS = """
You are a helpful financial assistant inside a stock terminal.
You are a helpful assistant for the FactSet Stock Terminal.
You are currently in UNAUTHENTICATED DEMO MODE.

Your Goals:
1. Help users with general knowledge (e.g. "Who is CEO of Apple?", "What does Nvidia do?").
2. DRIVE ADOPTION of FactSet for real-time data.

RULES OF ENGAGEMENT:
- **STRICTLY FORBIDDEN**: Do NOT search for or provide financial numbers (Price, Revenue, EPS, Rates, P/E, etc).
- **IF ASKED FOR NUMBERS**: You must DECLINE and say: "I cannot provide real-time financial numbers. Please Connect to FactSet."
- DO NOT HALLUCINATE or use training data for prices.
- For general questions (people, news, definitions), use 'perform_general_search_only'.
"""

# Note: We'll retrieve FACTSET_INSTRUCTIONS directly from factset_agent if possible, 
# or just define it here if we want to centralize. 
# For now, let's just use these constants.

def get_current_time() -> str:
    """Returns the current central date and time in ISO format. Use this to determine 'today', 'yesterday', or relative dates."""
    import datetime
    return datetime.datetime.now().isoformat()


# --- TOPOLOGY HELPER ---
def generate_topology(agent):
    """
    Recursively generates a topology dict {nodes, edges} from an Agent structure.
    """
    nodes = []
    edges = []
    
    def traverse(current_agent, parent_id=None):
        agent_id = getattr(current_agent, 'name', 'unknown_agent')
        
        # 1. Create Agent Node
        node = {
            "id": agent_id,
            "type": "agent", 
            "data": {
                "label": agent_id,
                "type": getattr(current_agent, 'agent_type', 'Agent') if hasattr(current_agent, 'agent_type') else current_agent.__class__.__name__,
                # "tools": [] # Tools are now separate nodes
            }
        }
        
        # Check if node already exists to avoid dupes
        if not any(n['id'] == agent_id for n in nodes):
            nodes.append(node)
        
        if parent_id:
            edges.append({
                "id": f"{parent_id}-{agent_id}",
                "source": parent_id,
                "target": agent_id,
                "type": "smoothstep"
            })
            
        # 2. Create Tool Nodes & Edges
        if hasattr(current_agent, 'tools') and current_agent.tools:
            for t in current_agent.tools:
                tool_name = getattr(t, 'name', None) or getattr(t, '__name__', None)
                if not tool_name:
                    # Fallback to class name if available, otherwise substring of repr
                    if hasattr(t, '__class__'):
                        tool_name = t.__class__.__name__
                        if tool_name == 'McpToolset':
                            # Special case for McpToolset to be more descriptive if possible, or just keep it short
                            tool_name = "FactSet_MCP" 
                # Use specific name for McpToolset to be readable
                raw_name = getattr(t, 'name', None) or getattr(t, '__name__', None)
                
                # Special handling for FactSet/MCP tools which might have complex repr
                if t.__class__.__name__ == 'McpToolset':
                    tool_name = "FactSet_MCP"
                elif raw_name:
                    tool_name = raw_name
                else:
                    tool_name = str(t)[:20] + "..." if len(str(t)) > 20 else str(t)

                tool_node_id = f"{agent_id}_{tool_name}"
                
                nodes.append({
                    "id": tool_node_id,
                    "type": "tool",
                    "data": {"label": tool_name, "parentAgent": agent_id}
                })
                edges.append({
                    "id": f"e_{agent_id}_{tool_node_id}",
                    "source": agent_id,
                    "target": tool_node_id,
                    "animated": True,
                    "style": {"strokeDasharray": "5,5"}
                })

        # Recurse for sub_agents
        if hasattr(current_agent, 'sub_agents') and current_agent.sub_agents:
            for sub in current_agent.sub_agents:
                traverse(sub, agent_id)
                
    traverse(agent)
    return {"nodes": nodes, "edges": edges}



async def perform_general_search_only(query: str) -> str:
    """
    Search for general news, events, or non-financial information.
    
    CRITICAL: DO NOT USE THIS FOR FINANCIAL NUMBERS (Revenue, EPS, Prices).
    If the user asks for financial numbers and is not connected to FactSet,
    you MUST DECLINE and ask them to connect.
    """
    # Hard guardrail for financial terms
    forbidden_terms = [
        "revenue", "price", "stock", "eps", "earnings", "profit", 
        "margin", "valuation", "market cap", "dividend", "financial"
    ]
    q_lower = query.lower()
    if any(term in q_lower for term in forbidden_terms):
        return (
            "ACTION_BLOCKED: Searching for financial data (Price, Revenue, EPS, etc.) "
            "is NOT ALLOWED in Demo Mode. You must tell the user to 'Connect to FactSet' "
            "to see this data."
        )

    return await perform_google_search(query)

def create_chat_agent(model_name: str = "gemini-2.5-flash"):
    """
    Creates the default 'Chat' agent (unauthenticated).
    """
    return Agent(
        model=model_name,
        name="StockTerminal_Chat",
        instruction=CHAT_INSTRUCTIONS,
        tools=[get_current_time, perform_general_search_only],
        # server=None 

    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryRequest(BaseModel):
    dashboard_data: dict
    session_id: str = "default"
    model: str = "gemini-2.5-flash"

class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None  # Base64 encoded image
    video_url: Optional[str] = None
    session_id: str = "default_chat"
    model: str = "gemini-2.5-flash"

class AuthCallbackRequest(BaseModel):
    redirect_url: str
    session_id: str = "default_chat"

# --- AUTH ENDPOINTS ---

@app.get("/auth/factset/url")
def get_factset_auth_url():
    """Returns the URL for the user to authenticate with FactSet."""
    params = {
        "response_type": "code",
        "client_id": FS_CLIENT_ID,
        "redirect_uri": FS_REDIRECT_URI,
        "scope": "mcp",
        "state": "stock_terminal_auth"
    }
    auth_url = requests.Request('GET', FS_AUTH_URL, params=params).prepare().url
    return {"auth_url": auth_url}

@app.post("/auth/factset/callback")
def factset_callback(req: AuthCallbackRequest):
    """Exchanges the redirect URL code for an access token."""
    url = req.redirect_url
    print(f"Receiving callback URL: {url}")

    # Extract Code
    try:
        if "code=" in url:
            parsed = urlparse(url)
            code = parse_qs(parsed.query).get('code', [None])[0]
        else:
            # Maybe the user pasted just the code?
            code = url if not url.startswith("http") else None
        
        if not code:
            raise HTTPException(status_code=400, detail="Could not extract authorization code from URL.")

        # Exchange for Token
        auth_str = f"{FS_CLIENT_ID}:{FS_CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": FS_REDIRECT_URI
        }

        response = requests.post(FS_TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            # Store token with timestamp
            factset_tokens[req.session_id] = {
                "token": access_token,
                "created_at": time.time()
            }
            save_tokens(factset_tokens)
            return {"status": "success", "message": "FactSet Connected successfully!"}
        else:
            print(f"Token Exchange Failed: {response.text}")
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")

    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/factset/status")
def get_factset_status(session_id: str = "default_chat"):
    data = factset_tokens.get(session_id)
    if not data:
        return {"connected": False}
    
    # Handle both legacy (string) and new (dict) formats
    token = None
    created_at = None
    
    if isinstance(data, dict):
        token = data.get("token")
        created_at = data.get("created_at")
    else:
        token = data
        
    # Validate token validity
    try:
        from factset_agent import validate_token
        validate_token(token)
    except Exception as e:
        print(f"Token validation failed for session {session_id}: {e}")
        # Invalid token, remove it
        factset_tokens.pop(session_id, None)
        save_tokens(factset_tokens)
        return {"connected": False}

    return {
        "connected": True, 
        "created_at": created_at,
        "expires_in": 900 - (time.time() - (created_at or time.time())) # 15 min = 900s
    }

@app.get("/agent-config")
def get_agent_config():
    from factset_agent import FACTSET_INSTRUCTIONS
    
    def clean(s):
        return "\n".join([line.strip() for line in s.strip().split("\n")])

    return {
        "standard_agent": {
            "name": "terminal_assistant",
            "instruction": clean(CHAT_INSTRUCTIONS),
            "tools": [
                {"name": "get_current_time", "description": "Returns the current central date and time in ISO format."},
                {"name": "perform_google_search", "description": "Performs a google search using a sub-agent."}
            ]
        },
        "factset_agent": {
            "name": "factset_analyst",
            "instruction": clean(FACTSET_INSTRUCTIONS),
            "tools": [
                {"name": "FactSet MCP Toolset", "description": "Global prices, company snapshots, estimates, and more via FactSet API."},
                {"name": "get_current_time", "description": "Returns the current central date and time in ISO format."},
                {"name": "perform_google_search", "description": "Performs a google search using a sub-agent."}
            ]
        }
    }

# --- MAIN ENDPOINTS ---

@app.get("/ticker-info/{ticker}")
async def get_ticker_info(ticker: str):
    data = await asyncio.to_thread(get_stock_snapshot, ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.post("/summarize")
async def summarize(req: SummaryRequest):
    agent = create_summary_agent(model_name=req.model)
    runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)

    prompt = f"Please summarize the following dashboard data:\n{json.dumps(req.dashboard_data, indent=2)}"
    new_message = Content(parts=[Part(text=prompt)])

    session = await session_service.get_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")
    if not session:
        await session_service.create_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")

    responses = []
    try:
        async for event in runner.run_async(user_id="user_1", session_id=req.session_id, new_message=new_message):
            if event.content and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if part.text:
                        responses.append(part.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"summary": "".join(responses)}

from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(req: ChatRequest):
    # Simulation hook for verification
    if req.message == "SIMULATE_AUTH_ERROR":
        raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")

    try:
        # Check if we have a FactSet token for this session
        token_data = factset_tokens.get(req.session_id)
        factset_token = None
        
        if token_data:
            if isinstance(token_data, dict):
                factset_token = token_data.get("token")
            else:
                factset_token = token_data
        agent = None
        
        if factset_token:
            print(f"DEBUG: Analyzing query for parallelism: {req.message}")
            try:
                # 1. Router Step: Check for multiple tickers
                # We do this with a lightweight call or regex. For simplicity and robustness, let's use a quick LLM check.
                # Note: In a PROD environment, we might want to optimize this latency.
                
                # Check if we should use Parallel execution
                # We will define a quick router if we suspect multiple tickers
                # Simple heuristic: "compare" or multiple commas/concepts
                
                is_multi_stock = False
                tickers = []
                
                # Basic Heuristic to save 1 LLM call:
                if "compare" in req.message.lower() or "," in req.message or "vs" in req.message.lower():
                    print(f"DEBUG: Intent looks like multi-stock comparison. Running Router...")
                    
                    # 1. Router Step: Extract tickers using a lightweight agent
                    router_instruction = """
                    Extract stock tickers or company names from the user query.
                    Map company names to their most common US tickers (e.g. "Apple" -> "AAPL-US", "Microsoft" -> "MSFT-US").
                    Return ONLY a JSON list of strings, e.g. ["AAPL-US", "MSFT-US"].
                    If one or none, return empty list [].
                    """
                    
                    try:
                        # Quick synchronous call using the same model
                        import google.genai as genai
                        # We use the ADK's model wrapper or just standard genai if available, 
                        # but ADK Agent is easier. However, we need to run it.
                        # Since we are inside an async function, we can run a quick agent?
                        # Actually, creating an Agent and running it is heavy. 
                        # Let's just use the regex improvement as a fallback for speed, 
                        # BUT the user wants "creative queries".
                        # Let's use a smarter regex that allows longer names, and then map them?
                        # Or just pass the NAMES to the worker agent and let IT figure out the ticker?
                        
                        # Let's improve the Regex to allow proper names and use that.
                        # Using an LLM router adds latency.
                        
                        import re
                        # Match words that start with capital letter, length 3-15 (e.g. Apple, Microsoft)
                        # OR all caps tickers.
                        potential_words = re.findall(r'\b[A-Z][a-zA-Z0-9-]{2,15}\b', req.message)
                        
                        COMMON_WORDS = {
                            'The', 'And', 'For', 'Are', 'Was', 'Who', 'How', 'Why', 'Yes', 'Not', 'Now', 'But', 
                            'Get', 'Set', 'Hey', 'Can', 'Use', 'See', 'Did', 'New', 'Big', 'Out', 'Top', 'Low', 
                            'Buy', 'Put', 'Call', 'Chart', 'Data', 'Show', 'Compare', 'Please', 'Visualise', 'Visualize',
                            'Historic', 'History', 'Figures', 'Last', 'Years', 'Months', 'Days', 'Figures'
                        }
                        
                        tickers = [w for w in potential_words if w.upper() not in [cw.upper() for cw in COMMON_WORDS]]
                        
                        # De-duplicate
                        tickers = list(set(tickers))
                        
                        if len(tickers) >= 2:
                            print(f"DEBUG: Detected Multi-Stock Parallel Intent: {tickers}")
                            from google.adk.agents import ParallelAgent, SequentialAgent
                            
                            # Limit to 3 to avoid rate limits
                            target_tickers = tickers[:3]
                            
                            parallel_workers = []
                            for t in target_tickers:
                                # Specialized Instruction
                                worker_instruction = f"""
                                You are a specialized worker fetching data for: {t}.
                                You have access to FactSet tools.
                                1. Search for the ticker symbol for "{t}" if needed (guess it if obvious like 'Apple' -> 'AAPL-US').
                                2. Use `FactSet_GlobalPrices` to get its history.
                                3. Return the data clearly.
                                """
                                worker = create_factset_agent(token=factset_token, model_name=req.model, instruction_override=worker_instruction)
                                worker.name = f"fetcher_{t}"
                                parallel_workers.append(worker)
                                
                            parallel_agent = ParallelAgent(
                                name="multi_stock_fetcher",
                                sub_agents=parallel_workers
                            )
                            
                            # We need a summarizer 
                            summarizer = create_factset_agent(token=factset_token, model_name=req.model)
                            summarizer.name = "summary_analyst"
                            from factset_agent import FACTSET_INSTRUCTIONS
                            summarizer.instruction = FACTSET_INSTRUCTIONS + "\n\nCONTEXT: You are summarizing data fetched by parallel workers. The chart has been updated by them. Explain the comparison."
                            
                            agent = SequentialAgent(
                                name="parallel_stock_workflow",
                                sub_agents=[parallel_agent, summarizer]
                            )
                        else:
                             # Fallback to single agent if regex failed to find >1
                             agent = create_factset_agent(token=factset_token, model_name=req.model)

                    except Exception as e:
                        print(f"DEBUG: Router failed: {e}. Falling back to standard.")
                        agent = create_factset_agent(token=factset_token, model_name=req.model)
                else:
                    # Standard Single Agent if no "compare" keyword
                    agent = create_factset_agent(token=factset_token, model_name=req.model)

        
            except Exception as e:
                print(f"DEBUG: Router block failed: {e}")
        
        if not agent:
             print(f"DEBUG: Using Standard Chat Agent for session {req.session_id}")
             agent = create_chat_agent(model_name=req.model)
        
        print(f"DEBUG: FINAL AGENT: {agent.name}")
        # Safe debug logging for agent tools
        req_tools = getattr(agent, 'tools', [])
        if req_tools:
            tool_names = [getattr(t, 'name', str(t)) for t in req_tools]
            print(f"DEBUG: FINAL TOOLS: {tool_names}")
        else:
            print(f"DEBUG: FINAL TOOLS: [] (Composite Agent or No Tools)")

        runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)
    
    except ValueError as e:
        # Handle initialization errors (like invalid tokens) gracefully
        error_msg = str(e)
        async def error_generator():
            yield json.dumps({"type": "error", "content": error_msg}) + "\n"
        return StreamingResponse(error_generator(), media_type="application/x-ndjson")
    except Exception as e:
        error_msg = str(e)
        async def error_generator():
            yield json.dumps({"type": "error", "content": f"Initialization failed: {error_msg}"}) + "\n"
        return StreamingResponse(error_generator(), media_type="application/x-ndjson")

    parts = [Part(text=req.message)]
    if req.image:
        try:
            # Assuming format: "data:image/png;base64,..."
            if "," in req.image:
                header, data = req.image.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
            else:
                data = req.image
                mime_type = "image/png" # Default

            parts.append(Part.from_bytes(
                data=base64.b64decode(data),
                mime_type=mime_type
            ))
        except Exception as e:
            print(f"Error decoding image: {e}")
            # Optionally stop if image is mandatory, but here we'll just log

    if req.video_url:
        try:
            parts.append(Part.from_uri(
                file_uri=req.video_url,
                mime_type="video/*"
            ))
        except Exception as e:
            print(f"Error adding video URL: {e}")

    new_message = Content(parts=parts)

    session = await session_service.get_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")
    if not session:
        await session_service.create_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")
        session = await session_service.get_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")

    # --- HISTORY TRUNCATION (Fix for 1M Token Limit) ---
    # Check if session history is getting too long. 
    # ADK Session history is typically a list of Content objects.
    # We want to preserve the System Prompt (usually distinct or first) but truncate the middle.
    MAX_HISTORY = 15
    if hasattr(session, 'history') and len(session.history) > MAX_HISTORY:
        print(f"DEBUG: Truncating session history from {len(session.history)} to {MAX_HISTORY}")
        # Keep the most recent messages. ADK usually handles system instruction separately via Agent definition.
        # So we can safely just slice the history.
        session.history = session.history[-MAX_HISTORY:]

    async def event_generator():
        # 1. Emit Topology Event IMMEDIATELY
        if agent:
            try:
                topology = generate_topology(agent)
                print(f"DEBUG: Emitting topology: {len(topology['nodes'])} nodes")
                yield json.dumps({"type": "topology", "data": topology}) + "\n"
            except Exception as e:
                print(f"Error generating topology: {e}")

        tool_start_times = {}
        try:
            async for event in runner.run_async(user_id="user_1", session_id=req.session_id, new_message=new_message):
                if hasattr(event, "step") and event.step: pass
                if event.content and hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if part.text:
                            yield json.dumps({"type": "text", "content": part.text}) + "\n"
                        if hasattr(part, "function_call") and part.function_call:
                            call = part.function_call
                            tool_start_times[call.name] = time.time()
                            yield json.dumps({"type": "tool_call", "tool": call.name, "args": call.args}) + "\n"
                        if hasattr(part, "function_response") and part.function_response:
                            resp = part.function_response
                            duration = 0
                            if resp.name in tool_start_times:
                                duration = time.time() - tool_start_times.pop(resp.name)
                            result_content = resp.response

                            # PATCH: Fix double-serialization of dicts as Python strings (single quotes)
                            # This happens when ADK or MCP returns a stringified dict
                            if isinstance(result_content, str):
                                stripped = result_content.strip()
                                if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                                    try:
                                        import ast
                                        # Try to parse as valid structure
                                        try:
                                            result_content = json.loads(result_content)
                                        except:
                                            result_content = ast.literal_eval(result_content)
                                    except:
                                        pass
                            
                            # Ensure result is serializable; if not, fall back to string
                            if not isinstance(result_content, (dict, list, str, int, float, bool, type(None))):
                                result_content = str(result_content)
                            
                            yield json.dumps({"type": "tool_result", "tool": resp.name, "result": result_content, "duration": duration}) + "\n"
                
                if hasattr(event, "usage_metadata") and event.usage_metadata:
                    yield json.dumps({"type": "usage", "prompt_tokens": event.usage_metadata.prompt_token_count, "candidates_tokens": event.usage_metadata.candidates_token_count, "total_tokens": event.usage_metadata.total_token_count}) + "\n"

        except Exception as e:
            print(f"Chat error: {e}")
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            
            # Recursive function to find the root cause
            def get_root_cause(exc):
                # Check for our specific ValueError from factset_agent.py
                if "FactSet authentication token expired" in str(exc):
                    return str(exc)
                
                # Check for HTTPStatusError (401)
                if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
                    if exc.response.status_code in (401, 403):
                        return "FactSet authentication token expired or invalid. Please reconnect."

                # Unwrap ExceptionGroups (anyio)
                if hasattr(exc, "exceptions") and exc.exceptions:
                    for sub_exc in exc.exceptions:
                        found = get_root_cause(sub_exc)
                        if found: return found
                
                # Unwrap direct causes (chained exceptions)
                if exc.__cause__:
                    found = get_root_cause(exc.__cause__)
                    if found: return found
                    
                return None

            root_msg = get_root_cause(e)
            if root_msg:
                error_msg = root_msg
            elif hasattr(e, "exceptions") and e.exceptions:
                 # Fallback for generic ExceptionGroup
                error_msg = str(e.exceptions[0])

            yield json.dumps({"type": "error", "content": error_msg}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
