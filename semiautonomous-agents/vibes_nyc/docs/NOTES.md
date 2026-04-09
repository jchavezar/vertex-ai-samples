# Vibes NYC - Technical Notes

> Comprehensive documentation for understanding and improving the application.

---

## Application Overview

**Vibes NYC** is a mood-to-venue matching engine that helps you find places based on how you want to feel, not star ratings.

### Core Concept

Traditional apps: "Show me 4.5+ star coffee shops"  
Vibes NYC: "I want a cozy morning spot with good coffee and an interesting crowd"

The app returns venues with:
- **Underground Score** (0-100): How "hidden gem" vs "tourist trap" a place is
- **Vibe Tags**: Aesthetic descriptors (cozy, intimate, industrial, etc.)
- **Accessibility**: Walk-in friendly vs reservation required
- **AI Vibe Summary**: 2-sentence description matching your mood

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   React/Vite    │────▶│   FastAPI        │────▶│   VenueResearchAgent    │
│   Frontend      │     │   Backend        │     │   (Google ADK)          │
│   :5173         │     │   :8888          │     │                         │
└─────────────────┘     └──────────────────┘     │   ┌─────────────────┐   │
                                                 │   │ Gemini 2.5 Flash│   │
                                                 │   └─────────────────┘   │
                                                 │           │             │
                                                 │   ┌───────▼───────┐     │
                                                 │   │ search_venues │     │
                                                 │   │    (tool)     │     │
                                                 │   └───────┬───────┘     │
                                                 └───────────┼─────────────┘
                                                             │
                                    ┌────────────────────────┼────────────────────────┐
                                    │                        │                        │
                              ┌─────▼─────┐          ┌───────▼───────┐        ┌───────▼───────┐
                              │ Foursquare│          │   Nominatim   │        │  vibe_engine  │
                              │ Places v2 │          │   Geocoding   │        │  (NOT USED!)  │
                              │  (free)   │          │    (free)     │        │               │
                              └───────────┘          └───────────────┘        └───────────────┘
```

---

## The Underground Score Problem

### Current Behavior (BUG)

**All venues show score 115** because:

1. The agent instruction tells Gemini to "compute" underground scores
2. But Gemini **hallucinates** the numbers - it doesn't run actual calculations
3. The LLM consistently returns 100-115 for all similar venue types
4. The real algorithm in `vibe_engine.py` is **NOT CALLED** during search

### Where the Bug Lives

**File: `agent/agent.py`**

The `AGENT_INSTRUCTION` tells Gemini:
```
underground_score (0-100): start at 100, penalize chains (-60), 
high review count (>2000: -50, >1000: -35, >500: -20), 
reward low reviews + high rating (+15)
```

But this is just TEXT - the LLM reads it and makes up numbers that "sound right."

**File: `backend/vibe_engine.py`**

Contains the REAL algorithm:
```python
def compute_underground_score(venue: dict, web_signals: dict = None) -> int:
    score = 100
    review_count = venue.get("review_count", 0)
    if review_count > 2000:
        score -= 50
    # ... actual math
    return max(0, min(100, score))
```

But this function is only called in `/api/venue/{id}` (detail view), NOT in the main search.

### The Fix

In `backend/main.py`, after getting results from the agent, apply the real algorithm:

```python
@app.post("/api/search")
async def search_venues(body: SearchRequest):
    from agent import run_venue_search
    from vibe_engine import compute_underground_score, tag_accessibility

    results = await run_venue_search(...)
    
    # FIX: Apply real scoring algorithm
    for venue in results:
        venue["underground_score"] = compute_underground_score(venue)
        venue["accessibility"] = tag_accessibility(venue)
    
    return {"venues": results, ...}
