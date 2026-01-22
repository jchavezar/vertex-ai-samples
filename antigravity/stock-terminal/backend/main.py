import os
import json
import asyncio
import time
import secrets
import traceback
import re
from dotenv import load_dotenv

load_dotenv()
import yfinance as yf
import requests
import base64
from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator, Dict, Any
import google.auth
from google.auth.transport.requests import Request

import google.adk as adk
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import httpx

# Import the new FactSet Agent factory
from factset_agent import create_factset_agent, google_search, perform_google_search, FACTSET_INSTRUCTIONS
from report_agent import create_report_orchestrator

# Setup ADK components
session_service = InMemorySessionService()

# Token Persistence
TOKEN_FILE = "factset_tokens.json"
factset_tokens = {} # Initialize global
_cached_tokens = None # In-memory cache

def load_tokens():
    """Loads tokens from disk or memory cache."""
    global _cached_tokens
    if _cached_tokens is not None:
        return _cached_tokens
        
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                _cached_tokens = json.load(f)
                return _cached_tokens
        except:
            pass
    _cached_tokens = {}
    return _cached_tokens

def save_tokens(tokens):
    """Saves tokens to disk and updates memory cache."""
    global _cached_tokens
    _cached_tokens = tokens
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)
    except Exception as e:
        print(f"Error saving tokens: {e}")

def handle_simple_greeting(message: str) -> bool:
    """Detects if a message is a simple greeting that doesn't need data tools."""
    greetings = {"hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening", "hi bro", "hey bro", "what's up", "how are you", "how are you doing", "how's it going", "how is it going", "hey how are you man"}
    msg = message.lower().strip().strip("!").strip(".").strip("?")
    return msg in greetings

async def refresh_factset_token(session_id: str):
    """Refreshes the FactSet token using the stored refresh_token."""
    data = factset_tokens.get(session_id)
    if not data or "refresh_token" not in data:
        return None

    print(f"Refreshing FactSet token for session: {session_id}")
    
    auth_str = f"{FS_CLIENT_ID}:{FS_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": data["refresh_token"]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(FS_TOKEN_URL, data=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                new_tokens = response.json()
                access_token = new_tokens.get("access_token")
                refresh_token = new_tokens.get("refresh_token") or data["refresh_token"]
                expires_in = new_tokens.get("expires_in", 900)
                
                factset_tokens[session_id] = {
                    "token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": time.time() + expires_in,
                    "created_at": time.time()
                }
                save_tokens(factset_tokens)
                print(f"Successfully refreshed token for {session_id}")
                return access_token
            else:
                print(f"Token Refresh Failed for {session_id}: {response.text}")
                return None
    except Exception as e:
        print(f"Error refreshing token for {session_id}: {e}")
        return None

async def get_valid_factset_token(session_id: str):
    # Fast in-memory check first
    global factset_tokens
    data = factset_tokens.get(session_id)
    
    if not data:
        # Avoid redundant disk I/O if possible
        factset_tokens = load_tokens()
        data = factset_tokens.get(session_id)
        if not data:
            return None

    token = data.get("token")
    expires_at = data.get("expires_at", 0)
    
    # Refresh if expired or expiring in the next 5 minutes
    if not expires_at or time.time() > (expires_at - 300):
        if data.get("refresh_token") and data["refresh_token"] != "pending":
            start_refresh = time.time()
            refreshed = await refresh_factset_token(session_id)
            print(f"DEBUG: get_valid_factset_token (REFRESH) took {time.time() - start_refresh:.4f}s")
            return refreshed
        else:
            print(f"Token for {session_id} is expired or invalid, and no refresh_token is available.")
            if expires_at and time.time() > expires_at:
                return None
            
    return token

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

def create_summary_agent(model_name: str = "gemini-2.5-flash-lite"):
    return Agent(
        name="terminal_summarizer",
        model=model_name,
        instruction="""
        You are a financial news and dashboard summarizer.
        You will receive a JSON object representing the current state of a stock terminal dashboard.
        Your goal is to provide a concise, professional summary of the key findings.
        """
    )

# --- VERTEX AI SEARCH CLIENT ---
PROJECT_ID = os.getenv("VAIS_PROJECT_ID", "254356041555")
LOCATION = os.getenv("VAIS_LOCATION", "global")
COLLECTION = os.getenv("VAIS_COLLECTION", "default_collection")
ENGINE = os.getenv("VAIS_ENGINE", "factset")
SERVING_CONFIG = os.getenv("VAIS_SERVING_CONFIG", "default_search")
VAIS_API_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE}/servingConfigs/{SERVING_CONFIG}:search"

