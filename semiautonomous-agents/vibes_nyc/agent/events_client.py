"""
Local events discovery via Gemini + Google Search grounding.
Finds hyper-local, culturally interesting events happening in NYC.
Same pattern as reddit_client.py / instagram_client.py.
"""
import os
import json
import re
import asyncio
from datetime import datetime, timedelta


async def search_local_events(
    location: str = "NYC",
    max_results: int = 8,
) -> list[dict]:
    """
    Find real upcoming hyper-local events using Gemini with Google Search grounding.

    Args:
        location: NYC neighborhood or area (e.g. "Williamsburg, Brooklyn")
        max_results: Max events to return

    Returns:
        List of dicts with name, date, time, venue, neighborhood, description,
        category, url, source. Empty list if nothing found.
    """
    try:
        from google import genai
        from google.genai.types import Tool, GoogleSearch, GenerateContentConfig

        client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location="us-central1",
        )

        today = datetime.now().strftime("%B %d, %Y")
        end_date = (datetime.now() + timedelta(days=5)).strftime("%B %d, %Y")

        prompt = f"""Search for unique, culturally interesting events happening in or near {location}, New York City in the next 5 days (from {today} to {end_date}).

Focus on:
- Pop-up events, art installations, immersive experiences
- Food/drink events, tastings, pop-up restaurants, supper clubs
- Community gatherings, block parties, street fairs
- Gallery openings, film screenings, book launches
- Public art, projections, video mappings, interactive exhibits
- Underground/indie music shows, comedy, spoken word, DJ sets
- Unique one-time happenings, farewells, launches, unveilings

Do NOT include:
- Major Broadway shows or long-running productions
- Regular sporting events (Yankees, Knicks, Mets, etc.)
- Large mainstream concerts at MSG, Barclays Center, or similar arenas
- Generic weekly farmers markets (unless special edition)
- Recurring bar trivia or standard open mic nights

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "name": "Event Name",
    "date": "Apr 8" or "Apr 8-10",
    "time": "7 PM" or "All day" or null,
    "venue": "Venue or location name",
    "neighborhood": "East Village" or "Williamsburg" etc,
    "description": "One vivid sentence, max 120 chars",
    "category": "art" | "food" | "music" | "community" | "film" | "pop-up",
    "url": "source URL if found, else null",
    "source": "TimeOut NYC" | "Reddit" | "Eventbrite" | "SecretNYC" | etc.
  }}
]

IMPORTANT:
- Only include real, confirmed events with actual dates
- Do NOT fabricate events — if you find fewer than {max_results}, return fewer
- If no events found, return []
- Prioritize unique/underground over mainstream"""

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[Tool(google_search=GoogleSearch())],
                    temperature=0.2,
                ),
            ),
        )

        text = response.text.strip() if response.text else ""
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if not match:
            print(f"[Events/Search] No JSON array for '{location}' — no results found")
            return []

        results = json.loads(match.group())
        valid = [
            r for r in results
            if isinstance(r, dict) and r.get("name") and r.get("date")
        ]
        print(f"[Events/Search] {len(valid)} events for '{location}'")
        return valid[:max_results]

    except Exception as e:
        print(f"[Events/Search] Error: {e}")
        return []
