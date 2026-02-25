import asyncio
import logging
import json
import secrets
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.adk import Runner
from google.genai import types

logger = logging.getLogger("news_agent")

MODEL_NAME = "gemini-2.5-flash"

# --- SCHEMAS ---

class NewsItem(BaseModel):
    id: str = Field(description="Unique ID for the news item")
    headline: str
    source: str
    summary: str
    url: str
    time: str = Field(description="Estimated relative time, e.g. '2h ago'")
    sentiment: Literal['positive', 'negative', 'neutral']
    impact_score: int = Field(description="0-100 score indicating market impact")

class NewsResponse(BaseModel):
    items: List[NewsItem]

# --- SUB-AGENTS ---

def create_specific_news_agent(ticker: str) -> LlmAgent:
    return LlmAgent(
        name="SpecificNewsAgent",
        model=MODEL_NAME,
        instruction=f"""
        You are a Financial News Researcher. 
        Research the latest, most impactful news for {ticker} specifically. 
        Focus on: Earnings rumors, quarterly results, product launches, or CEO statements.
        Use `google_search`.
        Summarize the top 3 items in clean text.
        """,
        tools=[google_search],
        output_key="specific_news"
    )

def create_peer_news_agent(ticker: str) -> LlmAgent:
    return LlmAgent(
        name="PeerNewsAgent",
        model=MODEL_NAME,
        instruction=f"""
        You are a Competitive Intelligence Analyst.
        Research what the competitors of {ticker} are doing.
        Find news that might impact {ticker} indirectly.
        Use `google_search`.
        Summarize the top 3 items in clean text.
        """,
        tools=[google_search],
        output_key="peer_news"
    )

def create_macro_news_agent(ticker: str) -> LlmAgent:
    return LlmAgent(
        name="MacroNewsAgent",
        model=MODEL_NAME,
        instruction=f"""
        You are a Macro Strategy Researcher.
        Research sector-wide trends (AI, Chips, whatever applies to {ticker}) and analyst upgrades/downgrades for {ticker}.
        Use `google_search`.
        Summarize the top 3 items in clean text.
        """,
        tools=[google_search],
        output_key="macro_news"
    )

# --- SYNTHESIS AGENT ---

def create_synthesis_agent(ticker: str) -> LlmAgent:
    return LlmAgent(
        name="SynthesisAgent",
        model=MODEL_NAME,
        instruction=f"""
        You are a Data Orchestrator. 
        You will receive 3 news summaries for {ticker}:
        
        1. Specific News: {{specific_news}}
        2. Peer News: {{peer_news}}
        3. Macro/Sector News: {{macro_news}}
        
        Your task is to synthesize these into a single list of high-impact `NewsItems`.
        
        RULES:
        - Output ONLY a JSON object matching the `NewsResponse` schema.
        - Ensure `impact_score` is realistic.
        - Assign a unique ID to each item.
        - If no news is found across all inputs, return an empty items list.
        """,
        output_schema=NewsResponse,
        output_key="final_news_result"
    )

# --- PUBLIC INTERFACE ---

async def get_parallel_news(ticker: str) -> List[NewsItem]:
    """
    Orchestrates the News Research Pipeline using Parallel and Sequential Agents.
    """
    session_service = InMemorySessionService()
    # Pre-initialize state to avoid "Context variable not found" errors
    initial_state = {
        "specific_news": "No news found.",
        "peer_news": "No news found.",
        "macro_news": "No news found."
    }
    
    sid = f"news_pipeline_{ticker}_{secrets.token_hex(4)}"
    await session_service.create_session(
        session_id=sid, 
        user_id="system", 
        app_name="news_svc",
        state=initial_state
    )
    
    # Define Pipeline
    specific = create_specific_news_agent(ticker)
    peer = create_peer_news_agent(ticker)
    macro = create_macro_news_agent(ticker)
    
    parallel_research = ParallelAgent(
        name="ParallelNewsResearch",
        sub_agents=[specific, peer, macro]
    )
    
    synthesis = create_synthesis_agent(ticker)
    
    pipeline = SequentialAgent(
        name="NewsPipeline",
        sub_agents=[parallel_research, synthesis]
    )
    
    runner = Runner(app_name="news_svc", agent=pipeline, session_service=session_service)
    
    # Execute
    query = f"Execute news pipeline for {ticker}"
    msg = types.Content(role="user", parts=[types.Part(text=query)])
    
    try:
        # We run the pipeline.
        async for _ in runner.run_async(user_id="system", session_id=sid, new_message=msg):
            pass
            
        # Retrieve final result from session state
        session = await session_service.get_session(app_name="news_svc", user_id="system", session_id=sid)
        print(f"Final State Keys: {list(session.state.keys())}")
        
        result = session.state.get("final_news_result")
        
        if result:
            # Check if it's a NewsResponse object
            if hasattr(result, 'items') and not callable(result.items):
                return result.items
            # Check if it's a dict (common if retrieved from state)
            if isinstance(result, dict) and "items" in result:
                return [NewsItem(**i) for i in result["items"]]
                
        return []
        
    except Exception as e:
        logger.error(f"News Pipeline failed for {ticker}: {e}")
        return []
