
import asyncio
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class NeuralCard(BaseModel):
    title: str = Field(description="The headline of the news item")
    snippet: str = Field(description="A concise summary of the news item")
    source: str = Field(description="The publisher or source name")
    url: str = Field(description="The direct link to the article")
    sentiment: str = Field(description="Sentiment of the news: 'Positive', 'Negative', or 'Neutral'")
    timestamp: Optional[str] = Field(None, description="Time since published, e.g. '2h ago'")

class RumorCard(BaseModel):
    source: str = Field(description="Social source, e.g. 'Reddit/r/WallStreetBets', 'X/Twitter'")
    content: str = Field(description="The specific rumor or speculative claim")
    impact: str = Field(description="Impact level: 'High', 'Medium', 'Low'")
    vibe: str = Field(description="The vibe of the rumor, e.g. 'LEAKED', 'SPECULATIVE', 'HYPE'")
    url: Optional[str] = Field(None, description="Link to the social post if available")

class NewsOutput(BaseModel):
    cards: List[NeuralCard]
    summary: str = Field(description="A one-sentence institutional synthesis of the news")
    market_vibe: str = Field(description="Punchy market vibe, e.g. 'BULLISH SURGE'")

class RumorOutput(BaseModel):
    rumors: List[RumorCard]

# --- INSTRUCTIONS ---

NEURAL_NEWS_INSTRUCTION = """
You are a Financial News Synthesizer.
Search for the latest OFFICIAL news and major analyst moves for the ticker.
Provide a high-quality synthesis of current market sentiment.
Return your analysis as a structured NewsOutput.
"""

NEURAL_RUMOR_INSTRUCTION = """
You are a Social Intelligence Scout.
Focus on: Reddit, X (Twitter), StockTwits, and niche tech blogs.
Find: LEAKS, RUMORS, and emerging social sentiment that isn't in mainstream news yet.
Be edgy but analytical.
Return your findings as a structured RumorOutput.
"""

class NeuralLinkService:
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.news_agent = LlmAgent(
            name="news_agent",
            model=model_name,
            instruction=NEURAL_NEWS_INSTRUCTION,
            tools=[google_search],
            output_schema=NewsOutput,
            output_key="news_result"
        )
        self.rumor_agent = LlmAgent(
            name="rumor_agent",
            model=model_name,
            instruction=NEURAL_RUMOR_INSTRUCTION,
            tools=[google_search],
            output_schema=RumorOutput,
            output_key="rumor_result"
        )
        from google.adk.sessions.sqlite_session_service import SqliteSessionService
        self.session_service = SqliteSessionService(db_path="neural_link_sessions.db")

    async def _run_agent_query(self, agent: LlmAgent, prompt: str, output_key: str) -> Dict[str, Any]:
        import google.adk as adk
        from google.genai import types
        import secrets
        
        session_id = f"neural_{secrets.token_hex(4)}"
        await self.session_service.create_session(session_id=session_id, user_id="system", app_name="neural_link")
        runner = adk.Runner(app_name="neural_link", agent=agent, session_service=self.session_service)
        
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        try:
            async for _ in runner.run_async(user_id="system", session_id=session_id, new_message=msg):
                pass
            
            # Retrieve from session state
            session = await self.session_service.get_session(session_id=session_id, app_name="neural_link", user_id="system")
            if session and output_key in session.state:
                return session.state[output_key]
        except Exception as e:
            print(f"Agent {agent.name} failed: {e}")
        return {}

    async def get_trends(self, ticker: str) -> Dict[str, Any]:
        # PARALLEL EXECUTION for latency reduction
        news_task = self._run_agent_query(self.news_agent, f"Official news and analyst moves for {ticker}", "news_result")
        rumor_task = self._run_agent_query(self.rumor_agent, f"Social rumors, leaks, and emerging sentiment for {ticker}", "rumor_result")
        
        news_res, rumor_res = await asyncio.gather(news_task, rumor_task)
        
        # Robust extraction for News Cards
        cards = news_res.get("cards", [])
        if not cards and isinstance(news_res, list):
            cards = news_res
        elif not cards:
            for k in ["data", "items", "result"]:
                if isinstance(news_res, dict) and k in news_res:
                    cards = news_res[k]
                    break

        # Robust extraction for Rumors
        rumors = rumor_res.get("rumors", [])
        if not rumors and isinstance(rumor_res, list):
            rumors = rumor_res
        elif not rumors:
            for k in ["data", "items", "result"]:
                if isinstance(rumor_res, dict) and k in rumor_res:
                    rumors = rumor_res[k]
                    break

        # Combine into the format expected by the frontend
        return {
            "ticker": ticker,
            "cards": cards,
            "rumors": rumors,
            "summary": news_res.get("summary", "Neural pulse synchronization complete.") if isinstance(news_res, dict) else "Neural pulse synchronization complete.",
            "market_vibe": news_res.get("market_vibe", "NEUTRAL") if isinstance(news_res, dict) else "NEUTRAL"
        }

# Singleton instance
neural_service = NeuralLinkService()
