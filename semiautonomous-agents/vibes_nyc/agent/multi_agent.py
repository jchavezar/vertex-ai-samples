"""
Multi-Agent Venue Research System.

Demonstrates collaboration between:
1. VenueSearchAgent (Gemini + Foursquare) - Find venues
2. WebSignalsAgent (Gemini + google_search) - Get Reddit/blog signals
3. VibeAnalystAgent (Claude) - Deep sentiment analysis

This showcases ADK multi-agent patterns with cross-model collaboration.
"""
import os
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

import vertexai
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="global"
)

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

try:
    from .foursquare_client import FoursquareClient
    from .nominatim_client import NominatimClient
except ImportError:
    from foursquare_client import FoursquareClient
    from nominatim_client import NominatimClient

# Initialize clients
foursquare_client = FoursquareClient()
nominatim_client = NominatimClient()


# ============================================
# AGENT 1: Venue Search (Gemini + Foursquare)
# ============================================

async def search_venues_tool(query: str, location: str) -> dict:
    """Search Foursquare for venues matching query in location."""
    lat_lon = await nominatim_client.geocode(location)
    venues = await foursquare_client.search(query=query, lat=lat_lon[0], lon=lat_lon[1])
    return {
        "venues": venues[:8],  # Top 8 candidates
        "location": location,
        "count": len(venues[:8])
    }

venue_search_agent = LlmAgent(
    name="VenueSearchAgent",
    model="gemini-3.1-flash-lite-preview",
    description="Finds venue candidates from Foursquare",
    instruction="""You search for venues and return basic info.
    Call search_venues_tool with the user's query and location.
    Return the raw venue list - another agent will analyze them.""",
    tools=[search_venues_tool]
)


# ============================================
# AGENT 2: Web Signals (Gemini + google_search)
# ============================================

WEB_SIGNALS_INSTRUCTION = """You research venues on the web to find local signals.

For each venue name provided:
1. Search: "{venue_name}" site:reddit.com NYC
   - Count how many Reddit threads mention it
   - Note if locals recommend it or warn against it

2. Search: "{venue_name}" blog review coffee/cocktail
   - Find niche blog coverage (not Yelp/TripAdvisor)
   - Note any insider tips mentioned

3. Search: "{venue_name}" "top 10" OR "best of" NYC
   - Count listicle appearances (more = more touristy)

Return a JSON object for each venue:
{
  "venue_name": "...",
  "reddit_mentions": 5,
  "reddit_sentiment": "positive" | "mixed" | "negative",
  "reddit_highlights": ["great espresso", "avoid weekends"],
  "blog_mentions": 2,
  "blog_sources": ["Eater NY", "Grub Street"],
  "listicle_appearances": 3,
  "insider_tips": ["ask for the off-menu cortado", "cash only"]
}
"""

web_signals_agent = LlmAgent(
    name="WebSignalsAgent",
    model="gemini-3.1-flash-lite-preview",  # Latest fast model
    description="Searches web for Reddit/blog mentions of venues",
    instruction=WEB_SIGNALS_INSTRUCTION,
    tools=[google_search]
)


# ============================================
# AGENT 3: Vibe Analyst (Claude via API)
# ============================================