```

---

## Underground Score Algorithm (Intended)

| Factor | Points | Logic |
|--------|--------|-------|
| **Base** | 100 | Everyone starts here |
| **Chain name detected** | -60 | Starbucks, Dunkin, Blue Bottle, etc. |
| **Review count > 2000** | -50 | Too popular = not underground |
| **Review count > 1000** | -35 | Very popular |
| **Review count > 500** | -20 | Popular |
| **Review count > 200** | -10 | Moderately known |
| **Listicle appearances > 5** | -25 | Too mainstream media |
| **Listicle appearances > 2** | -10 | Some mainstream coverage |
| **Reddit mentions** | +8 each (max +25) | Organic local buzz |
| **Niche blog features** | +5 each (max +15) | Indie coverage |
| **< 100 reviews + rating >= 4.0** | +15 | Hidden gem signal |

**Score Range**: 0-100 (clamped)

### Example Calculations

**Starbucks Reserve (2500 reviews)**:
- Base: 100
- Chain detected: -60
- Reviews > 2000: -50
- **Final: 0** (clamped from -10)

**Local Coffee Shop (45 reviews, 4.5 rating)**:
- Base: 100
- Hidden gem bonus: +15
- **Final: 115** (but clamped to 100)

**Popular but not chain (800 reviews)**:
- Base: 100
- Reviews > 500: -20
- **Final: 80**

---

## Known Chains List

These trigger a -60 penalty:

| Category | Chains |
|----------|--------|
| **Coffee** | Starbucks, Dunkin, Blue Bottle, Gregorys, Joe Coffee |
| **Fast Food** | McDonald's, Subway, Chipotle, Chick-fil-A, Five Guys, Shake Shack |
| **Fast Casual** | Sweetgreen, Panera, Pret A Manger, Au Bon Pain, Cosi, Le Pain Quotidien |

---

## Vibe Tags

AI-generated aesthetic descriptors based on venue category:

| Category Match | Default Tag |
|----------------|-------------|
| Coffee/Cafe | cozy |
| Cocktail/Bar | intimate |
| Brewery/Taproom | industrial |
| Bakery/Patisserie | bright |
| Default | contemporary |

Additional tags extracted from AI analysis:
- contemporary, cozy, industrial, minimal, eclectic
- vintage, bright, dark, intimate, spacious

---

## Accessibility Badges

| Badge | Meaning | Logic |
|-------|---------|-------|
| **walk-in** (teal) | No reservation needed | Default for most venues |
| **usually available** | Mostly walk-in friendly | > 2000 reviews |
| **book ahead** (amber) | Reservations recommended | $$$ + 500+ reviews OR 3+ reservation mentions |
| **impossible to get in** (rose) | Requires planning | $$$ + 1000+ reviews |

---

## API Endpoints

### POST /api/search

Main search endpoint.

**Request:**
```json
{
  "mood_query": "cozy coffee shop, morning vibes",
  "location": "Williamsburg, Brooklyn",
  "time_of_day": "morning",
  "open_now": true
}
```

**Response:**
```json
{
  "venues": [
    {
      "name": "Devocion",
      "address": "69 Grand St, Brooklyn",
      "rating": 4.5,
      "review_count": 234,
      "underground_score": 80,
      "vibe_tags": ["cozy", "bright", "contemporary"],
      "accessibility": "walk-in",
      "vibe_summary": "A Colombian coffee sanctuary with soaring ceilings...",
      "best_time": "morning"
    }
  ],
  "count": 6,
  "location": "Williamsburg, Brooklyn"
}
```

### GET /api/health

Health check.

**Response:** `{"status": "ok", "service": "vibes-nyc"}`

---

## Data Flow

1. **User Input**: "late night cocktails, moody lighting" in Williamsburg
2. **Frontend**: Sends POST to `/api/search`
3. **Backend**: Calls `run_venue_search()` from agent
4. **Agent**: 
   - Uses `search_venues` tool
   - Tool calls Nominatim to geocode "Williamsburg, Brooklyn" → (40.71, -73.95)
   - Tool calls Foursquare API to search "cocktails" near coordinates
   - Returns raw venue data to Gemini
5. **Gemini**: Analyzes venues, generates vibe tags, summaries, and (fake) scores
6. **Backend**: Returns JSON to frontend
7. **Frontend**: Renders venue cards with all vibe data

---

## External APIs

### Foursquare Places v2

- **Cost**: Free (200,000 calls/month)
- **Auth**: client_id + client_secret (OAuth, not API key)
- **Endpoint**: `https://api.foursquare.com/v2/venues/search`
- **Data**: Venue names, categories, locations, check-in counts

Note: Foursquare v2 doesn't provide ratings or reviews directly. The `rating` field defaults to 4.0 and `review_count` uses check-in counts.

### Nominatim (OpenStreetMap)

- **Cost**: Free (1 request/second limit)
- **Endpoint**: `https://nominatim.openstreetmap.org/search`
- **Purpose**: Convert "Williamsburg, Brooklyn" → lat/lon coordinates
- **Cache**: Results cached in-memory to respect rate limit

---

## File Structure

```
vibes_nyc/
├── agent/
│   ├── agent.py              # ADK LlmAgent + search_venues tool
│   ├── foursquare_client.py  # Foursquare v2 API client
│   └── nominatim_client.py   # Geocoding client
├── backend/
│   ├── main.py               # FastAPI endpoints
│   └── vibe_engine.py        # Underground score algorithm (NOT USED IN SEARCH!)
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main layout + state
│   │   ├── VenueCard.tsx     # Individual venue display
│   │   ├── VibeDials.tsx     # Search input + mood sliders
│   │   ├── NeighborhoodPicker.tsx
│   │   └── index.css         # Dark moody design system
│   └── package.json
├── docs/
│   ├── PRODUCT-PLAN.md       # Original specification
│   ├── CHECKLIST.md          # Implementation progress
│   └── NOTES.md              # This file
├── .env                      # Real credentials (gitignored)
└── .env.example              # Template
```

