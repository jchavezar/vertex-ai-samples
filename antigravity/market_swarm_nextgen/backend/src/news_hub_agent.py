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
            You are a Financial Video Intelligence Scout.
            Your task is to find REAL YouTube videos about specific stock tickers.
            
            STRICT RULES:
            1. You MUST call `google_search` to find news.
            2. You ONLY include videos that appear in the `google_search` results.
            3. You NEVER invent or hallucinate YouTube URLs or Video IDs.
            4. If a search result is not a direct YouTube link, DO NOT include it.
            5. The 'url' MUST be a real link from the search results.
            6. The 'id' MUST be the actual 11-character YouTube video ID extracted from that link.
            7. Return the results as a structured HubOutput.
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
        
        import datetime
        prompt = f"""Search for the 8 most recent (last 7 days) REAL financial news YouTube videos about {ticker} stock.
        
        Use `google_search` with a query like 'youtube news {ticker} stock analysis {datetime.datetime.now().strftime('%Y-%m-%d')}'
        
        CRITICAL: 
        - Only include videos where you have a valid youtube.com/watch or youtu.be URL.
        - The 'id' field MUST be the real 11-char ID (e.g., 'ABCdef123GH').
        - If you find no real results, return an empty list.
        """
        
        msg = types.Content(role="user", parts=[types.Part(text=prompt)])
        try:
            async for _ in runner.run_async(user_id="system", session_id=session_id, new_message=msg):
                pass
            
            # Retrieve from session state
            session = await self.session_service.get_session(session_id=session_id, app_name="news_hub", user_id="system")
            if session and "hub_result" in session.state:
                raw_data = session.state["hub_result"]
                print(f"DEBUG: News Hub Raw Data for {ticker}: {json.dumps(raw_data, indent=2)}")
                
                videos = []
                for i, v in enumerate(raw_data.get("videos", [])):
                    raw_id = v.get("id", "")
                    url = v.get("url", "")
                    
                    # Ensure we have a valid ID
                    video_id = self._extract_video_id(url) or raw_id
                    
                    if not video_id or len(video_id) != 11:
                        # Skip or try to fix if it's a common hallucination
                        if "v-" in str(video_id): continue 
                        continue

                    videos.append({
                        **v,
                        "id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
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
