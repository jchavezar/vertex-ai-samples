"""
VenueResearchAgent — ADK Agent for mood-to-venue matching.
Uses Yelp Fusion + google_search for organic web signals.
"""
import os
import sys
import json
import re
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# CRITICAL: Set env vars BEFORE any ADK imports
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"  # Required for flash-lite models

import vertexai
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="global"  # Flash-lite models require global region
)

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

try:
    from .places_client import GooglePlacesClient
    from .nominatim_client import NominatimClient
except ImportError:
    from places_client import GooglePlacesClient
    from nominatim_client import NominatimClient

# Initialize clients at module level
places_client = GooglePlacesClient()
nominatim_client = NominatimClient()


async def search_venues(query: str, location: str) -> dict:
    """
    Search Google Places for venues matching the mood query in the given location.
    Returns a list of venues with name, address, rating, review_count, price, categories, hours.
    Use this first to get candidate venues.

    Args:
        query: Search term describing what you're looking for (e.g., "cozy coffee shop", "craft cocktails")
        location: Neighborhood or area (e.g., "Williamsburg, Brooklyn", "Lower East Side, NYC")

    Returns:
        Dictionary with venues list, count, and location
    """
    lat_lon = await nominatim_client.geocode(location)
    venues = await places_client.search(query=query, lat=lat_lon[0], lon=lat_lon[1])
    return {
        "venues": venues,
        "location": location,
        "count": len(venues),
        "coordinates": {"lat": lat_lon[0], "lon": lat_lon[1]}
    }


AGENT_INSTRUCTION = """You are a Manhattan underground venue expert with deep knowledge of NYC neighborhoods.
Your goal: find venues that match a user's mood — not the most popular spots, but the most resonant ones.

When given a mood query and location:

1. Call search_venues to get candidate venues from Foursquare
2. Based on venue categories, review count, and price level, synthesize a vibe profile for each:
   - aesthetic (contemporary/cozy/industrial/minimal/eclectic/vintage)
   - energy (1-10: 1=very calm, 10=very buzzing)
   - sound (silent/lo-fi/jazz/acoustic/live/energetic)
   - crowd_vibe (neighborhood regulars/creative scene/mixed/tourist-heavy)
   - accessibility (walk-in/usually available/book ahead/impossible)
   - underground_score (0-100): start at 100, penalize chains (-60), high review count (>2000: -50, >1000: -35, >500: -20), reward low reviews + high rating (+15)
3. Rank by vibe match to the user's mood, NOT by Yelp rating
4. Return top 6-8 venues with full vibe profiles and a 2-sentence vibe summary each

KNOWN CHAINS TO PENALIZE: starbucks, dunkin, mcdonald, subway, chipotle, sweetgreen, blue bottle, gregorys, joe coffee

IMPORTANT:
- Prioritize walk-in accessible spots with interesting local crowd
- Hidden gems with <100 reviews but high ratings are valuable
- Coffee shops/cafes = cozy, lo-fi, quiet energy
- Cocktail bars = intimate, moody, creative crowd
- Breweries = industrial, buzzing, mixed crowd

OUTPUT FORMAT:
Return ONLY a JSON array (no markdown, no explanation) of venue objects with these fields:
- name, address, yelp_id, rating, review_count, price, photos, categories
- coordinates (copy from input: {latitude, longitude})
- underground_score (0-100)
- vibe_tags (array of 3-5 aesthetic words)
- accessibility ("walk-in" or "book ahead")
- vibe_summary (2 sentences describing the feel)
- best_time (when to visit)
"""


root_agent = LlmAgent(
    name="VenueResearchAgent",
    model="gemini-3.1-flash-lite-preview",  # Fast lite model
    description="NYC underground venue expert that matches mood to place",
    instruction=AGENT_INSTRUCTION,
    tools=[search_venues]
)


async def run_venue_search(
    mood_query: str,
    location: str,
    time_of_day: str = "morning",
    open_now: bool = True
) -> list[dict]:
    """
    Run the venue search agent and return ranked results.

    Args:
        mood_query: Natural language mood description
        location: Neighborhood or area
        time_of_day: morning/afternoon/evening/night
        open_now: Filter to open venues

    Returns:
        List of venue dicts with vibe profiles, sorted by underground score
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="vibes_nyc",
        user_id="user_1"
    )

    runner = Runner(
        agent=root_agent,
        app_name="vibes_nyc",
        session_service=session_service
    )

    user_message = f"""Find venues for: {mood_query}
Location: {location}
Time of day: {time_of_day}
Currently open: {open_now}

Search Yelp first, then check Reddit/blogs for the top candidates. Return ranked venues with vibe profiles."""

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)]
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text

    # Parse JSON from response
    try:
        # Try to find JSON array in response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            venues = json.loads(json_match.group())
            # Sort by underground score descending
            venues.sort(key=lambda v: v.get("underground_score", 0), reverse=True)
            return venues
    except json.JSONDecodeError:
        pass

    # Return empty if parsing fails
    return []


__all__ = ["root_agent", "run_venue_search"]
