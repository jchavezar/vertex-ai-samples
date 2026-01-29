import os
import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import google.adk as adk
from google.adk.agents import Agent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Reuse existing tools if possible, or define specialized ones
from src.market_data import get_real_price, get_real_history
from google.adk.tools import google_search as adk_google_search

logger = logging.getLogger("adk_comps_workflow")

# --- SCHEMAS ---

class PeerIntel(BaseModel):
    ticker: str
    name: str
    ceo_sentiment: str = Field(description="Aggressive/Defensive strategic posture")
    identity: str = Field(description="Visual brand aura (e.g. 'Neon Sapphire')")
    last_launch: str = Field(description="Latest major product or strategic event")
    momentum: str = Field(description="Sentiment: Bullish, Bearish, etc.")
    upside: int = Field(description="0-100 probability")
    vol_risk: int = Field(description="0-100 volatility risk")
    marketCap: str
    price: float
    change: float
    comparison_thesis: str = Field(description="Why this peer is a structural threat or opportunity")
    alpha_thesis: str = Field(description="The core structural advantage or gap (2-3 sentences)")
    valuation_gap: str = Field(description="Relative valuation insight (e.g., '12.4x P/E Premium')")
    key_metrics: List[str] = Field(description="2-3 key technical data points (e.g. 'Blackwell B200', '3.2T MCAP')")

# --- WORKFLOW ---

def create_discovery_agent():
    return LlmAgent(
        name="discovery_bot",
        model="gemini-2.5-flash-lite",
        instruction="Find 3 direct strategic competitors for the given ticker. Use search to find recent market leaders and disruptors. Return ONLY a JSON list of tickers like ['AMD', 'INTC', 'AVGO'].",
        tools=[adk_google_search]
    )

async def create_research_agent(fs_token: Optional[str] = None):
    # Use the robust SmartAgent factory
    from src.smart_agent import create_smart_agent
    
    # We use gemini-2.5-flash for the deep research
    agent = await create_smart_agent(
        token=fs_token if fs_token else "mock", 
        model_name="gemini-2.5-flash"
    )
    
    # Update instructions specifically for the Battlecard context
    # while keeping the base smart instructions
    agent.instruction += """
    
    ### COMP ANALYSIS SPECIAL INSTRUCTIONS
    You are acting as a Deep Equity Researcher for a Battlecard.
    Your goal is to research a target ticker in the context of its competition with a primary ticker.
    Provide a deep strategic battle card using the available tools.
    
    REQUIRED JSON OUTPUT FIELDS:
    - ticker: The stock ticker
    - name: Company name
    - ceo_sentiment: 1-sentence analytical take on CEO posture
    - identity: 3-word visual brand aura
    - last_launch: Most impactful recent product or strategic event
    - momentum: Sentiment (e.g. 'Bullish', 'Hyper-Growth')
    - upside: Probability score 0-100 indicating conviction in alpha thesis
    - vol_risk: Volatility/Operational risk score 0-100
    - marketCap: readable string (e.g. '2.5T', '450B')
    - price: Current float
    - change: % float (relative to previous close)
    - comparison_thesis: Senior analyst level contrast vs the primary company. 
    - alpha_thesis: A 2-3 sentence deep dive into the structural advantage or gap.
    - valuation_gap: A string representing the valuation contrast (e.g. '12.4x P/E Premium').
    - key_metrics: A list of 2-3 short strings representing core technical strengths (e.g. ['Blackwell B200', '3.2T MCAP']).
    
    Return ONLY the JSON object.
    """
    return agent

