import json
import re
from typing import List, Optional
from pydantic import BaseModel
from .smart_agent import LlmAgent

class VideoNews(BaseModel):
    id: str
    title: str
    url: str
    summary: str
    company: str
    duration: str
    snippet: str
    thumbnail: str

class HubOutput(BaseModel):
    videos: List[VideoNews]
    market_outlook: str

class NewsHubService:
    def __init__(self):
        self.agent = LlmAgent()
        self.cache = {}

    def _extract_video_id(self, url: str) -> Optional[str]:
        # Improved YouTube ID extraction
        reg_exp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
        match = re.match(reg_exp, url)
        if match and len(match.group(7)) == 11:
            return match.group(7)
        return None

    async def fetch_news_hub(self, ticker: str) -> HubOutput:
        # Check cache (session persistence)
        if ticker in self.cache:
            return self.cache[ticker]

        prompt = f"""Find the top 10 most recent (last 7 days) semiconductor financial news YouTube videos for {ticker} (or general semiconductor industry if {ticker} is not a primary player) that are less than 5 minutes long. 

        Focus on major players: NVIDIA, TSMC, AMD, Intel, ASML, ARM, Broadcom.

        For each video, provide:
        1. Title
        2. YouTube URL
        3. A short summary of the financial impact or news
        4. The primary company mentioned
        5. Estimated duration (must be < 5 mins)
        6. A "snippet" - a direct quote or specific detail from the search result description.

        Also include a "market_outlook" field summarizing the overall semiconductor sector sentiment based on these recent results.

        Return the results as a JSON object with a 'videos' array and a 'market_outlook' string.
        """

        response = await self.agent.generate_response(
            prompt, 
            use_search=True,
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "videos": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "url": {"type": "STRING"},
                                "summary": {"type": "STRING"},
                                "company": {"type": "STRING"},
                                "duration": {"type": "STRING"},
                                "snippet": {"type": "STRING"},
                            },
                            "required": ["title", "url", "summary", "company", "duration", "snippet"]
                        }
                    },
                    "market_outlook": {"type": "STRING"}
                },
                "required": ["videos", "market_outlook"]
            }
        )

        try:
            # The agent returns the raw text from the LLM, but we requested JSON schema.
            # LlmAgent.generate_response will return the text content.
            # We need to parse it.
            data = json.loads(response)
            
            videos = []
            for i, item in enumerate(data.get("videos", [])):
                video_id = self._extract_video_id(item.get("url", "")) or f"fallback-{i}"
                videos.append(VideoNews(
                    id=video_id,
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    summary=item.get("summary", ""),
                    company=item.get("company", ""),
                    duration=item.get("duration", ""),
                    snippet=item.get("snippet", ""),
                    thumbnail=f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                ))

            output = HubOutput(
                videos=videos,
                market_outlook=data.get("market_outlook", "No sector sentiment available at this time.")
            )
            
            # Save to cache
            self.cache[ticker] = output
            return output

        except Exception as e:
            print(f"Error parsing News Hub response: {e}")
            return HubOutput(videos=[], market_outlook=f"Error retrieving intelligence for {ticker}.")

    def clear_session(self, ticker: str):
        if ticker in self.cache:
            del self.cache[ticker]
        return {"status": "success", "message": f"Session cleared for {ticker}"}

news_hub_service = NewsHubService()
