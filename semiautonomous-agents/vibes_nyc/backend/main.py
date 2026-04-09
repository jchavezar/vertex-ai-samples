"""
Vibes NYC — FastAPI Backend.
Mood-to-venue matching API.
"""
import os
import sys
import asyncio
import time
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Set Vertex AI env vars
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"  # Required for flash-lite models

import vertexai
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="global"  # Flash-lite models require global region
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Add agent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

app = FastAPI(title="Vibes NYC API", description="Mood-to-venue matching for NYC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    mood_query: str  # "cozy morning, contemporary, good coffee"
    location: str = "Lower East Side, NYC"
    time_of_day: str = "morning"  # morning | afternoon | evening | night
    open_now: bool = True
    vibe_dims: Optional[dict] = None  # Optional slider overrides


class VenueDetailRequest(BaseModel):
    yelp_id: str
    venue_name: str
    neighborhood: str


MODEL_NAME = "gemini-3.1-flash-lite-preview"
MODEL_REGION = "global"

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "vibes-nyc",
        "model": MODEL_NAME,
        "region": MODEL_REGION
    }


@app.post("/api/search")
async def search_venues(body: SearchRequest):
    """
    Main search endpoint.
    Takes mood query + location, returns ranked venues with vibe profiles.
    """
    from agent import run_venue_search
    from vibe_engine import compute_underground_score, tag_accessibility

    results = await run_venue_search(
        mood_query=body.mood_query,
        location=body.location,
        time_of_day=body.time_of_day,
        open_now=body.open_now
    )

    # Apply REAL scoring algorithm (not LLM hallucination)
    for venue in results:
        venue["underground_score"] = compute_underground_score(venue)
        venue["accessibility"] = tag_accessibility(venue)
        # Sanitize LLM string-ified None values
        if venue.get("price") in (None, "None", "null", ""):
            venue["price"] = ""
        if venue.get("hours") in (None, "None", "null", "n/a", "N/A"):
            venue["hours"] = None

    # Re-sort by actual underground score
    results.sort(key=lambda v: v.get("underground_score", 0), reverse=True)

    return {
        "venues": results,
        "location": body.location,
        "query": body.mood_query,
        "count": len(results),
        "model": MODEL_NAME,
        "region": MODEL_REGION
    }


@app.get("/api/venue/{place_id}")
async def venue_detail(place_id: str):
    """Full venue detail with vibe profile and web signals."""
    from places_client import GooglePlacesClient

    client = GooglePlacesClient()
    details = await client.get_details(place_id)

    if not details:
        return {"error": "Venue not found"}

    # Add computed vibe profile
    from vibe_engine import synthesize_vibe_profile
    profile = synthesize_vibe_profile(details)

    return profile


@app.post("/api/search/deep")
async def deep_search(body: SearchRequest):
    """
    Deep search using multi-agent collaboration:
    1. VenueSearchAgent (Gemini) - Foursquare search
    2. WebSignalsAgent (Gemini) - Google Search for Reddit/blogs
    3. VibeAnalystAgent (Claude) - Sentiment analysis

    This demonstrates cross-model agent collaboration.
    """
    from multi_agent import run_multi_agent_search

    result = await run_multi_agent_search(
        mood_query=body.mood_query,
        location=body.location,
        include_web_signals=True,
        include_claude_analysis=True
    )

    return {
        **result,
        "search_type": "multi-agent",
        "agents": result.get("agents_used", [])
    }


@app.post("/api/mood")
async def quick_mood(body: dict):
    """Quick Gemini response explaining the vibe for a location/time combo."""
    location = body.get("location", "Manhattan")
    time_of_day = body.get("time_of_day", "morning")

    # Simple response without full agent query
    vibe_descriptions = {
        "morning": "quiet energy, locals grabbing coffee before work, soft sunlight",
        "afternoon": "steady flow of remote workers, lunch crowds thinning out",
        "evening": "after-work crowds, cocktail hour vibes, golden hour through windows",
        "night": "intimate lighting, creative types emerging, neighborhood regulars"
    }

    vibe = vibe_descriptions.get(time_of_day, "eclectic mix of locals and visitors")

    return {
        "location": location,
        "time_of_day": time_of_day,
        "vibe_description": f"Here's the vibe in {location} during {time_of_day}: {vibe}."
    }


def _verify_signal(signal: dict, venue_name: str) -> dict:
    """Add verified flag based on URL and content checks."""
    venue_lower = venue_name.lower()
    quote_lower = signal.get("quote", "").lower()
    url = signal.get("url", "") or ""

    checks = {
        "has_url": bool(url),
        "url_domain_match": any(d in url for d in ["reddit.com", "instagram.com"]),
        "venue_mentioned": venue_lower in quote_lower or any(
            word in quote_lower for word in venue_lower.split() if len(word) > 2
        ),
    }
    signal["verified"] = all(checks.values())
    return signal


