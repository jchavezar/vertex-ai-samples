# Vibes NYC — Full Product Plan

> **Version**: 1.0.0 | **Created**: 2026-04-06  
> **Author**: Jesus (product), Claude Sonnet 4.6 (architecture)  
> **Status**: Ready for implementation

---

## Background & Problem Statement

Existing venue discovery platforms (Yelp, Google Maps, Foursquare) rate places by quality (stars, review count) but not by **gestalt vibe**. When you want a cozy solo breakfast spot with a contemporary interior, lo-fi music, interesting local crowd you can walk into without a reservation — no existing platform surfaces that. You get "4.2 stars, 847 reviews, $$" which tells you nothing about how the place feels.

The insight: every place has a **sensory fingerprint** made up of aesthetic, energy, crowd type, sound profile, accessibility, and underground-ness. This platform matches mood to fingerprint using AI over aggregated free signals.

**Target user**: Someone in NYC (or any city) who has high standards for environment and experience, knows what they like, and wants to find it without reading 200 reviews.

---

## Product Name & Concept

**"Vibes"** — A mood-to-venue matching engine for underground local spots.

The interface lets users either:
1. Type a natural language mood description ("cozy, contemporary, good coffee, walk-in, interesting crowd")
2. Dial in vibe dimensions using sliders + time-of-day picker

The engine returns ranked venues with vibe fingerprints, underground scores, and AI-generated 2-sentence vibe summaries — not generic star ratings.

---

## Crowd / Accessibility Clarification (IMPORTANT)

"Not crowded" does NOT mean empty or antisocial. It means:
- **Accessible**: You can walk in, get a seat, no 3-week reservation waitlist
- **Great vibe people**: The room is full of interesting, local, creative people with good energy

These are modeled as TWO separate dimensions:
- **Accessibility** axis: walk-in anytime ↔ impossible to book
- **Crowd vibe** axis: neighborhood regulars ↔ creative/artistic scene ↔ tourist-heavy

The best spot scores: walk-in friendly + interesting local crowd.

---

## Geography

- **Not Manhattan-only** — works for any NYC neighborhood (Williamsburg, Astoria, Nolita, Bed-Stuy, etc.)
- User picks neighborhood via text input or "Use my location"
- Yelp `location` param accepts any neighborhood name, borough, city, or lat/lon
- Designed to extend to any city (not hardcoded to NYC)

---

## API Stack — 100% Free

