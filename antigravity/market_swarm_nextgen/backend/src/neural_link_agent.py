
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

class DeepDiveAnalysis(BaseModel):
    category: str = Field(description="The category of analysis (Profile, Valuation, Dividends, Consensus)")
    ticker: str = Field(description="The ticker symbol analyzed")
    content: str = Field(description="A detailed, high-quality, professional financial analysis in markdown format. Use bolding for key figures and bullet points for readability. Be very specific and data-driven.")
    model_used: str = Field(description="Name of the model used")

NEURAL_DEEP_DIVE_INSTRUCTION = """
You are a helpful financial assistant.
Your goal is to provide a deep-dive analysis for a specific category (Profile, Valuation, Dividends, or Consensus).
Use Google Search to find the latest, most relevant financial data and analyst reports.
Be precise and data-driven.
Format your response as valid Markdown within the JSON structure.
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
        # NEW: Deep Dive Agent using gemini-2.5-flash-lite for speed/cost balance
        # NEW: Deep Dive Agent using gemini-2.5-flash-lite for speed/cost balance
        self.deep_dive_agent = LlmAgent(
            name="deep_dive_agent",
            model="gemini-2.5-flash-lite",
            instruction=NEURAL_DEEP_DIVE_INSTRUCTION,
            tools=[google_search],
            # DISABLED schema to avoid conflict with Search tool (Controlled Generation not supported with Search)
            # output_schema=DeepDiveAnalysis,
            # output_key="deep_dive_result"
        )

        from google.adk.sessions.sqlite_session_service import SqliteSessionService
        self.session_service = SqliteSessionService(db_path="neural_link_sessions.db")

    async def _run_agent_query(self, agent: LlmAgent, prompt: str, output_key: Optional[str] = None) -> Any:
        import google.adk as adk
        from google.genai import types
        import secrets
        
        session_id = f"neural_{secrets.token_hex(4)}"
        await self.session_service.create_session(session_id=session_id, user_id="system", app_name="neural_link")
        runner = adk.Runner(app_name="neural_link", agent=agent, session_service=self.session_service)
        
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        try:
            full_text = ""
            async for chunk in runner.run_async(user_id="system", session_id=session_id, new_message=msg):
                try:
                    # Check for content.parts (GenerateContentResponse or Step)
                    if hasattr(chunk, 'content') and chunk.content and chunk.content.parts:
                         full_text += chunk.content.parts[0].text
                    # Fallback for other types
                    elif hasattr(chunk, 'parts') and chunk.parts:
                         full_text += chunk.parts[0].text
                    elif hasattr(chunk, 'text'):
                         full_text += chunk.text
                except:
                    pass
            
            # Retrieve from session state
            session = await self.session_service.get_session(session_id=session_id, app_name="neural_link", user_id="system")
            
            if output_key and session and output_key in session.state:
                return session.state[output_key]
            
            # Fallback
            if full_text:
                return full_text
            
            # Try to get from session history if needed (if full_text capture failed)
            # Inspecting session structure
            # if hasattr(session, 'history'): ...
                    
        except Exception as e:
            print(f"Agent {agent.name} failed: {e}")
            import traceback
            traceback.print_exc()
        return {}
                    


    async def get_trends(self, ticker: str) -> Dict[str, Any]:
        # PARALLEL EXECUTION for latency reduction
        news_task = self._run_agent_query(self.news_agent, f"Official news and analyst moves for {ticker}", "news_result")
        rumor_task = self._run_agent_query(self.rumor_agent, f"Social rumors, leaks, and emerging sentiment for {ticker}", "rumor_result")
        
        news_res, rumor_res = await asyncio.gather(news_task, rumor_task)
        
        # Robust extraction for News Cards
        cards = news_res.get("cards", []) if isinstance(news_res, dict) else []
        if not cards and isinstance(news_res, list):
            cards = news_res
        elif not cards and isinstance(news_res, dict):
            for k in ["data", "items", "result"]:
                if k in news_res:
                    cards = news_res[k]
                    break

        # Robust extraction for Rumors
        rumors = rumor_res.get("rumors", []) if isinstance(rumor_res, dict) else []
        if not rumors and isinstance(rumor_res, list):
            rumors = rumor_res
        elif not rumors and isinstance(rumor_res, dict):
            for k in ["data", "items", "result"]:
                if k in rumor_res:
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

    async def get_deep_dive(self, ticker: str, category: str) -> Dict[str, Any]:
        # Explicit JSON instruction since we disabled schema enforcement
        prompt = (
            f"Perform a deep dive analysis for {ticker} focusing specifically on {category}. "
            f"Provide detailed insights, numbers, and forward-looking analysis. "
            f"Use Google Search to find real-time data or strictly follow your internal knowledge if search fails. "
            f"You MUST respond with valid raw JSON (no markdown block markers like ```json) using strictly this structure: "
            f'{{"category": "{category}", "ticker": "{ticker}", "content": "your detailed markdown analysis here", "model_used": "gemini-2.5-flash-lite"}}'
        )
        
        # Call without output_key to get raw text
        result_text = await self._run_agent_query(self.deep_dive_agent, prompt, output_key=None)
        
        try:
            if isinstance(result_text, str):
                # cleaning markdown code blocks if present
                clean_text = result_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                return json.loads(clean_text)
            elif isinstance(result_text, dict):
                return result_text
                
        except json.JSONDecodeError:
            print(f"Failed to parse Deep Dive JSON: {result_text}")
        except Exception as e:
            print(f"Deep Dive Error: {e}")
        
        # Fallback
        return {
            "category": category,
            "ticker": ticker,
            "content": f"Neural link failed to converge on {category} for {ticker}. (Parse Error)",
            "model_used": "gemini-2.5-flash-lite"
        }

# Singleton instance
neural_service = NeuralLinkService()
