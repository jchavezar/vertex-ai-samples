import os
import json
import asyncio
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
from factset_agent import create_factset_agent

load_dotenv()

# Setup ADK components
session_service = InMemorySessionService()
# Simple in-memory storage for tokens (in production use a database/Redis)
factset_tokens = {} 

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
You can answer questions about the market, specific stocks, and financial concepts.

MULTIMODAL CAPABILITIES:
- You can SEE and ANALYZE images provided by the user (e.g., stock charts, financial reports, or screenshots).
- You can WATCH and ANALYZE YouTube videos provided via link.
- If the user provides an image or video, extract relevant data and use it to enhance your response.

CRITICAL GUIDELINES:
1. For any questions about financial figures, numbers, or company-specific data that can be retrieved via the FactSet MCP tools, you MUST use those tools. 
2. Do NOT invent or estimate financial information. If you do not have access to the data through your tools, state that clearly.
3. Use your general knowledge ONLY for broad financial concepts, general market history, or banal conversation.
4. Be professional, 100% factual, and concise. Accuracy is paramount.
5. Use the get_current_time tool to determine the current date if you need to calculate 'today', 'yesterday', or 'a month ago' for date-based queries.
6. Always present stock prices and financial data in a clean, readable format using Markdown tables or bullet points.
"""

# Note: We'll retrieve FACTSET_INSTRUCTIONS directly from factset_agent if possible, 
# or just define it here if we want to centralize. 
# For now, let's just use these constants.

def get_current_time() -> str:
    """Returns the current central date and time in ISO format. Use this to determine 'today', 'yesterday', or relative dates."""
    import datetime
    return datetime.datetime.now().isoformat()

def create_chat_agent(model_name: str = "gemini-2.5-flash"):
    return Agent(
        name="terminal_assistant",
        model=model_name,
        tools=[get_current_time],
        instruction=CHAT_INSTRUCTIONS
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
            # Store token
            factset_tokens[req.session_id] = access_token
            return {"status": "success", "message": "FactSet Connected successfully!"}
        else:
            print(f"Token Exchange Failed: {response.text}")
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")

    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/factset/status")
def get_factset_status(session_id: str = "default_chat"):
    return {"connected": session_id in factset_tokens}

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
                {"name": "get_current_time", "description": "Returns the current central date and time in ISO format."}
            ]
        },
        "factset_agent": {
            "name": "factset_analyst",
            "instruction": clean(FACTSET_INSTRUCTIONS),
            "tools": [
                {"name": "FactSet MCP Toolset", "description": "Global prices, company snapshots, estimates, and more via FactSet API."},
                {"name": "get_current_time", "description": "Returns the current central date and time in ISO format."}
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

    # Check if we have a FactSet token for this session
    factset_token = factset_tokens.get(req.session_id)
    
    if factset_token:
        print(f"Using FactSet Agent for session {req.session_id}")
        agent = create_factset_agent(token=factset_token, model_name=req.model)
    else:
        print(f"Using Standard Chat Agent for session {req.session_id}")
        agent = create_chat_agent(model_name=req.model)

    runner = adk.Runner(app_name="stock_terminal", agent=agent, session_service=session_service)

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

    async def event_generator():
        try:
            async for event in runner.run_async(user_id="user_1", session_id=req.session_id, new_message=new_message):
                # Inspect event for tool calls/thoughts (simplified based on typical ADK events)
                # Note: ADK events might be complex types, we iterate content.parts
                
                # Check for Tool Calls (Execution Steps)
                if hasattr(event, "step") and event.step:
                    # Depending on ADK version, steps might be available. 
                    # For now, we infer from content parts if they are function calls
                    pass
                
                if event.content and hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        # Log/Debug print
                        # print(f"DEBUG PART: {part}")
                        
                        # Handle Text (Thought or Final Response)
                        if part.text:
                            # Heuristic: If it's a short "thought" or valid text
                            yield json.dumps({"type": "text", "content": part.text}) + "\n"
                        
                        # Handle Function Calls
                        if hasattr(part, "function_call") and part.function_call:
                            call = part.function_call
                            yield json.dumps({
                                "type": "tool_call", 
                                "tool": call.name, 
                                "args": call.args
                            }) + "\n"
                        
                        # Handle Function Responses (if available in this event stream style)
                        if hasattr(part, "function_response") and part.function_response:
                             resp = part.function_response
                             # Use the raw response object so it serializes to JSON, not a string representation
                             result_content = resp.response
                             
                             yield json.dumps({
                                 "type": "tool_result",
                                 "tool": resp.name,
                                 "result": result_content
                             }) + "\n"

                # Check for Usage Metadata (Tokens)
                if hasattr(event, "usage_metadata") and event.usage_metadata:
                    yield json.dumps({
                        "type": "usage",
                        "prompt_tokens": event.usage_metadata.prompt_token_count,
                        "candidates_tokens": event.usage_metadata.candidates_token_count,
                        "total_tokens": event.usage_metadata.total_token_count
                    }) + "\n"

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