| API | Cost | Rate Limit | Purpose |
|-----|------|-----------|---------|
| **Yelp Fusion** | FREE | 5,000 req/day | Primary venue search: name, address, rating, review count, price level, hours, categories, photos |
| **ADK `google_search`** | FREE (built-in) | Per ADK quotas | Web signal extraction: Reddit mentions, blog features, Eater NY, Infatuation, TimeOut — search queries like `"[venue] site:reddit.com/r/nyc"` |
| **Nominatim (OpenStreetMap)** | FREE | 1 req/sec | Geocoding: neighborhood name → lat/lon |
| **Gemini via Vertex AI** | FREE (user's GCP project) | Generous | Vibe analysis, mood query translation, synthesis, underground score reasoning |

**No Google Places API** (costs $275+/month after Feb 2025).  
**No Custom Search API** (ADK google_search replaces it for free).  
**No Reddit API** (google_search covers Reddit results: `site:reddit.com/r/nyc`).

### Vertex AI Configuration

```python
import os
import vertexai

# Must be set BEFORE importing ADK agents
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"]
)
```

### Yelp Fusion API Key

- Register free at: https://api.yelp.com (Yelp Fusion, Developer plan)
- 5,000 API calls/day free
- Header: `Authorization: Bearer {YELP_API_KEY}`

---

## Vibe Dimensions (7 axes)

| Dimension | Values |
|-----------|--------|
| **Aesthetic** | contemporary / raw-industrial / cozy / minimal / eclectic / vintage |
| **Energy** | contemplative ↔ buzzing (0–100 scale) |
| **Sound** | silent / lo-fi / jazz / acoustic / live music / energetic |
| **Crowd vibe** | neighborhood regulars / creative-artistic / mixed / after-work / tourist-heavy |
| **Accessibility** | walk-in anytime / usually available / recommend booking / impossible to get in |
| **Vibe people** | tags: local, creative, dog-friendly, laptop-friendly, date-spot, group-friendly |
| **Underground score** | 0–100, inverse of mainstream-ness (see algorithm below) |

---

## Underground Score Algorithm

```python
def compute_underground_score(venue: dict, web_signals: dict) -> int:
    score = 100

    # Penalize by review count (popularity ≠ underground)
    review_count = venue.get("review_count", 0)
    if review_count > 2000: score -= 50
    elif review_count > 1000: score -= 35
    elif review_count > 500:  score -= 20
    elif review_count > 200:  score -= 10

    # Penalize chains / franchises
    KNOWN_CHAINS = ["starbucks", "dunkin", "mcdonald", "subway", "chipotle",
                    "sweetgreen", "blue bottle", "gregorys", "joe coffee"]
    name_lower = venue.get("name", "").lower()
    if any(chain in name_lower for chain in KNOWN_CHAINS):
        score -= 60

    # Penalize heavy listicle coverage (too mainstream)
    listicle_count = web_signals.get("listicle_appearances", 0)
    if listicle_count > 5: score -= 25
    elif listicle_count > 2: score -= 10

    # Reward organic Reddit mentions by locals
    reddit_count = web_signals.get("reddit_mentions", 0)
    score += min(reddit_count * 8, 25)

    # Reward niche blog features (not Yelp/TripAdvisor/Timeout)
    niche_blogs = web_signals.get("niche_blog_count", 0)
    score += min(niche_blogs * 5, 15)

    # Reward low review count with high rating (hidden gem signal)
    if review_count < 100 and venue.get("rating", 0) >= 4.0:
        score += 15

    return max(0, min(100, score))
```

---

## Project Structure

```
semiautonomous-agents/vibes_nyc/
├── docs/
│   ├── PRODUCT-PLAN.md          ← This file
│   └── CHECKLIST.md             ← Implementation checklist for Claude
├── frontend/                    # React + Vite (reuse sharepoint_wif_portal/frontend patterns)
│   ├── src/
│   │   ├── main.tsx             # Entry point (NO MSAL — no auth needed)
│   │   ├── App.tsx              # Main layout: search + results grid
│   │   ├── VibeDials.tsx        # Mood input: NL text + sliders + time picker
│   │   ├── VenueCard.tsx        # Rich venue card with vibe breakdown
│   │   ├── NeighborhoodPicker.tsx  # Location input with autocomplete
│   │   └── index.css            # Dark moody palette (charcoal + amber accents)
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts           # Proxy /api → localhost:8000
├── backend/
│   ├── main.py                  # FastAPI: /api/search, /api/venue, /api/mood
│   ├── vibe_engine.py           # Vibe profile synthesis + underground score
│   └── pyproject.toml
├── agent/
│   ├── agent.py                 # VenueResearchAgent — ADK agent with 3 tools
│   ├── yelp_client.py           # Yelp Fusion API client
│   ├── web_signals.py           # google_search-powered signal extraction
│   ├── nominatim_client.py      # Free geocoding
│   └── pyproject.toml
├── .env.example
└── README.md
```

---

## Architecture Diagram

```
User (browser)
      │
      ▼
Frontend (React, port 5173)
  • NL mood input OR vibe sliders
  • Neighborhood picker
  • Time of day picker
  • Results grid with vibe cards
      │
      │ POST /api/search {mood_query, location, time_of_day, vibe_dims}
      ▼
Backend (FastAPI, port 8000)
  • Translates mood query → structured search params (via Gemini)
  • Calls Agent → collects VenueResult[]
  • Applies underground score ranking
  • Returns ranked JSON
      │
      ▼
VenueResearchAgent (ADK)
  Model: gemini-2.5-flash (via Vertex AI)
  Tools:
  ├── search_yelp_venues(query, location) → venue list
  ├── get_web_signals(venue_name, neighborhood) → Reddit/blog signals
  └── google_search (built-in ADK tool, free)
      │
      ├── Yelp Fusion API (free, 5K/day)
      ├── ADK google_search → reddit.com/r/nyc, eater.com, infatuation.com
      └── Nominatim → lat/lon for neighborhood
```

---

## Agent Definition (agent/agent.py)

```python
import os
import vertexai
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools import FunctionTool

# Vertex AI setup (must come first)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")
vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])

from agent.yelp_client import YelpClient
from agent.nominatim_client import NominatimClient

yelp = YelpClient()
geo = NominatimClient()

async def search_yelp_venues(query: str, location: str, tool_context) -> dict:
    """
    Search Yelp for venues matching the mood query in the given location.
    Returns a list of venues with name, address, rating, review_count, price, categories, hours.
    Use this first to get candidate venues.
    """
    lat_lon = await geo.geocode(location)
    venues = await yelp.search(term=query, lat=lat_lon[0], lon=lat_lon[1])
    return {"venues": venues, "location": location, "count": len(venues)}

async def get_web_signals(venue_name: str, neighborhood: str, tool_context) -> dict:
    """
    Get organic web signals for a venue: Reddit mentions, blog features, listicle appearances.
    Returns reddit_mentions count, niche_blog_count, listicle_count, and sample snippets.
    Call this after search_yelp_venues for the top candidate venues.
    """
    # This function uses google_search under the hood via the agent's reasoning
    # Returns structured signal data parsed from search results
    pass  # Agent uses google_search tool autonomously for this

AGENT_INSTRUCTION = """
You are a Manhattan underground venue expert with deep knowledge of NYC neighborhoods.
Your goal: find venues that match a user's mood — not the most popular spots, but the most resonant ones.

When given a mood query and location:
1. Call search_yelp_venues to get candidate venues
2. Use google_search to find Reddit and blog signals for top candidates:
   - Search: "[venue name] site:reddit.com" for Reddit mentions
   - Search: "[venue name] [neighborhood] review hidden gem" for blog coverage
   - Search: "best [mood] spots [neighborhood] NYC 2024 2025" for curated lists
3. Synthesize a vibe profile for each venue including:
   - aesthetic (contemporary/cozy/industrial/minimal/eclectic/vintage)
   - energy (1-10: 1=very calm, 10=very buzzing)
   - sound (silent/lo-fi/jazz/acoustic/live/energetic)
   - crowd_vibe (neighborhood regulars/creative scene/mixed/tourist-heavy)
   - accessibility (walk-in/usually available/book ahead/impossible)
   - underground_score (0-100: penalize chains, high review count, listicles; reward Reddit organics)
4. Rank by vibe match to the user's mood, not by rating
5. Return top 6-10 venues with full vibe profiles and a 2-sentence vibe summary each

IMPORTANT: Prioritize walk-in accessible spots with interesting local crowd over trendy reservations-only places.
"""

root_agent = LlmAgent(
    name="VenueResearchAgent",
    model="gemini-2.5-flash",
    description="NYC underground venue expert that matches mood to place",
    instruction=AGENT_INSTRUCTION,
    tools=[search_yelp_venues, google_search]
)
```

---

## Yelp Client (agent/yelp_client.py)

```python
import os
import httpx
from typing import Optional

class YelpClient:
    BASE_URL = "https://api.yelp.com/v3/businesses/search"
    DETAIL_URL = "https://api.yelp.com/v3/businesses/{id}"

    def __init__(self):
        self.api_key = os.environ.get("YELP_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def search(
        self,
        term: str,
        lat: float,
        lon: float,
        radius: int = 1500,  # meters (~1 mile)
        limit: int = 20,
        open_now: bool = True,
        price: Optional[str] = None,  # "1,2" for $ and $$
    ) -> list[dict]:
        params = {
            "term": term,
            "latitude": lat,
            "longitude": lon,
            "radius": radius,
            "limit": limit,
            "open_now": open_now,
            "sort_by": "best_match",
        }
        if price:
            params["price"] = price

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(self.BASE_URL, headers=self.headers, params=params)
            if not resp.is_success:
                return []
            data = resp.json()
            return [self._normalize(b) for b in data.get("businesses", [])]

    def _normalize(self, b: dict) -> dict:
        return {
            "yelp_id": b.get("id"),
            "name": b.get("name"),
            "rating": b.get("rating"),
            "review_count": b.get("review_count"),
            "price": b.get("price", ""),
            "address": ", ".join(b.get("location", {}).get("display_address", [])),
            "neighborhood": b.get("location", {}).get("city", ""),
            "categories": [c["title"] for c in b.get("categories", [])],
            "is_closed": b.get("is_closed", False),
            "photos": [b.get("image_url")] if b.get("image_url") else [],
            "url": b.get("url"),
            "coordinates": b.get("coordinates", {}),
            "distance": b.get("distance"),
        }

    async def get_details(self, yelp_id: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                self.DETAIL_URL.format(id=yelp_id),
                headers=self.headers
            )
            return resp.json() if resp.is_success else {}
```

---

## Nominatim Client (agent/nominatim_client.py)

```python
import httpx

class NominatimClient:
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    CACHE = {}  # Simple in-memory cache to respect 1 req/sec limit

    async def geocode(self, location: str) -> tuple[float, float]:
        if location in self.CACHE:
            return self.CACHE[location]

        async with httpx.AsyncClient(
            timeout=5,
            headers={"User-Agent": "VibesNYC/1.0 (venue discovery app)"}
        ) as client:
            resp = await client.get(self.BASE_URL, params={
                "q": location,
                "format": "json",
                "limit": 1,
                "countrycodes": "us"
            })
            results = resp.json()
            if results:
                lat = float(results[0]["lat"])
                lon = float(results[0]["lon"])
                self.CACHE[location] = (lat, lon)
                return (lat, lon)

        # Default to Manhattan midtown if geocoding fails
        return (40.7549, -73.9840)
```

---

## FastAPI Backend (backend/main.py)

```python
import os
import asyncio
import vertexai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Vertex AI init
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")
vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])

app = FastAPI(title="Vibes NYC API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class SearchRequest(BaseModel):
    mood_query: str                          # "cozy morning, contemporary, good coffee"
    location: str = "Lower East Side, NYC"  # Any neighborhood or city
    time_of_day: str = "morning"            # morning | afternoon | evening | night
    open_now: bool = True
    vibe_dims: Optional[dict] = None        # Optional slider overrides

class VenueDetailRequest(BaseModel):
    yelp_id: str
    venue_name: str
    neighborhood: str

@app.post("/api/search")
async def search_venues(body: SearchRequest):
    """
    Main search endpoint. Takes mood query + location, returns ranked venues with vibe profiles.
    """
    from agent.agent import run_venue_search
    results = await run_venue_search(
        mood_query=body.mood_query,
        location=body.location,
        time_of_day=body.time_of_day,
        open_now=body.open_now
    )
    return {"venues": results, "location": body.location, "query": body.mood_query}

@app.get("/api/venue/{yelp_id}")
async def venue_detail(yelp_id: str):
    """Full venue detail with vibe profile and web signals."""
    from agent.yelp_client import YelpClient
    client = YelpClient()
    details = await client.get_details(yelp_id)
    return details

@app.post("/api/mood")
async def quick_mood(body: dict):
    """Quick Gemini response explaining the vibe for a location/time combo."""
    # Returns a short paragraph: "Here's the vibe in Williamsburg on a Sunday morning..."
    pass
```

---

## Frontend Design System (frontend/src/index.css)

```css
/* Dark moody palette — gallery/speakeasy aesthetic */
:root {
  --bg-primary: #0F0F0F;          /* Near black */
  --bg-secondary: #1A1A1A;        /* Dark slate */
  --bg-card: #1F1F1F;             /* Slightly lighter card bg */
  --bg-elevated: #252525;         /* Hover/elevated surfaces */

  --accent-amber: #F59E0B;        /* Underground score, highlights */
  --accent-teal: #14B8A6;         /* Vibe match indicator */
  --accent-rose: #F43F5E;         /* Accessibility indicator */
  --text-primary: #F5F5F5;        /* Near white */
  --text-secondary: #9CA3AF;      /* Muted grey */
  --text-muted: #6B7280;

  --font-family: 'Inter', system-ui, sans-serif;
  --border-subtle: rgba(255,255,255,0.08);
  --transition: all 0.2s ease-in-out;
}
```

---

## Frontend UI Layout (frontend/src/App.tsx)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ◆ VIBES    📍 Williamsburg, Brooklyn  ▾        🌅 Morning  ▾            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   ┌──────────────────────────────────────────────────────┐  [Search]     │
│   │ Describe your vibe... "cozy, contemporary, good       │               │
│   │ coffee, not touristy, interesting crowd"              │               │
│   └──────────────────────────────────────────────────────┘               │
│                                                                            │
│   ─── Or dial it in ──────────────────────────────────────────────────── │
│   Energy:        [ Calm  ●──────○──────────────  Buzzing ]                │
│   Accessibility: [ Walk-in ●───────────○  Book ahead ]                   │
│   Crowd vibe:    [ Neighborhood locals ●────○────  Scene ]                │
│   Aesthetic:     [ Minimal ○──────────●──  Eclectic ]                    │
│   Sound:         [ Silent ○────●──  Lo-fi ──── Live ]                    │
│                                                                            │
├──────────────────────────────────────────────────────────────────────────┤
│  8 spots matching your vibe · Underground only · Open now                 │
│                                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  [venue photo]   │  │  [venue photo]   │  │  [venue photo]   │       │
│  │                  │  │                  │  │                  │       │
│  │  Maman Tribeca   │  │  Sunday in BK    │  │  Blank Street    │       │
│  │  ⬡ 87  UG score │  │  ⬡ 74  UG score │  │  ⬡ 91  UG score │       │
│  │  Contemporary    │  │  Exposed brick   │  │  Minimal         │       │
│  │  Lo-fi · Quiet  │  │  Jazz · Locals   │  │  Fast · Clean    │       │
│  │  ✓ Walk-in      │  │  ✓ Walk-in       │  │  ✓ Walk-in       │       │
│  │  Best: 7–10am   │  │  Best: 9–11am    │  │  Best: 8–11am    │       │
│  │                  │  │                  │  │                  │       │
│  │  0.3 mi          │  │  0.6 mi          │  │  0.4 mi          │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## VenueCard Component Fields

Each card shows:
- **Photo** (from Yelp image_url)
- **Name**
- **Underground score** (amber hexagon ⬡, 0–100)
- **Vibe tags** (3–5 single words: Contemporary · Lo-fi · Locals)
- **Accessibility badge** (✓ Walk-in / ⚠ Book ahead / ✗ Hard to get in)
- **Best time to go** (derived from Yelp hours + crowd signal)
- **AI vibe summary** (2 sentences, generated by agent)
- **Distance** (from search location)
- **Hover/click**: expands to full vibe breakdown + map pin link

---

## Key Files to Reference (from existing codebase)

All patterns should be copied and adapted from the SharePoint WIF portal:

| New File | Reference From | Key Pattern |
|----------|---------------|-------------|
| `agent/agent.py` | `sharepoint_wif_portal/agent/agent.py` | ADK LlmAgent + async tool functions |
| `agent/yelp_client.py` | `sharepoint_wif_portal/agent/discovery_engine.py` | Class-based API client, error handling, response normalization |
| `backend/main.py` | `sharepoint_wif_portal/backend/main.py` | FastAPI, CORS, asyncio.to_thread, Pydantic models |
| `frontend/src/App.tsx` | `sharepoint_wif_portal/frontend/src/App.tsx` | Layout structure, useState patterns, fetch calls |
| `frontend/src/index.css` | `sharepoint_wif_portal/frontend/src/index.css` | CSS variables, keyframe animations, component classes |
| `frontend/package.json` | `sharepoint_wif_portal/frontend/package.json` | Dependencies (react, vite, lucide-react, react-markdown) |
| `backend/pyproject.toml` | `sharepoint_wif_portal/backend/pyproject.toml` | Python deps (fastapi, uvicorn, httpx, pydantic, uv) |
| `agent/pyproject.toml` | `sharepoint_wif_portal/pyproject.toml` (root) | ADK deps (google-adk, google-cloud-aiplatform[adk]) |

---

## Environment Variables

```env
# .env (backend + agent)

# Vertex AI (use existing GCP project — absorbs Gemini cost)
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1
# Authentication via ADC: run `gcloud auth application-default login`

# ADK: use Vertex AI backend (not Google AI Studio)
GOOGLE_GENAI_USE_VERTEXAI=true

# Yelp Fusion (FREE — register at https://api.yelp.com)
YELP_API_KEY=your-yelp-api-key
```

```env
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Build Order

1. **`agent/nominatim_client.py`** — geocoding (no API key, just HTTP)
2. **`agent/yelp_client.py`** — Yelp Fusion search + normalize response
3. **`backend/vibe_engine.py`** — underground score algorithm
4. **`agent/agent.py`** — VenueResearchAgent with `search_yelp_venues` + `google_search` tools
5. **`backend/main.py`** — FastAPI with `/api/search` + `/api/venue/:id`
6. **`frontend/src/index.css`** — dark design system (charcoal + amber)
7. **`frontend/src/VenueCard.tsx`** — rich card component
8. **`frontend/src/VibeDials.tsx`** — mood input with sliders + NL text
9. **`frontend/src/NeighborhoodPicker.tsx`** — location input
10. **`frontend/src/App.tsx`** — main layout connecting all components
11. **`frontend/package.json`** + **`vite.config.ts`** — Vite proxy `/api → localhost:8000`
12. **End-to-end test** — search "cozy morning, contemporary, walk-in" in Williamsburg

---

## Local Development Commands

```bash
# Backend
cd backend && uv sync && uv run uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
# → http://localhost:5173

# Test agent directly
cd agent && uv run python test_local.py
```

---

## Notes for Implementation

1. **No auth needed** — this is a public app, no MSAL, no WIF, no login
2. **ADK `google_search` is free and built-in** — `from google.adk.tools import google_search` — no API key needed
3. **Yelp `open_now=true`** — always filter for currently open venues by default
4. **Nominatim rate limit** — 1 req/sec, use in-memory cache for repeated neighborhood lookups
5. **Underground score** — compute in `vibe_engine.py`, not in the agent (keep deterministic logic separate from AI)
6. **Vibe summary** — 2 sentences max, written by Gemini based on aggregated signals, NOT generic marketing copy
7. **Photo fallback** — if Yelp photo is missing, show a dark gradient placeholder with the venue's category emoji
8. **Mobile-first** — the card grid should be 1-col on mobile, 2-col on tablet, 3-col on desktop