---

## Environment Variables

```bash
# Vertex AI
PROJECT_ID=your-gcp-project
LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true

# Foursquare (from developers.foursquare.com → OAuth section)
FOURSQUARE_CLIENT_ID=xxx
FOURSQUARE_CLIENT_SECRET=xxx
```

---

## Running the App

```bash
# Terminal 1: Backend
cd backend
uv sync
uv run uvicorn main:app --port 8888 --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Known Issues

### 1. All Underground Scores are 115

**Status**: BUG  
**Cause**: LLM hallucination - scores are generated by Gemini, not computed  
**Fix**: Apply `vibe_engine.compute_underground_score()` in backend after agent returns

### 2. No Real Review Counts from Foursquare

**Status**: LIMITATION  
**Cause**: Foursquare v2 only provides check-in counts, not reviews  
**Impact**: Underground score can't penalize by review count accurately  
**Workaround**: Could integrate a second API (Google Places) for review data

### 3. Vibe Summaries Sometimes Generic

**Status**: MINOR  
**Cause**: Gemini has limited data per venue  
**Workaround**: Could fetch more context from venue detail endpoint

---

## Latency Analysis

**Current performance:** ~9-10 seconds per search

### Breakdown

| Component | Time | % of Total |
|-----------|------|------------|
| **LLM (Gemini 3.1 Flash Lite)** | ~8-9s | 90% |
| Foursquare API | ~0.5s | 5% |
| Nominatim geocoding | ~0.3s | 3% |
| Backend overhead | ~0.2s | 2% |

**The LLM is the bottleneck** - it's generating vibe tags, summaries, and best_time for each venue.

### Quick Optimizations (can reduce to ~4-5s)

1. **Shorter agent prompt** - fewer tokens = faster response
2. **Limit venues** - analyze 6 instead of 20
3. **Simpler summaries** - 1 sentence instead of 2
4. **Remove best_time generation** - use static mapping instead

### Bigger Refactors (for production)

1. **Skip LLM for simple searches** - use Foursquare + vibe_engine directly, only use LLM for complex mood queries
2. **Streaming responses** - show venues progressively as they're analyzed
3. **Pre-compute popular searches** - cache common queries like "coffee Williamsburg"
4. **Parallel LLM calls** - analyze venues in batches of 3
5. **Response caching** - TTL cache for identical queries (Redis)
6. **Edge functions** - move geocoding to edge for lower latency

### Model Comparison

| Model | Latency | Quality |
|-------|---------|---------|
| gemini-2.5-flash | ~18s | High |
| gemini-2.0-flash | ~15s | High |
| gemini-3.1-flash-lite-preview | ~9s | Good |

---

## Development Mode

To avoid burning Foursquare API calls during development:

```bash
# In .env
USE_MOCK_DATA=true
```

This returns pre-defined mock venues instead of hitting the real API. Mock data includes:
- 6 coffee shops (with varying review counts for score testing)
- 5 cocktail bars
- Includes chains (Starbucks, Blue Bottle) to test scoring penalties

---

## Future Improvements

1. ~~**Fix underground scoring**~~: DONE - using `vibe_engine.py` for real calculations
2. **Add Google Places**: Get actual review counts for better scoring
3. **Web signals**: Re-add Reddit/blog scraping for listicle detection
4. **Caching**: Cache venue data to reduce API calls
5. **User accounts**: Save favorite venues and searches
6. **Map view**: Show venues on an interactive map
7. **Latency optimization**: Implement quick wins listed above

---

## Photos, Maps & Directions (Future Feature)

### Venue Photos

| Source | Cost | Implementation |
|--------|------|----------------|
| **Foursquare Photos** | Free (within 200K) | Call `/venues/{id}` for `bestPhoto` field |
| **Google Places Photos** | $7/1000 | Use place_id → photos endpoint |
| **Google Custom Search** | 100 free/day | Search `"{venue name} {neighborhood} interior"` |

**Recommended approach:**
1. First try Foursquare `bestPhoto` from venue details
2. Fallback to Google Custom Search for image
3. Final fallback to category icon (current behavior)

### Walking Directions

| Source | Cost | Features |
|--------|------|----------|
| **Google Directions API** | $5/1000 | Best routing, step-by-step, ETA |
| **OSRM** | Free | OpenStreetMap routing, self-host or public API |
| **Mapbox Directions** | 100K free/mo | Good alternative |

**Implementation:**
```javascript
// Example: Get walking directions
const response = await fetch(
  `https://router.project-osrm.org/route/v1/walking/${userLng},${userLat};${venueLng},${venueLat}?overview=full&geometries=geojson`
);
const { routes } = await response.json();
const walkingMinutes = Math.round(routes[0].duration / 60);
const polyline = routes[0].geometry; // For map trace
```

### Map Display

| Library | Cost | Notes |
|---------|------|-------|
| **Leaflet + OpenStreetMap** | Free | Best for MVP, easy setup |
| **Google Maps JS** | $7/1000 loads | Best UX, familiar |
| **Mapbox GL JS** | 50K free/mo | Beautiful, 3D support |

**Recommended stack:**
- **Leaflet + React-Leaflet** for map display (free)
- **OSRM** for walking directions (free)
- **Foursquare** for photos (already have)

### Implementation Plan

1. **Phase 1: Basic Map**
   - Add Leaflet map below search results
   - Plot venue markers with popups
   - Click marker → highlight venue card

2. **Phase 2: User Location**
   - "Use my location" button
   - Show user position on map
   - Calculate walking distance to each venue

3. **Phase 3: Directions**
   - Click venue → show walking route
   - Display estimated walking time
   - Turn-by-turn in expandable panel

4. **Phase 4: Photos**
   - Fetch Foursquare bestPhoto on venue detail
   - Lazy load photos as user scrolls
   - Lightbox for full-size view

---

## Implemented Features (as of latest session)

### Map Integration (DONE)
- **Leaflet + React-Leaflet** for map display
- **CartoDB dark tiles** matching the app theme
- **Amber venue markers** with custom SVG icons
- **Auto-fit bounds** to show all venues
- **Hide Map / Find Me** toggle buttons
- **Venue selection** highlights card with amber border
- **Walking directions** via OSRM (when user location available)

### Underground Scoring (FIXED)
- Now using real algorithm from `vibe_engine.py`
- Chain detection working (Blue Bottle: 5, Starbucks: 0)
- Review count penalties applied
- Scores sorted descending (hidden gems first)

### Development Mode (DONE)
- `USE_MOCK_DATA=true` uses pre-defined venues
- Saves Foursquare API calls during development
- Mock data includes chains for testing scoring

---

## Multi-Agent Architecture (NEW)

### Use Case: Deep Venue Vetting with Web Signals

The standard search uses a single agent. The deep search (`/api/search/deep`) uses three agents collaborating:

```
User Query: "cozy coffee, locals only"
         │
         ▼