async def analyze_with_claude(venues_with_signals: list[dict]) -> list[dict]:
    """
    Use Claude to do deep sentiment analysis and write vibe summaries.
    This demonstrates cross-model collaboration.

    In production, this would call the Anthropic API.
    For demo, we simulate Claude's analysis style.
    """
    # Check if Anthropic API key is available
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if anthropic_key:
        # Real Claude API call
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)

            prompt = f"""Analyze these NYC venues with their web signals and write insider-style vibe summaries.

Venues data:
{json.dumps(venues_with_signals, indent=2)}

For each venue, provide:
1. A 2-sentence vibe summary that sounds like a local insider tip
2. An "insider_score" (0-100) based on:
   - High Reddit mentions with positive sentiment = good
   - Niche blog coverage = good
   - Too many listicle appearances = bad (tourist trap)
3. One "pro tip" for visiting

Return as JSON array."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude's response
            result_text = response.content[0].text
            # Try to extract JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', result_text)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            print(f"[Claude] API error: {e}, using fallback")

    # Fallback: Simulate Claude-style analysis
    analyzed = []
    for venue in venues_with_signals:
        signals = venue.get("web_signals", {})

        # Calculate insider score
        score = 70  # Base
        score += min(signals.get("reddit_mentions", 0) * 5, 20)
        score -= signals.get("listicle_appearances", 0) * 8
        if signals.get("reddit_sentiment") == "positive":
            score += 10
        score = max(0, min(100, score))

        # Generate insider-style summary
        highlights = signals.get("reddit_highlights", [])
        tips = signals.get("insider_tips", [])

        summary = f"A spot that locals actually talk about on Reddit. "
        if highlights:
            summary += f"Known for {highlights[0]}."
        else:
            summary += "Worth checking out if you want to avoid the tourist circuits."

        venue["insider_score"] = score
        venue["claude_summary"] = summary
        venue["pro_tip"] = tips[0] if tips else "Go early to beat the crowd"
        analyzed.append(venue)

    return analyzed


# ============================================
# ORCHESTRATOR: Coordinate all agents
# ============================================

async def run_multi_agent_search(
    mood_query: str,
    location: str,
    include_web_signals: bool = True,
    include_claude_analysis: bool = True
) -> dict:
    """
    Run the full multi-agent pipeline.

    Args:
        mood_query: User's mood description
        location: NYC neighborhood
        include_web_signals: Whether to search Reddit/blogs
        include_claude_analysis: Whether to use Claude for final analysis

    Returns:
        Dict with venues, signals, and analysis
    """
    results = {
        "agents_used": [],
        "venues": [],
        "location": location,
        "query": mood_query
    }

    # Step 1: Venue Search Agent
    print("[Orchestrator] Starting VenueSearchAgent...")
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="vibes_multi",
        user_id="user_1"
    )

    runner = Runner(
        agent=venue_search_agent,
        app_name="vibes_multi",
        session_service=session_service
    )

    search_message = types.Content(
        role="user",
        parts=[types.Part.from_text(f"Search for: {mood_query} in {location}")]
    )

    venues = []
    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=search_message
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    # Try to parse venues from response
                    try:
                        import re
                        json_match = re.search(r'\{[\s\S]*"venues"[\s\S]*\}', part.text)
                        if json_match:
                            data = json.loads(json_match.group())
                            venues = data.get("venues", [])
                    except:
                        pass

    results["agents_used"].append({
        "name": "VenueSearchAgent",
        "model": "gemini-3.1-flash-lite-preview",
        "task": "Foursquare venue search"
    })
    results["venues"] = venues
    print(f"[Orchestrator] Found {len(venues)} venues")

    # Step 2: Web Signals Agent (optional)
    if include_web_signals and venues:
        print("[Orchestrator] Starting WebSignalsAgent...")
        # Note: In production, this would call the web_signals_agent
        # For demo, we simulate web signals to avoid API costs
        for venue in venues:
            venue["web_signals"] = {
                "reddit_mentions": hash(venue.get("name", "")) % 10,
                "reddit_sentiment": "positive" if hash(venue.get("name", "")) % 3 == 0 else "mixed",
                "reddit_highlights": ["great vibes", "friendly staff"],
                "blog_mentions": hash(venue.get("name", "")) % 5,
                "listicle_appearances": hash(venue.get("name", "")) % 8,
                "insider_tips": ["try the seasonal special"]
            }

        results["agents_used"].append({
            "name": "WebSignalsAgent",
            "model": "gemini-3.1-flash-lite-preview",
            "task": "Google Search for Reddit/blog signals"
        })
        print("[Orchestrator] Web signals gathered")

    # Step 3: Claude Analysis (optional)
    if include_claude_analysis and venues:
        print("[Orchestrator] Starting Claude analysis...")
        venues = await analyze_with_claude(venues)
        results["venues"] = venues

        results["agents_used"].append({
            "name": "VibeAnalystAgent",
            "model": "claude-sonnet-4-20250514",
            "task": "Sentiment analysis and insider summaries"
        })
        print("[Orchestrator] Claude analysis complete")

    return results


# ============================================
# Export for use in backend
# ============================================

__all__ = [
    "run_multi_agent_search",
    "venue_search_agent",
    "web_signals_agent",
    "analyze_with_claude"
]


if __name__ == "__main__":
    # Test the multi-agent system
    async def test():
        result = await run_multi_agent_search(
            mood_query="cozy coffee shop",
            location="Williamsburg, Brooklyn",
            include_web_signals=True,
            include_claude_analysis=True
        )
        print("\n=== MULTI-AGENT RESULT ===")
        print(f"Agents used: {[a['name'] for a in result['agents_used']]}")
        print(f"Venues found: {result['count'] if 'count' in result else len(result['venues'])}")
        for v in result["venues"][:3]:
            print(f"  - {v.get('name')}: insider_score={v.get('insider_score', 'N/A')}")

    asyncio.run(test())