@app.post("/api/venue/deep-vibe")
async def venue_deep_vibe(body: dict):
    """
    Generate deep vibe profile for a venue:
    - Radar scores across 5 dimensions (Gemini 2.5 Flash + real reviews)
    - "Who Goes Here" crowd archetypes (Gemini)
    - Neighborhood signals (Reddit + Instagram via Google Search grounding)
    - Provenance: per-dimension explanation of scoring basis
    """
    import json, re, asyncio
    from google import genai
    from google.genai.types import GenerateContentConfig
    sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
    from reddit_client import search_venue_mentions
    from instagram_client import search_venue_instagram

    venue_name = body.get("name", "")
    vibe_tags = body.get("vibe_tags", [])
    vibe_summary = body.get("vibe_summary", "")
    underground_score = body.get("underground_score", 50)
    categories = body.get("categories", [])
    reviews = body.get("reviews", [])

    # Format review text for the prompt
    if reviews:
        review_text = "\n".join(f"- {r[:300]}" for r in reviews[:5] if r)
    else:
        review_text = "(No customer reviews available)"

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location="us-central1",
    )

    prompt = f"""You are a NYC neighborhood expert. Generate a deep vibe profile for this venue.

Venue: {venue_name}
Category: {', '.join(categories)}
Vibe tags: {', '.join(vibe_tags)}
Summary: {vibe_summary}
Underground score: {underground_score}/100

Real customer reviews:
{review_text}

Based on the venue info AND the real reviews above, return ONLY valid JSON with this exact structure:
{{
  "radar": {{
    "energy": <0-100, 0=calm/contemplative, 100=electric/buzzing>,
    "sound": <0-100, 0=silent, 50=lo-fi/ambient, 100=live music/loud>,
    "aesthetic": <0-100, 0=bare/functional, 100=highly curated/designed>,
    "crowd": <0-100, 0=solo regulars/quiet locals, 100=social scene crowd>,
    "accessibility": <0-100, 0=impossible to get in, 100=walk-in anytime>
  }},
  "archetypes": [
    {{"emoji": "...", "title": "...", "description": "one vivid sentence about this person type"}},
    {{"emoji": "...", "title": "...", "description": "one vivid sentence about this person type"}},
    {{"emoji": "...", "title": "...", "description": "one vivid sentence about this person type"}}
  ],
  "provenance": {{
    "energy": "one-line reason based on reviews or venue data",
    "sound": "one-line reason based on reviews or venue data",
    "aesthetic": "one-line reason based on reviews or venue data",
    "crowd": "one-line reason based on reviews or venue data",
    "accessibility": "one-line reason based on reviews or venue data"
  }}
}}

Rules:
- Radar scores should be honest — low energy spots get low energy scores
- Archetypes are vivid NYC character sketches, hyper-specific (not generic)
- Provenance must cite specific review quotes or venue facts that justify each score"""

    async def run_gemini():
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=GenerateContentConfig(temperature=0.7),
            )
            text = response.text.strip() if response.text else ""
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            print(f"[Gemini] deep-vibe error: {e}")
        return None

    # Run Gemini, Reddit, and Instagram in parallel — zero extra latency
    gemini_result, reddit_signals, instagram_signals = await asyncio.gather(
        run_gemini(),
        search_venue_mentions(venue_name, max_results=3),
        search_venue_instagram(venue_name, max_results=3),
    )

    if not gemini_result:
        return {"error": "Failed to generate vibe profile", "radar": None}

    profile = gemini_result

    # Combine and verify all social signals
    all_signals = []
    for s in (reddit_signals or []):
        s["platform"] = "reddit"
        all_signals.append(_verify_signal(s, venue_name))
    for s in (instagram_signals or []):
        s["platform"] = "instagram"
        all_signals.append(_verify_signal(s, venue_name))

    profile["neighborhood_signals"] = all_signals
    profile["signals_source"] = "live" if all_signals else "none"

    return profile


# ─── Local Events ────────────────────────────────────────────────────────────

_events_cache: dict[str, tuple[float, list]] = {}
_EVENTS_TTL = 1800  # 30 minutes


@app.get("/api/events")
async def get_local_events(location: str = "NYC"):
    """
    Discover hyper-local, culturally interesting events in the next 5 days.
    Uses Gemini 2.5 Flash + Google Search grounding.
    Results cached per location for 30 minutes.
    """
    from events_client import search_local_events

    cache_key = location.lower().strip()
    now = time.time()

    # Check cache
    if cache_key in _events_cache:
        ts, cached = _events_cache[cache_key]
        if now - ts < _EVENTS_TTL:
            return {
                "events": cached,
                "location": location,
                "count": len(cached),
                "cached": True,
            }

    # Cache miss — call Gemini with Google Search grounding
    events = await search_local_events(location, max_results=8)
    _events_cache[cache_key] = (now, events)

    return {
        "events": events,
        "location": location,
        "count": len(events),
        "cached": False,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
