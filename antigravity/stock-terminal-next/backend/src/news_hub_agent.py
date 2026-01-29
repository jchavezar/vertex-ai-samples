import json
import re
import asyncio
import secrets
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class VideoNews(BaseModel):
    id: str = Field(description="YouTube Video ID")
    title: str = Field(description="The headline of the video news")
    url: str = Field(description="The direct link to the YouTube video")
    summary: str = Field(description="A concise summary of the financial impact")
    company: str = Field(description="The primary company mentioned")
    duration: str = Field(description="Estimated duration of the video")
    snippet: str = Field(description="A direct quote or detail from the source")
    thumbnail: str = Field(description="YouTube thumbnail URL")

class HubOutput(BaseModel):
    videos: List[VideoNews]
    market_outlook: str = Field(description="One-sentence sector sentiment")

class NewsHubService:
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.agent = LlmAgent(
            name="news_hub_agent",
            model=model_name,
            instruction="""
            You are a Semiconductor Financial Intelligence Scout.
            Your task is to find recent YouTube videos about semiconductor stocks (NVDA, TSMC, AMD, etc.).
            Prioritize short, high-impact news videos (< 5 mins).
            Search for the latest news and summarize the financial impact.
            Return the results as a structured HubOutput.
            """,
            tools=[google_search],
            output_schema=HubOutput,
            output_key="hub_result"
        )
        from google.adk.sessions.sqlite_session_service import SqliteSessionService
        self.session_service = SqliteSessionService(db_path="news_hub_sessions.db")
        self.cache = {}

    def _extract_video_id(self, url: str) -> Optional[str]:
        reg_exp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
        match = re.match(reg_exp, url)
        if match and len(match.group(7)) == 11:
            return match.group(7)
        return None

    async def get_summarized_news(self, ticker: str) -> Dict[str, Any]:
        # Check cache
        if ticker in self.cache:
            return self.cache[ticker]

        import google.adk as adk
        from google.genai import types
        
        session_id = f"hub_{secrets.token_hex(4)}"
        await self.session_service.create_session(session_id=session_id, user_id="system", app_name="news_hub")
        runner = adk.Runner(app_name="news_hub", agent=self.agent, session_service=self.session_service)
        
        prompt = f"""Find the top 8 most recent (last 7 days) financial news YouTube videos for {ticker} (semiconductor context).
        Prioritize videos under 5 minutes.
        For each video, provide title, YouTube URL, impact summary, and duration.
        Also provide a one-sentence 'market_outlook' for the semiconductor sector based on these findings.
        """
        
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        try:
            async for _ in runner.run_async(user_id="system", session_id=session_id, new_message=msg):
                pass
            
            # Retrieve from session state
            session = await self.session_service.get_session(session_id=session_id, app_name="news_hub", user_id="system")
            if session and "hub_result" in session.state:
                raw_data = session.state["hub_result"]
                
                # Format for frontend (add thumbnails)
                videos = []
                for i, v in enumerate(raw_data.get("videos", [])):
                    video_id = self._extract_video_id(v.get("url", "")) or f"v-{i}"
                    videos.append({
                        **v,
                        "id": video_id,
                        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                    })
                
                result = {
                    "videos": videos,
                    "market_outlook": raw_data.get("market_outlook", "Outlook stabilized.")
                }
                self.cache[ticker] = result
                return result

        except Exception as e:
            print(f"News Hub Agent failed: {e}")
            
        return {"videos": [], "market_outlook": f"Intelligence gathering offline for {ticker}."}

    def clear_session(self, ticker: str):
        if ticker in self.cache:
            del self.cache[ticker]
        return {"status": "success"}

news_hub_service = NewsHubService()
