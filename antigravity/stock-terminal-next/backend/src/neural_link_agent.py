
import asyncio
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.tools import google_search

class NeuralCard(BaseModel):
    title: str
    snippet: str
    source: str
    url: str
    sentiment: str # "Positive", "Negative", "Neutral"
    timestamp: Optional[str] = None

class NeuralTrends(BaseModel):
    ticker: str
    cards: List[NeuralCard]
    summary: str

# Define the instruction with output schema enforcement via prompt (since simplified ADK use)
NEURAL_AGENT_INSTRUCTION = """
You are a highly advanced Financial Trends Analyzer (Neural Link).
Your goal is to search for the latest news, market sentiment, and trends for a specific stock ticker.
Use Google Search tool to find very recent and relevant information.

Input: A stock ticker (e.g., "TSLA", "GOOGL").

Tasks:
1. Search for latest news, rumors, analyst upgrades/downgrades, and major events for the ticker.
2. Analyze the sentiment of each major story.
3. Return a Structured JSON response with a list of "cards".

Format your FINAL response EXACTLY as this JSON structure (no markdown fences around it if possible, or just the JSON):
{
  "ticker": "TICKER_SYMBOL",
  "summary": "A brief 2-sentence summary of the overall vibe.",
  "cards": [
    {
      "title": "Headline 1",
      "snippet": "Short description of the event...",
      "source": "Source Name (e.g. Bloomberg)",
      "url": "https://...",
      "sentiment": "Positive" | "Negative" | "Neutral",
      "timestamp": "e.g. 2 hours ago"
    },
    ...
  ]
}

Ensure you provide at least 4-6 high-quality cards.
Focus on "Impact News" - things moving the stock.
"""

class NeuralLinkService:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.agent = Agent(
            name="neural_link_agent",
            model=model_name,
            instruction=NEURAL_AGENT_INSTRUCTION,
            description="Neural Link Agent for Live Trends",
            tools=[google_search]
        )
        # We need to initialize runner per request or reuse? 
        # Ideally stateless for simple queries, but Runner requires session.
        from google.adk.sessions import InMemorySessionService
        self.session_service = InMemorySessionService()

    async def get_trends(self, ticker: str) -> NeuralTrends:
        import google.adk as adk
        from google.genai import types
        import secrets
        
        prompt = f"Analyze latest trends for {ticker} stock."
        session_id = secrets.token_hex(4)
        
        # Create session
        await self.session_service.create_session(session_id=session_id, user_id="neural_user", app_name="neural_link")
        
        runner = adk.Runner(app_name="neural_link", agent=self.agent, session_service=self.session_service)
        
        final_text = ""
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        
        try:
            async for event in runner.run_async(user_id="neural_user", session_id=session_id, new_message=msg):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_text += part.text
            
            # Parse result
            text = final_text
            
            # Clean markdown if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
                
            data = json.loads(text)
            return NeuralTrends(**data)
            
        except Exception as e:
            print(f"Neural Link Agent Error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback
            return NeuralTrends(
                ticker=ticker,
                summary="Neural Link unavailable. Check system logs.",
                cards=[]
            )

# Singleton instance
neural_service = NeuralLinkService()