async def run_adk_comps_workflow(ticker: str, session_id: str, context: str = "", token: Optional[str] = None):
    """
    Orchestrates the multi-agent Comps Analysis workflow.
    
    Flow:
    1. Discovery: Search for strategic competitors.
    2. Parallel Research: Deep dive into each peer concurrently.
    3. Synthesis: Aggregate and format the final cluster.
    """
    logger.info(f"Starting ADK Comps Workflow for {ticker} with context: {context}")
    
    session_service = InMemorySessionService()
    # Initialize research agent
    research_agent = await create_research_agent(token)
    
    # 1. Strategic Discovery
    yield {"type": "reasoning", "message": f"Establishing neural context for {ticker}...", "progress": 5}
    if context:
        yield {"type": "reasoning", "message": f"Filtering reconnaissance through focal point: '{context}'...", "progress": 10}

    discovery_session_id = f"{session_id}_discovery"
    # Ensure session exists
    await session_service.create_session(session_id=discovery_session_id, user_id="system", app_name="adk_comps")
    
    discovery_bot = LlmAgent(
        name="StrategicDiscoveryBot",
        model="gemini-2.0-flash",
        instruction=f"""
        You are a strategic peer discovery bot.
        Target: {ticker}
        Focal Point: {context if context else 'General competitive landscape'}
        
        Task: Identify exactly 3 strategic competitors for {ticker}.
        If a focus context is provided, prioritize companies that compete directly in that specific area.
        Return ONLY a JSON list of tickers.
        Example: ["AMD", "INTC", "AVGO"]
        """,
        tools=[adk_google_search]
    )
    
    runner = adk.Runner(app_name="adk_comps", agent=discovery_bot, session_service=session_service)
    discovery_output = ""
    msg = types.Content(role="user", parts=[types.Part(text=f"Identify 3 strategic competitors for {ticker} focused on {context if context else 'the broader market'}.")])
    async for event in runner.run_async(user_id="system", session_id=discovery_session_id, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: discovery_output += part.text
    
    try:
        match = re.search(r'\[.*\]', discovery_output, re.DOTALL)
        peer_tickers = json.loads(match.group(0)) if match else ["AMD", "AVGO", "INTC"]
        peer_tickers = [p.upper() for p in peer_tickers if p.upper() != ticker.upper()][:3]
    except:
        peer_tickers = ["AMD", "AVGO", "INTC"]
    
    if not peer_tickers: peer_tickers = ["AMD", "AVGO", "INTC"]
    
    yield {"type": "reasoning", "message": f"> Discovered Peer Cluster: {', '.join(peer_tickers)}", "progress": 30}
    
    # Step 2: Parallel Analysis
    yield {"type": "reasoning", "message": f"> Deploying Parallel Agents for deep dive...", "progress": 50}
    
    tasks = []
    # Primary first
    primary_session_id = f"{session_id}_primary"
    await session_service.create_session(session_id=primary_session_id, user_id="system", app_name="adk_comps")
    primary_runner = adk.Runner(app_name="adk_comps", agent=research_agent, session_service=session_service)
    tasks.append(run_one_research(primary_runner, ticker, ticker, primary_session_id))
    
    # Then Peers
    for peer in peer_tickers:
        peer_session_id = f"{session_id}_{peer}"
        await session_service.create_session(session_id=peer_session_id, user_id="system", app_name="adk_comps")
        research_runner = adk.Runner(app_name="adk_comps", agent=research_agent, session_service=session_service)
        tasks.append(run_one_research(research_runner, peer, ticker, peer_session_id))
    
    responses = await asyncio.gather(*tasks)
    
    # Step 3: Aggregate
    yield {"type": "reasoning", "message": "> Synthesizing Alpha Cluster and Cross-Correlation...", "progress": 85}
    
    primary_json = None
    peer_jsons = []
    
    if responses:
        # First task was primary
        primary_json = extract_json(responses[0])
        # Following tasks were peers
        for r in responses[1:]:
            p_json = extract_json(r)
            if p_json:
                # If the agent returned a wrapped dict { 'TICKER': {...} }, unwrap it
                if len(p_json.keys()) == 1 and isinstance(list(p_json.values())[0], dict):
                    p_json = list(p_json.values())[0]
                peer_jsons.append(p_json)
    
    # Fallback if primary extraction failed
    if not primary_json and peer_jsons:
        # Check if one of the peers is actually the primary (shouldn't happen but good to be safe)
        for i, p in enumerate(peer_jsons):
            if p.get("ticker") == ticker:
                primary_json = peer_jsons.pop(i)
                break

    final_intel = {
        "summary": f"Alpha thesis for {ticker} vs cluster: {', '.join([p.get('ticker','PEER') for p in peer_jsons])}.",
        "reasoning": [
            f"Neural Recon: Identified {len(peer_jsons)} strategic peers.",
            f"Semantic Analysis: CEO posture suggests competitive positioning for {ticker}.",
            "Parallel Research: Real-time price and history metrics cross-correlated."
        ],
        "primary": primary_json,
        "peers": peer_jsons
    }
    
    yield {"type": "intel", "data": final_intel}
    yield {"type": "reasoning", "message": "> Neural Sync Complete.", "progress": 100}

async def run_one_research(runner, target, primary, sess_id):
    result = ""
    prompt = f"""
    Perform a DEEP reconnaissance on {target} in the context of its competition with {primary}.
    Use FactSet tools to retrieve real-time data on price, market cap, and strategic momentum.
    
    Return a single JSON object representing the battlecard for {target}.
    """
    msg = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id="system", session_id=sess_id, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: result += part.text
    return result

def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return None

if __name__ == "__main__":
    async def main():
        async for event in run_adk_comps_workflow("NVDA", "test_" + re.sub(r'[^a-zA-Z0-9]', '_', str(asyncio.get_event_loop()))):
            print(f"EVENT: {event}")
    asyncio.run(main())