class VertexSearchClient:
    def __init__(self):
        self.credentials, self.project = google.auth.default()
        self._token = None
        self._token_expiry = 0
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_token(self) -> str:
        now = time.time()
        if not self._token or not self.credentials.valid or now > self._token_expiry:
            print("[VAIS] Refreshing Google Auth Token (Async Thread)...")
            t0 = time.time()
            import anyio
            await anyio.to_thread.run_sync(self.credentials.refresh, Request())
            self._token = self.credentials.token
            self._token_expiry = now + 3000 # 50 min buffer
            print(f"[VAIS] Token refresh took {time.time() - t0:.4f}s")
        return self._token

    async def search(self, query: str, page_size: int = 10, offset: int = 0) -> Dict[str, Any]:
        token = await self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "pageSize": page_size,
            "offset": offset,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "userInfo": {"timeZone": "UTC"}
        }

        t0 = time.time()
        try:
            response = await self._client.post(VAIS_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            print(f"[VAIS] Search for '{query}' took {time.time() - t0:.4f}s")
            return response.json()
        except Exception as e:
            print(f"[VAIS] Search Failed after {time.time() - t0:.4f}s: {e}")
            raise

vais_client = VertexSearchClient()

class SearchRequest(BaseModel):
    query: str
    pageSize: Optional[int] = 10
    offset: Optional[int] = 0



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
    
    def find_model(a):
        if hasattr(a, 'model') and a.model:
            return a.model
        if hasattr(a, 'sub_agents') and a.sub_agents:
            # Try to find model in first sub-agent
            for sub in a.sub_agents:
                m = find_model(sub)
                if m: return m
        return 'default'

    def traverse(current_agent, parent_id=None):
        agent_id = getattr(current_agent, 'name', 'unknown_agent')
        
        # 1. Create Agent Node
        node = {
            "id": agent_id,
            "type": "agent", 
            "data": {
                "label": agent_id,
                "type": getattr(current_agent, 'agent_type', 'Agent') if hasattr(current_agent, 'agent_type') else current_agent.__class__.__name__,
                "model": find_model(current_agent)
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
                    # Expand known FactSet tools for visualization so they can be highlighted
                    fs_tools = [
                        "FactSet_GlobalPrices", "FactSet_Fundamentals", "FactSet_EstimatesConsensus",
                        "FactSet_People", "FactSet_Ownership", "FactSet_SupplyChain",
                        "FactSet_MergersAcquisitions", "FactSet_GeoRev", "FactSet_CalendarEvents", "FactSet_Metrics"
                    ]
                    for fst in fs_tools:
                        fst_node_id = f"{agent_id}_{fst}"
                        nodes.append({
                            "id": fst_node_id,
                            "type": "tool",
                            "data": {
                                "label": fst, 
                                "parentAgent": agent_id,
                                "description": "FactSet Financial Data Tool"
                            }
                        })
                        edges.append({
                            "id": f"e_{agent_id}_{fst_node_id}",
                            "source": agent_id,
                            "target": fst_node_id,
                            "animated": True,
                            "style": {"strokeDasharray": "5,5"}
                        })
                    continue # Skip generic node

                elif raw_name:
                    tool_name = raw_name
                else:
                    tool_name = str(t)[:20] + "..." if len(str(t)) > 20 else str(t)

                tool_node_id = f"{agent_id}_{tool_name}"
                
                # Fetch description if available
                description = ""
                if hasattr(t, 'description') and t.description:
                    description = t.description
                elif hasattr(t, '__doc__') and t.__doc__:
                    description = t.__doc__.strip()
                elif hasattr(t, 'func') and hasattr(t.func, '__doc__') and t.func.__doc__:
                    description = t.func.__doc__.strip()

                nodes.append({
                    "id": tool_node_id,
                    "type": "tool",
                    "data": {
                        "label": tool_name, 
                        "parentAgent": agent_id,
                        "description": description
                    }
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
    return Agent(
        model=model_name,
        name="terminal_assistant",
        instruction=CHAT_INSTRUCTIONS,
        tools=[get_current_time, perform_google_search],
    )

def create_data_analyst_agent(token: str, model_name: str = "gemini-2.5-flash", ticker: str = None, section: str = "Financial") -> Agent:
    """Specialized worker for high-speed financial data extraction for widgets."""
    from factset_agent import create_factset_agent
    instruction = (
        f"You are a high-speed Data Analyst worker for: {ticker or 'the requested company'}.\n"
        f"Your task is to fetch specific {section} data points from FactSet to populate a dashboard widget.\n"
        "INSTRUCTIONS:\n"
        f"1. Focus ONLY on {section} metrics.\n"
        "2. FORMAT: Start with a 1-2 sentence high-level summary paragraph. Then provide a detailed Markdown Table with the raw data.\n"
        "3. CRITICAL: If fetching PRICES via GlobalPrices, you MUST fetch a HISTORY (e.g., last 30 days). "
        "Example: if today is 2025-01-17, set 'startDate' to '2024-12-17' and 'endDate' to '2025-01-17'. "
        "Do NOT set them to the same day. This is REQUIRED for charts to work.\n"
        f"4. RETURN data specifically for {ticker}. Provide raw numbers for tool calls, but summarize the findings in text.\n"
        "5. **INTELLIGENT FALLBACK**: If a tool returns NO DATA for a requested date, PROACTIVELY try to find the last available value by widening the date range (e.g. look back 7 days). Explain to the user: 'I don't have data for [Date], but the last available value is [Value] from [Last Date].'"
    )
    agent = create_factset_agent(
        token=token,
        model_name=model_name,
        instruction_override=instruction,
        include_native_tools=True # Allow get_current_time for date logic
    )
    if ticker:
        agent.name = f"analyst_{ticker.replace('-US', '').replace(' ', '_')}"
    return agent

def create_parallel_data_analyst_workflow(token: str, tickers: list, section: str, model_name: str = "gemini-3-flash-preview") -> Agent:
    """Creates a parallel workflow where multiple analysts fetch data simultaneously."""
    workers = [create_data_analyst_agent(token, model_name, t, section) for t in tickers]
    
    sanitized_section = section.replace(" ", "_").replace("-", "_")
    parallel_agent = ParallelAgent(
        name=f"parallel_{sanitized_section}_fetcher",
        sub_agents=workers
    )
    
    aggregator_instruction = (
        f"Synthesize the financial data for {', '.join(tickers)} regarding {section}.\n"
        "Provide a concise, professional comparison or structured list.\n"
        f"IMPORTANT: YOU MUST WRAP YOUR ENTIRE RESPONSE IN [WIDGET:{section}]...[/WIDGET] tags."
    )
    aggregator = Agent(
        name="widget_aggregator",
        model=model_name,
        instruction=aggregator_instruction,
        tools=[] # Aggregator doesn't need tools
    )
    
    return SequentialAgent(
        name=f"{sanitized_section}_widget_workflow",
        sub_agents=[parallel_agent, aggregator]
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
async def search_vais(req: SearchRequest):
    try:
        # Fast retrieval only - no summarySpec
        results = await vais_client.search(req.query, req.pageSize, req.offset)
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class OverviewRequest(BaseModel):
    query: str
    contexts: List[str]

class ReportRequest(BaseModel):
    ticker: str
    templateId: str
    session_id: str = "default_chat"
    model: str = "gemini-2.5-flash"
    use_mock_data: bool = False

@app.post("/search/generative-overview")
async def stream_search_overview(req: OverviewRequest):
    """
    Streams a generative overview using a dedicated Google ADK Agent (Gemini 2.5 Flash Lite).
    """
    async def generate_with_agent():
        try:
            # Construct context from search results
            context_str = "\n\n".join([f"Source {i+1}: {ctx}" for i, ctx in enumerate(req.contexts)])
            
            prompt = f"""
            You are a senior financial analyst assistant. 
            User Query: "{req.query}"

            Based ONLY on the provided search snippets below, write a concise, high-level executive summary (max 3-4 sentences).
            - Focus on the most important facts.
            - If the snippets don't answer the query, say so politely.
            
            AFTER the summary, provide 2-3 short, relevant follow-up questions that would help scope the search or dig deeper.
            
            Format:
            [Summary text...]

            **Follow-up Questions:**
            - [Question 1]
            - [Question 2]
            
            Contexts:
            {context_str}
            """
            
            # Create a dedicated agent for this request
            # We use the ADK Agent as requested by the user
            overview_agent = Agent(
                name="search_overview_worker",
                model="gemini-2.5-flash-lite",
                instruction="You are a helpful financial analyst. You synthesize search results into concise summaries.",
                tools=[] # No tools needed, just synthesis
            )
            
            # Create a temporary session for isolation
            temp_session_id = f"overview_{secrets.token_hex(4)}"
            await session_service.create_session(session_id=temp_session_id, user_id="overview_worker", app_name="stock_terminal_search")
            
            # Create runner
            runner = adk.Runner(app_name="stock_terminal_search", agent=overview_agent, session_service=session_service)
            msg = Content(role="user", parts=[Part(text=prompt)])
            
            # Stream response
            async for event in runner.run_async(user_id="overview_worker", session_id=temp_session_id, new_message=msg):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield json.dumps({"text": part.text}) + "\n"
                            
        except Exception as e:
            traceback.print_exc()
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate_with_agent(), media_type="application/x-ndjson")



def fix_leaked_data_blocks(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans text components for leaked <data_block> tags and converts them into chart components.
    This heals the output when the Synthesizer fails to transform the data itself.
    """
    print(f"[Healer] Scanning {len(components)} components for leaks...")
    new_components = []
    
    for i, comp in enumerate(components):
        if comp.get("type") == "text":
            content = comp.get("content", "")
            # Improved Regex: Handles single/double quotes and flexible whitespace
            # <data_block name="...">Content</data_block>
            pattern = r'<data_block\s+name=["\'](.*?)["\']>\s*(.*?)\s*</data_block>'
            matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
            
            if not matches:
                # Debug log to see if we missed it (sample first 100 chars)
                if "<data_block" in content:
                    print(f"[Healer] WARN: Found '<data_block' in component {i} but Regex failed! Content start: {content[:100]}")
                new_components.append(comp)
                continue
            
            print(f"[Healer] Found {len(matches)} leaks in component {i}")
            
            # We found blocks. Split and process.
            last_pos = 0
            for match in matches:
                # 1. Add text before the block
                pre_text = content[last_pos:match.start()].strip()
                if pre_text:
                    new_components.append({**comp, "content": pre_text})
                
                # 2. Process the block
                block_name = match.group(1)
                block_json_str = match.group(2)
                print(f"[Healer] Processing block: '{block_name}'")
                
                try:
                    block_data = json.loads(block_json_str)
                    
                    # Determine chart type heuristically
                    chart_type = "bar" # Default
                    lower_name = block_name.lower()
                    if "segments" in lower_name or "distribution" in lower_name or "geo" in lower_name:
                        chart_type = "pie"
                    elif "history" in lower_name or "trend" in lower_name or "price" in lower_name:
                        chart_type = "bar"
                    
                    # Create Healed Chart Component
                    print(f"[Healer] Recovered chart: {block_name} ({chart_type})")
                    new_components.append({
                        "type": "chart",
                        "title": block_name,
                        "chartType": chart_type,
                        "data": block_data,
                        "layout": "half",
                        "source": "Healer"
                    })
                except Exception as e:
                    print(f"[Healer] Failed to parse block {block_name}: {e}")
                    # If parsing fails, output the raw block as code so at least we see it debuggable
                    new_components.append({
                        "type": "text",
                        "title": f"Debug: {block_name}",
                        "content": f"```json\n{block_json_str}\n```"
                    })

                last_pos = match.end()
            
            # 3. Add remaining text
            remaining_text = content[last_pos:].strip()
            if remaining_text:
                 new_components.append({**comp, "content": remaining_text})
        else:
            new_components.append(comp)
            
    print(f"[Healer] Finished. New component count: {len(new_components)}")
    return new_components

def fix_nested_json_leaks(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans text components for hallucinated nested JSON blocks (e.g. {"components": [...]}) 
    that invalidate the report structure, and strips them.
    """
    print(f"[Cleaner] Scanning {len(components)} components for nested JSON leaks...")
    new_components = []
    
    for i, comp in enumerate(components):
        if comp.get("type") == "text":
            content = comp.get("content", "")
            
            # Check for markdown code blocks containing "components"
            # Pattern: ```json { "components": ...
            match = re.search(r'```json\s*\{\s*"components"', content)
            if match:
                print(f"[Cleaner] Found recursive JSON in component {i}. Stripping it...")
                # Truncate content at the start of the leak
                start_idx = match.start()
                cleaned_content = content[:start_idx].strip()
                if cleaned_content:
                    new_components.append({**comp, "content": cleaned_content})
                # If cleaned content is empty, we drop the component (it was just the leak)
            else:
                 # Check for raw JSON without backticks if it provides "components" list start
                 # e.g. "Some text { "components": [ ... ] }"
                 # Heuristic: must have { "components": [
                 match_raw = re.search(r'\s\{\s*"components":\s*\[', content)
                 if match_raw and len(content) > 50: # Only if mixed with text
                     print(f"[Cleaner] Found raw recursive JSON in component {i}. Stripping it...")
                     start_idx = match_raw.start()
                     cleaned_content = content[:start_idx].strip()
                     if cleaned_content:
                        new_components.append({**comp, "content": cleaned_content})
                 else:
                    new_components.append(comp)
        else:
            new_components.append(comp)
            
    return new_components


@app.post("/generate-report")
async def generate_report(req: ReportRequest):
    """
    Generates a full investment report using the specialized Report Orchestrator (ParallelAgent).
    Streams NDJSON events:
    - {"type": "status", "message": "..."}
    - {"type": "complete", "data": {...}}
    - {"type": "error", "message": "..."}
    """
    async def generate_stream():
        session_id = req.session_id
        
        # Determine Token Strategy
        if req.use_mock_data:
            print(f"[Report] Mock Mode requested for {req.ticker}")
            token = "mock_token_for_testing"
        else:
            token = await get_valid_factset_token(session_id)
            
            # Auto-fallback to mock if auth fails to improve User Experience
            if not token:
                print(f"[Report] Auth failed for {req.ticker}, falling back to Mock Mode.")
                yield json.dumps({"type": "status", "message": "Authentication unavailable. Switching to Demo/Mock Mode...", "agent": "Orchestrator"}) + "\n"
                token = "mock_token_for_testing"

        if not token:
            yield json.dumps({"type": "error", "message": "FactSet token invalid or expired."}) + "\n"
            return

        try:
            # Create specialized orchestrator
            agent = create_report_orchestrator(token, req.model, req.ticker, req.templateId)
            
            # Reuse existing session or create new one?
            report_session_id = f"report_{secrets.token_hex(4)}"
            await session_service.create_session(session_id=report_session_id, user_id="report_user", app_name="stock_terminal")
            
            runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)
            
            # Prompt is simple, the agents have the heavy lifting instructions
            prompt = f"Analyze {req.ticker}."
            
            final_text = ""
            msg = Content(role="user", parts=[Part(text=prompt)])
            
            yield json.dumps({"type": "status", "message": f"Initializing Parallel Agents for {req.ticker}..."}) + "\n"
            
            async for event in runner.run_async(user_id="report_user", session_id=report_session_id, new_message=msg):
                 # Detect Activity
                 if event.content and event.content.parts:
                     for part in event.content.parts:
                         if part.text:
                             final_text += part.text
                             # Can we detect if this is the final JSON?
                             # The Synthesizer is the one outputting text. The others mostly output tool calls or internal thoughts (if not silent).
                             # We'll just accumulate everything.
                         
                         if hasattr(part, "function_call") and part.function_call:
                             tool_name = part.function_call.name
                             # Clean up name for UI
                             friendly_name = tool_name.replace("FactSet_", "").replace("_", " ")
                             if "google_search" in tool_name:
                                 yield json.dumps({"type": "status", "message": "Researching Market Trends...", "agent": "MarketResearcher"}) + "\n"
                             elif "FactSet" in tool_name:
                                 yield json.dumps({"type": "status", "message": f"Fetching {friendly_name}...", "agent": "DataExtractor"}) + "\n"
                             else:
                                 yield json.dumps({"type": "status", "message": f"Using {friendly_name}...", "agent": "Orchestrator"}) + "\n"
                
            # Parse the Final JSON Component Feed
            # The synthesizer wraps everything in ```json ... ``` usually
            clean_text = final_text.strip()
            
            components = []
            
            # Parsing Logic with Brace Counting Fallback
            components = []
            
            def extract_first_json(text: str):
                """
                Robustly extracts the first valid JSON object from a string by counting braces.
                This handles cases where regex is too greedy or fails on nested structures.
                """
                text = text.strip()
                start_idx = text.find('{')
                if start_idx == -1:
                    return None
                
                balance = 0
                for i in range(start_idx, len(text)):
                    char = text[i]
                    if char == '{':
                        balance += 1
                    elif char == '}':
                        balance -= 1
                        if balance == 0:
                            # Potential candidate found
                            candidate = text[start_idx : i+1]
                            try:
                                return json.loads(candidate)
                            except:
                                # Keep going if this wasn't it (unlikely for valid JSON)
                                continue
                return None

            try:
                # 1. Try direct parsing first (Fastest)
                parsed = json.loads(clean_text)
            except:
                # 2. Try Robust Extraction
                print("[Report] Direct parse failed, attempting robust extraction...")
                parsed = extract_first_json(clean_text)
                
            if parsed and "components" in parsed:
                 components = parsed["components"]
            elif parsed:
                 # It parsed but didn't have "components", wrap it
                 components = [{"type": "text", "title": "Analysis", "content": clean_text}] 
            else:
                 # Total failure
                 print(f"[Report] JSON extraction failed completely.")
                 components = [{"type": "text", "title": "Raw Output", "content": clean_text}]

            # 3. Apply Heuristics to Fix Leaked Data Blocks
            components = fix_leaked_data_blocks(components)
            components = fix_nested_json_leaks(components)

            result_data = {
                "title": f"{req.ticker} Report",
                "ticker": req.ticker,
                "date": get_current_time().split('T')[0],
                "components": components # New Structure
            }
            
            yield json.dumps({"type": "complete", "data": result_data}) + "\n"

        except Exception as e:
            traceback.print_exc()
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")

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
    complex_model: str = "gemini-3-flash-preview"

class ChartCurationRequest(BaseModel):
    headers: List[str]
    rows: List[List[str]]
    context: Optional[str] = None
    session_id: str = "default_chat"

class WidgetRequest(BaseModel):
    tickers: List[str]
    section: str
    session_id: str = "default_chat"
    model: str = "gemini-2.5-flash"

class AuthCallbackRequest(BaseModel):
    redirect_url: str
    session_id: str = "default_chat"

class ManualAuthRequest(BaseModel):
    refresh_token: str
    session_id: str = "default_chat"

# --- AUTH ENDPOINTS ---

@app.get("/auth/factset/url")
def get_factset_auth_url(session_id: str = "default_chat"):
    """Returns the URL for the user to authenticate with FactSet."""
    params = {
        "response_type": "code",
        "client_id": FS_CLIENT_ID,
        "redirect_uri": FS_REDIRECT_URI,
        "scope": "mcp",
        "state": session_id,
        "prompt": "consent"
    }
    auth_url = requests.Request('GET', FS_AUTH_URL, params=params).prepare().url
    return {"auth_url": auth_url}

async def exchange_factset_code_for_token(code: str, session_id: str):
    """Internal helper to exchange an auth code for tokens."""
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

    async with httpx.AsyncClient() as client:
        response = await client.post(FS_TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 900)
            
            factset_tokens[session_id] = {
                "token": access_token,
                "refresh_token": refresh_token,
                "expires_at": time.time() + expires_in,
                "created_at": time.time()
            }
            save_tokens(factset_tokens)
            return True, tokens
        else:
            print(f"Token Exchange Failed: {response.text}")
            return False, response.text

@app.get("/auth/factset/callback")
async def factset_callback_get(code: str, state: Optional[str] = "default_chat"):
    """Automatic callback handler that closes the popup after success."""
    success, result = await exchange_factset_code_for_token(code, state)
    
    # Return HTML that closes the popup window
    if success:
        return HTMLResponse("""
            <html>
                <body style="font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f0f7ff;">
                    <div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
                        <h2 style="color: #004b87;">Authentication Successful!</h2>
                        <p style="color: #666;">You can close this window now. The terminal will automatically update.</p>
                        <script>
                            setTimeout(() => { window.close(); }, 2000);
                        </script>
                    </div>
                </body>
            </html>
        """)
    else:
        return HTMLResponse(f"""
            <html>
                <body style="font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #fff5f5;">
                    <div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
                        <h2 style="color: #c53030;">Authentication Failed</h2>
                        <p style="color: #666;">Error: {result}</p>
                    </div>
                </body>
            </html>
        """)

@app.post("/auth/factset/callback")
async def factset_callback_post(req: AuthCallbackRequest):
    """Exchanges the redirect URL code for an access token (Manual/POST mode)."""
    url = req.redirect_url
    print(f"Receiving callback URL (POST): {url}")

    try:
        if "code=" in url:
            parsed = urlparse(url)
            code = parse_qs(parsed.query).get('code', [None])[0]
        else:
            code = url if not url.startswith("http") else None
        
        if not code:
            raise HTTPException(status_code=400, detail="Could not extract authorization code from URL.")

        success, result = await exchange_factset_code_for_token(code, req.session_id)
        if success:
            return {"status": "success", "message": "FactSet Connected successfully!"}
        else:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {result}")

    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/factset/manual")
async def factset_manual_auth(req: ManualAuthRequest):
    """Manually stores a long-lived refresh token."""
    print(f"Storing manual refresh token for session: {req.session_id}")
    
    # We immediately try to get an access token to verify it works
    factset_tokens[req.session_id] = {
        "token": "pending", # Temporary
        "refresh_token": req.refresh_token,
        "expires_at": 0,    # Will be updated by refresh
        "created_at": time.time()
    }
    
    access_token = await refresh_factset_token(req.session_id)
    if access_token:
        return {"status": "success", "message": "Manual Refresh Token connected successfully!"}
    else:
        # Cleanup if failed
        factset_tokens.pop(req.session_id, None)
        save_tokens(factset_tokens)
        raise HTTPException(status_code=400, detail="Failed to verify manual refresh token. Please check it is valid.")

@app.get("/auth/factset/status")
async def get_factset_status(session_id: str = "default_chat"):
    token = await get_valid_factset_token(session_id)
    if not token:
        return {"connected": False}
    
    data = factset_tokens.get(session_id)
    created_at = data.get("created_at") if isinstance(data, dict) else None
    expires_at = data.get("expires_at", 0) if isinstance(data, dict) else 0
    has_refresh = bool(data.get("refresh_token")) if isinstance(data, dict) else False
    
    time_remaining = expires_at - time.time() if expires_at else 900
    
    return {
        "connected": True, 
        "created_at": created_at,
        "expires_in": max(0, int(time_remaining)),
        "has_refresh_token": has_refresh
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

def normalize_model_name(name: str) -> str:
    """Maps UI model labels to valid API model IDs."""
    if not name: return "gemini-2.5-flash-lite"
    n = name.lower()
    
    # Handle "3.0 Flash" -> Fallback to 2.0 Flash Exp or keep if valid environment
    # Assuming 2.0 Flash Exp is the intended 'bleeding edge' equivalent for now
    if "3.0" in n and "flash" in n: return "gemini-2.0-flash-exp"
    if "2.0" in n and "flash" in n: return "gemini-2.0-flash-exp"
    
    if "2.5" in n and "lite" in n: return "gemini-2.5-flash-lite"
    if "2.5" in n and "flash" in n: return "gemini-2.5-flash"
    
    # Handle just "Flash" or "Pro"
    if n == "flash": return "gemini-2.5-flash"
    if n == "pro": return "gemini-1.5-pro"
    
    # If it contains spaces, it's likely a UI label that missed mapping -> default to 2.5 Flash
    if " " in name: 
        print(f"[Warning] Unknown model label '{name}', defaulting to gemini-2.5-flash")
        return "gemini-2.5-flash"
        
    return name

@app.get("/ticker-info/{ticker}")
async def get_ticker_info(ticker: str):
    data = await asyncio.to_thread(get_stock_snapshot, ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.post("/summarize")
async def summarize(req: SummaryRequest):
    # Use the requested model if provided, otherwise default to lite
    agent = create_summary_agent(model_name=req.model or "gemini-2.5-flash-lite")
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

@app.post("/curate-chart")
async def curate_chart(req: ChartCurationRequest):
    """Uses an LLM to intelligently decide how to plot table data."""
    table_json = json.dumps({"headers": req.headers, "rows": req.rows})
    context_str = f"\nUSER CONTEXT/GOAL: {req.context}" if req.context else ""
    
    prompt = f"""
    Analyze the following table data and determine the BEST way to visualize it.
    {context_str}
    
    TABLE DATA:
    {table_json}
    
    GOAL:
    1. Identify the X-axis (usually the first column if it's dates or categories).
    2. Identify the meaningful data series to plot.
    3. IMPORTANT: DO NOT plot meta-columns like 'Fiscal Year', 'Index', or 'Rating' as series on the same Y-axis if they have a vastly different scale than the primary metric (e.g. don't plot Year 2025 next to EPS 7.35).
    4. If the data is Time Series (Date/Time on X-axis), return 'chartType': 'line'.
    5. If the data compares values across categories, return 'chartType': 'bar' or 'pie'.
    
    RESPONSE FORMAT:
    Return ONLY a JSON object with this exact structure:
    {{
      "title": "Descriptive Title",
      "chartType": "line" | "bar" | "pie",
      "series": [ // ONLY for line charts
        {{
          "ticker": "Series Name",
          "history": [ {{ "date": "...", "close": number }} ]
        }}
      ],
      "data": [ // ONLY for bar/pie charts
        {{ "label": "...", "value": number }}
      ]
    }}
    
    Rules:
    - Values MUST be numbers (strip $, %, commas).
    - If chartType is 'line', use 'series'. Ensure 'history' points have 'date' and 'close'.
    - If chartType is 'bar' or 'pie', use 'data'. Ensure points have 'label' and 'value'.
    """

    agent = Agent(
        model="gemini-2.5-flash-lite", 
        name="chart_curator",
        instruction="You are a data visualization architect. Return ONLY valid JSON."
    )
    
    runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)
    new_message = Content(parts=[Part(text=prompt)])
    
    responses = []
    try:
        async for event in runner.run_async(user_id="user_1", session_id=f"curate_{time.time()}", new_message=new_message):
            if event.content and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if part.text:
                        responses.append(part.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    full_text = "".join(responses)
    # Extract JSON if model added markdown blocks
    if "```json" in full_text:
        full_text = full_text.split("```json")[1].split("```")[0].strip()
    elif "```" in full_text:
        full_text = full_text.split("```")[1].split("```")[0].strip()
    
    try:
        chart_config = json.loads(full_text)
        return chart_config
    except Exception as e:
        print(f"Failed to parse curator JSON: {full_text}")
        raise HTTPException(status_code=500, detail="Invalid curator response")

@app.post("/generate-widget")
async def generate_widget_endpoint(req: WidgetRequest):
    """
    Dedicated endpoint for asynchronous widget generation.
    Returns a JSON response with the analysis content.
    """
    try:
        # ALWAYS use the base session_id to retrieve the auth token
        factset_token = await get_valid_factset_token(req.session_id)
        if not factset_token:
            raise HTTPException(status_code=401, detail="FactSet not connected")

        # Create the appropriate agent (Parallel or Single)
        if len(req.tickers) > 1:
            agent = create_parallel_data_analyst_workflow(
                token=factset_token, 
                tickers=req.tickers, 
                section=req.section, 
                model_name=req.model
            )
        else:
            ticker = req.tickers[0] if req.tickers else "selected company"
            agent = create_data_analyst_agent(
                token=factset_token, 
                ticker=ticker, 
                model_name=req.model, # Use the requested model
                section=req.section
            )
            agent.instruction += f"\nIMPORTANT: YOU MUST WRAP YOUR ENTIRE RESPONSE IN [WIDGET:{req.section}]...[/WIDGET] tags."

        runner = adk.Runner(app_name="stock_terminal_widgets", agent=agent, session_service=session_service)
        
        # Use a section-specific session ID to avoid history pollution between parallel widgets
        widget_session_id = f"{req.session_id}_{req.section.replace(' ', '_')}"
        
        # Ensure session exists
        if not await session_service.get_session(session_id=widget_session_id, app_name=runner.app_name, user_id="widget_user"):
            await session_service.create_session(session_id=widget_session_id, app_name=runner.app_name, user_id="widget_user")

        prompt = f"Generate {req.section} analysis for {', '.join(req.tickers)}."
        new_message = Content(role="user", parts=[Part(text=prompt)])
        
        full_text = ""
        async for event in runner.run_async(user_id="widget_user", session_id=widget_session_id, new_message=new_message):
            if event.content and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if part.text:
                        full_text += part.text
        
        # Extract content between tags if present
        import re
        tag_pattern = rf"\[WIDGET:{re.escape(req.section)}\]([\s\S]*?)\[/WIDGET\]"
        match = re.search(tag_pattern, full_text)
        content = match.group(1).strip() if match else full_text.strip()

        return {"section": req.section, "content": content}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Widget Generation Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(req: ChatRequest):
    start_time = time.time()
    # Simulation hook for verification
    if req.message == "SIMULATE_AUTH_ERROR":
        raise ValueError("FactSet authentication token expired or invalid. Please reconnect.")

    try:
        # FAST PATH: Check for simple greetings
        msg_lower = req.message.lower()
        is_greeting = handle_simple_greeting(req.message)
        
        agent = None
        factset_token = None
        
        # Determine Routing Path
        if is_greeting:
             print(f"DEBUG: [FAST PATH] Greeting detected. Skipping FactSet Auth.")
             agent = create_chat_agent(model_name=req.model)
             agent.instruction = (
                 "You are the FactSet Terminal Analyst. "
                 "Greeting the user warmly and concisely. "
                 "Suggest that you can help with financial data."
             )
             agent.name = "factset_analyst"
        
        else:
             t0 = time.time()
             factset_token = await get_valid_factset_token(req.session_id)
             print(f"DEBUG: Auth Check took {time.time() - t0:.4f}s")

             if factset_token:
                 # Extract section and tickers
                 import re
                 section_match = re.search(r"Generate (.+?) analysis", req.message)
                 tickers_match = re.search(r"analysis for ([^.]+)", req.message)
                 
                 section = section_match.group(1) if section_match else "Financial"
                 tickers_str = tickers_match.group(1).strip() if tickers_match else ""
                 if "IMPORTANT" in tickers_str:
                     tickers_str = tickers_str.split("IMPORTANT")[0].strip()
                 
                 tickers_list = [t.strip() for t in tickers_str.split(",") if t.strip()]
                 
                 if "generate" in msg_lower and "analysis for" in msg_lower:
                      if len(tickers_list) > 1:
                          print(f"DEBUGGING: Creating Parallel Workflow for {tickers_list}")
                          agent = create_parallel_data_analyst_workflow(token=factset_token, tickers=tickers_list, section=section, model_name=req.model)
                      else:
                          single_ticker = tickers_list[0] if tickers_list else None
                          print(f"DEBUGGING: Creating Data Analyst for {single_ticker}")
                          agent = create_data_analyst_agent(token=factset_token, ticker=single_ticker, model_name=req.model, section=section)
                          agent.instruction += f"\nIMPORTANT: YOU MUST WRAP YOUR ENTIRE RESPONSE IN [WIDGET:{section}]...[/WIDGET] tags."
                 
                 else:
                    async def run_parallel_comparison(tickers_str: str, metric_focus: str = "Price Performance") -> str:
                        return f"SWITCH_TO_PARALLEL_WORKFLOW:{tickers_str}:{metric_focus}"

                    gatekeeper_instruction = (
                        "You are the specialized FactSet Gatekeeper analyst.\n\n"
                        "EFFICIENCY PROTOCOL:\n"
                        "1. For SINGLE stock queries (e.g., 'Tell me about FDS'), be SURGICAL. "
                        "Start by fetching Fundamentals and Price data. Do NOT call Estimates, Metrics, or People tools immediately.\n"
                        "2. Synthesize a high-quality summary from initial data before deciding if more tools are needed.\n"
                        "3. Aim for high signal-to-noise ratio. Avoid redundant tool calls.\n\n"
                        "When a user asks to COMPARE stocks (e.g. 'Compare X and Y'):\n"
                        "1. **CONSULTATIVE MODE**: Do NOT fetch data immediately if the query is broad.\n"
                        "2. **ASK**: 'Would you like to compare Price Performance, Valuation, or News?'\n"
                        "3. **ONLY** run `run_parallel_comparison` if the user specifies the metric OR says 'Full/Detailed Analysis'."
                    )
                    
                    if "visualize" in msg_lower or "chart" in msg_lower or "plot" in msg_lower:
                        gatekeeper_instruction += "\nCRITICAL: The user wants a chart. You MUST use the [CHART] tag protocol to visualize the numbers discussed or recently fetched. Do NOT just summarize in text."
                    
                    t_create_agent = time.time()
                    agent = create_factset_agent(
                        token=factset_token, 
                        model_name=req.model,
                        instruction_override=gatekeeper_instruction + "\n" + FACTSET_INSTRUCTIONS,
                        extra_tools=[run_parallel_comparison]
                    )
                    print(f"DEBUG: create_factset_agent took {time.time() - t_create_agent:.4f}s")
             else:
                  agent = create_chat_agent(model_name=req.model)
        
        init_time = time.time() - start_time
        print(f"DEBUG: FINAL AGENT: {agent.name} (Init: {init_time:.2f}s)")

        # Safe debug logging for agent tools
        req_tools = getattr(agent, 'tools', [])
        if req_tools:
            tool_names = [t.name if hasattr(t, 'name') else str(t) for t in req_tools]
            print(f"DEBUG: Agent Tools: {tool_names}")
        else:
            print(f"DEBUG: FINAL TOOLS: [] (Composite Agent or No Tools)")

        runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)

        # Generate topology for visualization
        t_topo = time.time()
        topo = generate_topology(agent)
        print(f"DEBUG: Topology Generation took {time.time() - t_topo:.4f}s")
        
        print(f"DEBUG: Request Ready for Runner at {time.time() - start_time:.4f}s total")
    
    
    except Exception as e:
        print(f"Initialization Error: {e}")
        traceback.print_exc()
        # Capture error message string to avoid "free variable" issues in closure
        err_str = str(e)
        async def error_generator():
             yield json.dumps({"type": "error", "content": f"Init failed: {err_str}"}) + "\n"
        return StreamingResponse(error_generator(), media_type="application/x-ndjson")

    # Move imports to top if possible, or keep here
    from google.genai.types import Content, Part
    
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

    new_message = Content(role="user", parts=parts)

    session = await session_service.get_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")
    if not session:
        await session_service.create_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")
        session = await session_service.get_session(session_id=req.session_id, app_name=runner.app_name, user_id="user_1")

    # --- HISTORY TRUNCATION (Fix for 1M Token Limit) ---
    # Check if session history is getting too long. 
    # ADK Session history is typically a list of Content objects.
    # We want to preserve the System Prompt (usually distinct or first) but truncate the middle.
    MAX_HISTORY = 6
    if hasattr(session, 'history') and len(session.history) > MAX_HISTORY:
        print(f"DEBUG: Truncating session history from {len(session.history)} to {MAX_HISTORY}")
        # Keep the most recent messages. ADK usually handles system instruction separately via Agent definition.
        # So we can safely just slice the history.
        session.history = session.history[-MAX_HISTORY:]

    # Recursive function to find the root cause
    def get_root_cause(exc):
        exc_str = str(exc)
        
        # 1. Check for specific known messages
        if "FactSet authentication token expired" in exc_str:
            return exc_str
        
        # 2. Check for HTTP 401/403
        if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
            if exc.response.status_code in (401, 403):
                return "FactSet authentication token expired or invalid. Please reconnect."

        # 3. Check for Network Errors
        if "ReadError" in exc_str or "anyio.EndOfStream" in exc_str or "ConnectionResetError" in exc_str:
            return "Network Error: The FactSet service closed the connection (ReadError). This often happens during high-concurrency parallel tasks. Please try again."

        # 4. Unwrap ExceptionGroups/BaseExceptionGroups (anyio/asyncio)
        if hasattr(exc, "exceptions") and exc.exceptions:
            # Recursive search for a known error in the group
            for sub_exc in exc.exceptions:
                found = get_root_cause(sub_exc)
                # If we found something more specific than the generic group message, return it
                if found and "TaskGroup" not in found and "sub-exception" not in found:
                    return found
            # If no specific known error found, return the root cause of the first sub-exception
            return get_root_cause(exc.exceptions[0])
        
        # 5. Unwrap direct causes (chained exceptions)
        if hasattr(exc, "__cause__") and exc.__cause__:
            return get_root_cause(exc.__cause__)
            
        if hasattr(exc, "__context__") and exc.__context__:
            return get_root_cause(exc.__context__)
        
        # 6. Fallback to string but avoid generic TaskGroup message
        if "unhandled errors in a TaskGroup" in exc_str and hasattr(exc, "exceptions") and exc.exceptions:
             return get_root_cause(exc.exceptions[0])

        return exc_str

    async def event_generator():
        # Helper to parse events consistently across ADK versions
        def parse_event(event, start_times):
            source = event.step if hasattr(event, "step") and event.step else event
            results = []
            source_agent = getattr(source, 'author', None) or getattr(event, 'author', None)

            # Case A: Parts-based Content (Newer ADK)
            content_obj = getattr(source, "model_content", None) or getattr(source, "content", None)
            if not content_obj and hasattr(source, "parts"): content_obj = source
            elif not content_obj and hasattr(event, "content") and event.content: content_obj = event.content

            if content_obj and hasattr(content_obj, "parts") and content_obj.parts:
                for part in content_obj.parts:
                    if hasattr(part, "text") and part.text:
                        results.append({"type": "text", "content": part.text, "sourceAgent": source_agent})
                    elif hasattr(part, "function_call") and part.function_call:
                        call = part.function_call
                        start_times[call.name] = time.time()
                        args = call.args if isinstance(call.args, dict) else getattr(call.args, "__dict__", {})
                        results.append({"type": "tool_call", "tool": call.name, "args": args, "sourceAgent": source_agent})
                    elif hasattr(part, "function_response") and part.function_response:
                        resp = part.function_response
                        duration = time.time() - start_times.pop(resp.name, time.time())
                        results.append({"type": "tool_result", "tool": resp.name, "result": resp.response, "duration": duration, "sourceAgent": source_agent})

            # Case B: Traditional Tool Call
            if hasattr(source, "tool_code") and source.tool_code:
                call = source.tool_code
                if not any(r.get("type") == "tool_call" and r.get("tool") == call.name for r in results):
                    start_times[call.name] = time.time()
                    results.append({"type": "tool_call", "tool": call.name, "args": call.args, "sourceAgent": source_agent})
                
            # Case C: Traditional Tool Result
            if hasattr(source, "tool_result") and source.tool_result:
                resp = source.tool_result
                if not any(r.get("type") == "tool_result" and r.get("tool") == resp.name for r in results):
                    duration = time.time() - start_times.pop(resp.name, time.time())
                    results.append({"type": "tool_result", "tool": resp.name, "result": resp.response, "duration": duration, "sourceAgent": source_agent})
            
            # PATCH: Handle double-serialization in results
            for res in results:
                if res["type"] == "tool_result" and isinstance(res["result"], str):
                    s = res["result"].strip()
                    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
                        try:
                            res["result"] = json.loads(s)
                        except:
                            try:
                                import ast
                                res["result"] = ast.literal_eval(s)
                            except: pass

            return results

        # 1. Emit Topology Event IMMEDIATELY
        yield json.dumps({"type": "topology", "data": topo}) + "\n"
        
        # 2. Emit Model Info
        def extract_models_recursive(agent_obj):
            models_found = []
            # Check current agent
            if hasattr(agent_obj, "model") and agent_obj.model:
                models_found.append(agent_obj.model)
            elif hasattr(agent_obj, "_model") and agent_obj._model:
                models_found.append(agent_obj._model)
            
            # Recurse children
            if hasattr(agent_obj, "sub_agents") and agent_obj.sub_agents:
                for sub in agent_obj.sub_agents:
                    models_found.extend(extract_models_recursive(sub))
            
            return models_found

        all_models = extract_models_recursive(agent)
        
        # Normalize models
        normalized_models = []
        for am in all_models:
            if isinstance(am, str):
                normalized_models.append(am)
            elif hasattr(am, "name"):
                normalized_models.append(am.name)
            elif hasattr(am, "model_id"):
                normalized_models.append(am.model_id)
            else:
                normalized_models.append(str(am))

        unique_models = list(set(filter(None, normalized_models)))
        yield json.dumps({"type": "model_info", "models": unique_models}) + "\n"

        current_runner = runner
        tool_start_times = {}
        full_content_buffer = ""
        switch_directive = None

        try:
            try:
                import httpx
                t_first_event = time.time()
                first_event_logged = False
                
                async for event in current_runner.run_async(user_id="user_1", session_id=req.session_id, new_message=new_message):
                    if not first_event_logged:
                        print(f"DEBUG: First Event received at {time.time() - t_first_event:.4f}s from execution start")
                        first_event_logged = True
                        
                    # 1. Yield Usage
                    if hasattr(event, "usage_metadata") and event.usage_metadata:
                        yield json.dumps({
                            "type": "usage", 
                            "prompt_tokens": event.usage_metadata.prompt_token_count or 0, 
                            "candidates_tokens": event.usage_metadata.candidates_token_count or 0, 
                            "total_tokens": event.usage_metadata.total_token_count or 0
                        }) + "\n"

                    # 2. Parse and Yield Event Data
                    try:
                        data_list = parse_event(event, tool_start_times)
                        
                        for data in data_list:
                            # Update buffer if text
                            if data["type"] == "text":
                                full_content_buffer += data["content"]
                            
                            # Check for Sentinel in tool result
                            if data["type"] == "tool_result":
                                res_val = data["result"]
                                if isinstance(res_val, dict) and "result" in res_val:
                                    res_val = res_val["result"]
                                
                                res_str = str(res_val)
                                if "SWITCH_TO_PARALLEL_WORKFLOW:" in res_str:
                                    print(f"DEBUG: Detected switch directive: {res_str}")
                                    switch_directive = res_str

                            yield json.dumps(data) + "\n"
                    except Exception as e2:
                        print(f"Error processing event: {e2}")

            # End of first run.
            except ImportError:
                 pass
            
            # 2. Check for Switch Directive
            if switch_directive:
                try:
                    print(f"[Main] Switching to Parallel Workflow based on directive: {switch_directive}")
                    yield json.dumps({"type": "text", "content": "\n\n_Starting Parallel Workflow..._\n"}) + "\n"
                    _, tickers_str, metric_focus = switch_directive.split(":", 2)
                    metric_focus = metric_focus.strip().replace("'", "").replace('"', "")
                    
                    # Construct the Parallel Agent (Copied logic from earlier)
                    # Parse tickers
                    raw_list = [t.strip() for t in tickers_str.split(',')]
                    target_tickers = raw_list[:4]
                    
                    # Normalize model name
                    complex_model_id = normalize_model_name(req.complex_model)
                    print(f"[Main] Using normalized complex model: {complex_model_id} (from '{req.complex_model}')")
    
                    parallel_workers = []
                    for t in target_tickers:
                        worker = create_data_analyst_agent(
                            token=factset_token,
                            model_name=complex_model_id, # Use NORMALIZED model
                            ticker=t,
                            section=metric_focus
                        )
                        parallel_workers.append(worker)
                       
                    sanitized_section = metric_focus.replace(" ", "_")
                    parallel_agent = ParallelAgent(
                        name=f"parallel_{sanitized_section}_fetcher",
                        sub_agents=parallel_workers
                    )
                    
                    sum_instr = (
                        f"Summarize comparison of {tickers_str}. Focus: {metric_focus}.\n"
                        "Synthesize findings. No tools."
                    )
                    summarizer = Agent(
                        name="summary_analyst",
                        model=complex_model_id, # Use NORMALIZED model
                        tools=[],
                        instruction=sum_instr
                    )
                   
                    workflow_agent = SequentialAgent(
                        name=f"{sanitized_section}_widget_workflow",
                        sub_agents=[parallel_agent, summarizer]
                    )
                   
                    # Create NEW Runner for the workflow
                    new_topo = generate_topology(workflow_agent)
                    print(f"[Main] Yielding NEW Topology with {len(new_topo['nodes'])} nodes")
                    yield json.dumps({"type": "topology", "data": new_topo}) + "\n"
                    
                    # Emit NEW Model Info for workflow
                    workflow_models = []
                    if hasattr(workflow_agent, "model"): workflow_models.append(workflow_agent.model)
                    if hasattr(workflow_agent, "sub_agents"):
                        for sa in workflow_agent.sub_agents:
                            if hasattr(sa, "model"): workflow_models.append(sa.model)
                    unique_workflow_models = list(set(filter(None, workflow_models)))
                    yield json.dumps({"type": "model_info", "models": unique_workflow_models}) + "\n"
    
                    workflow_runner = adk.Runner(app_name="stock_terminal_parallel", agent=workflow_agent, session_service=session_service)
                    # Ensure session exists but don't fail if it does
                    if not await session_service.get_session(session_id=req.session_id, app_name="stock_terminal_parallel", user_id="user_1"):
                        await session_service.create_session(session_id=req.session_id, app_name="stock_terminal_parallel", user_id="user_1")
                   
                    workflow_tool_start_times = {}
                    workflow_buffer = ""
    
                    # Run the workflow with a dummy trigger message
                    trigger_msg = Content(role="user", parts=[Part(text=f"Proceed with fetching data for {tickers_str} focusing on {metric_focus}")])
                    
                    async for event in workflow_runner.run_async(user_id="user_1", session_id=req.session_id, new_message=trigger_msg):
                        # 1. Yield Usage
                        if hasattr(event, "usage_metadata") and event.usage_metadata:
                            yield json.dumps({
                                "type": "usage", 
                                "prompt_tokens": event.usage_metadata.prompt_token_count or 0, 
                                "candidates_tokens": event.usage_metadata.candidates_token_count or 0, 
                                "total_tokens": event.usage_metadata.total_token_count or 0
                            }) + "\n"
    
                        # 2. Parse and Yield Event Data
                        try:
                            data_list = parse_event(event, workflow_tool_start_times)
                            for data in data_list:
                                if data["type"] == "text":
                                    workflow_buffer += data["content"]
                                yield json.dumps(data) + "\n"
                        except Exception as e3:
                            print(f"Error processing workflow event: {e3}")
                            traceback.print_exc()

                except Exception as e_switch:
                    print(f"[Main] Error in Parallel Switch: {e_switch}")
                    traceback.print_exc()
                    
                    root_msg = get_root_cause(e_switch)
                    error_msg = f"Parallel Workflow Failed: {root_msg}" if root_msg else f"Parallel Workflow Failed: {str(e_switch)}"
                    
                    yield json.dumps({"type": "error", "content": error_msg}) + "\n"
    

        except Exception as e:
            print(f"Stream error: {e}")
            traceback.print_exc()
            
            error_msg = get_root_cause(e) or str(e)
            
            # Check for httpx.ReadError (via string check if class not imported or generic)
            if "httpx.ReadError" in str(type(e)) or "ReadError" in str(e):
                 yield json.dumps({"type": "error", "content": "Network Error: The AI service closed the connection (ReadError)."}) + "\n"
                 return

            yield json.dumps({"type": "error", "content": error_msg}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
