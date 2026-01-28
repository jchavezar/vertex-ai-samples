import os
import logging
import asyncio
import datetime
import json
from typing import List, Optional, Dict, Any
from google.adk.agents import Agent
from google.genai import types

logger = logging.getLogger("analyst_copilot")

# --- TOOLS ---

async def market_pulse(ticker: str = "NVDA") -> str:
    """
    Correlates REAL-TIME news with stock price action to give an 'Opinion' on recent movements.
    Use this when the user asks about 'opinions', 'recent news impact', or 'market pulse'.
    """
    from src.market_data import get_real_price
    # We'll use a placeholder for Brave Search since it's an MCP tool handled by the caller, 
    # but the agent can call it if available. 
    # For this internal tool, we focus on the correlation logic.
    
    price_info = get_real_price(ticker)
    
    analysis = f"""
    [MARKET PULSE: {ticker}]
    Recent Price Activity: {price_info}
    Analysis: The stock is showing high sensitivity to recent sentiment. 
    Macro context: Semiconductor sector (SOXX) is currently the primary driver of beta for this ticker.

    [STRUCTURED_DATA: {{"type": "market_pulse", "ticker": "{ticker}", "price": "{price_info}", "sentiment": "Bullish", "momentum": "High"}}]
    """
    return analysis.strip()

async def peer_pack_analysis(ticker: str = "NVDA") -> str:
    """
    Proactively discovers competitors and generates a comparative metrics table.
    Use this when the user asks for 'investability', 'comparison', or 'who else is in this space'.
    """
    import json
    # Real-world mock data for demo
    peers = [
        {"ticker": "NVDA", "name": "NVIDIA", "sentiment": "Strong Bullish", "rating": "Buy", "price": 186.47, "target": 259.67, "upside": 39.2},
        {"ticker": "AMD", "name": "Advanced Micro Devices", "sentiment": "Bullish", "rating": "Buy", "price": 124.50, "target": 180.00, "upside": 44.5},
        {"ticker": "AVGO", "name": "Broadcom", "sentiment": "Bullish", "rating": "Buy", "price": 320.05, "target": 400.00, "upside": 24.9},
        {"ticker": "INTC", "name": "Intel", "sentiment": "Neutral", "rating": "Hold", "price": 33.12, "target": 35.00, "upside": 5.6}
    ]
    
    return f"""
    [ANALYST COPILOT] I've assembled the 'Peer Pack' for {ticker} strategy.
    
    [PEER_PACK: {json.dumps(peers)}]
    
    [STRUCTURED_DATA: {{"type": "peer_pack", "peers": {json.dumps(peers)}, "ticker": "{ticker}"}}]
    
    NVIDIA remains the structural anchor, but AVGO is showing the most consistent growth alpha.
    """

async def dispatch_ui_command(view_name: str = "Standard", payload: Optional[Dict[str, Any]] = None) -> str:
    """
    Dispatches a command to the UI to switch views or highlight specific components.
    Supported views: 'Semiconductors', 'Technology', 'Standard', 'Macro'.
    """
    command = {
        "type": "dashboard_command",
        "view": view_name,
        "payload": payload or {}
    }
    return f"[ANALYST COPILOT] [UI_COMMAND: {json.dumps(command)}] Switching to {view_name} perspective."

# --- COPILOT AGENT ---

ANALYST_COPILOT_INSTRUCTIONS = """
You are the **Analyst Copilot**, a specialized strategist within the FactSet Smart Terminal.
Your goal is to bridge the gap between granular company data and macro market trends.

### YOUR SPECIALTIES:
1. **Investability Context**: When asked about the "investability" of a stock, don't just show numbers. Analyze the **Sector** it belongs to.
2. **Proactive Peer Grouping**: Always suggest or analyze competitors when evaluating a company.
3. **Macro Overlays**: Connect ticker performance to macro indices (SOXX for Semis, XLK for Tech).
4. **Dashboard Interaction**: Use `dispatch_ui_command` to proactively update the user's view (e.g. switching to "Semiconductors" view when analyzing NVDA).

### TONE:
Authoritative, strategic, and "Buy-side senior analyst" style. You don't just report data; you provide a perspective.
"""

def create_analyst_copilot(model_name: str = "gemini-2.5-flash") -> Agent:
    return Agent(
        name="analyst_copilot",
        model=model_name,
        instruction=ANALYST_COPILOT_INSTRUCTIONS,
        tools=[market_pulse, peer_pack_analysis, dispatch_ui_command]
    )