┌─────────────────────────────┐
│  VenueSearchAgent (Gemini)  │ ← Foursquare API
│  Model: gemini-3.1-flash    │
│  Task: Find candidate venues│
└─────────────────────────────┘
         │ 8 venues
         ▼
┌─────────────────────────────┐
│  WebSignalsAgent (Gemini)   │ ← google_search tool
│  Model: gemini-2.0-flash    │
│  Task: Search Reddit/blogs  │
│  - reddit_mentions          │
│  - blog_coverage            │
│  - listicle_appearances     │
└─────────────────────────────┘
         │ venues + signals
         ▼
┌─────────────────────────────┐
│  VibeAnalystAgent (Claude)  │ ← Anthropic API
│  Model: claude-sonnet-4     │
│  Task: Sentiment analysis   │
│  - insider_score            │
│  - claude_summary           │
│  - pro_tip                  │
└─────────────────────────────┘
         │
         ▼
   Final ranked results
```

### Why Multi-Agent?

| Agent | Model | Why This Model |
|-------|-------|----------------|
| VenueSearch | gemini-3.1-flash-lite-preview | Fast, cheap, good at structured search |
| WebSignals | gemini-3.1-flash-lite-preview | Same fast model with google_search tool |
| VibeAnalyst | claude-sonnet-4 | Best at nuanced writing and sentiment analysis |

### Web Signals Collected

For each venue, the WebSignalsAgent searches:

1. `"{venue}" site:reddit.com NYC` → Reddit buzz
2. `"{venue}" blog review` → Niche coverage
3. `"{venue}" "top 10"` → Listicle detection (tourist trap signal)

### Claude's Analysis

Claude receives venues + web signals and produces:

- **insider_score** (0-100): Combines Reddit sentiment, blog coverage, inverse of listicle appearances
- **claude_summary**: 2-sentence "local insider" style description
- **pro_tip**: Actionable advice ("ask for off-menu cortado")

### API Endpoints

| Endpoint | Agents | Latency | Use Case |
|----------|--------|---------|----------|
| `POST /api/search` | 1 (Gemini) | ~9s | Quick search |
| `POST /api/search/deep` | 3 (Gemini + Claude) | ~20s | Deep vetting |

### Response includes agent info

```json
{
  "venues": [...],
  "model": "gemini-3.1-flash-lite-preview",
  "region": "global",
  "agents": [
    {"name": "VenueSearchAgent", "model": "gemini-3.1-flash-lite-preview"},
    {"name": "WebSignalsAgent", "model": "gemini-3.1-flash-lite-preview"},
    {"name": "VibeAnalystAgent", "model": "claude-sonnet-4"}
  ]
}
```
