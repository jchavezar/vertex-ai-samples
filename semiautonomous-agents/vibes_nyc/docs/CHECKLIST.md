# Vibes NYC — Implementation Checklist

> **For the implementing model**: Read `PRODUCT-PLAN.md` in full before starting.  
> All patterns should be copied and adapted from `semiautonomous-agents/sharepoint_wif_portal/`.  
> Use `uv` for all Python (never pip, never docker unless asked).  
> Work in order — each phase depends on the previous.

---

## Before You Start

- [x] Read `docs/PRODUCT-PLAN.md` completely
- [x] Read `semiautonomous-agents/sharepoint_wif_portal/agent/agent.py` (tool pattern to reuse)
- [x] Read `semiautonomous-agents/sharepoint_wif_portal/agent/discovery_engine.py` (API client pattern)
- [x] Read `semiautonomous-agents/sharepoint_wif_portal/backend/main.py` (FastAPI pattern)
- [x] Read `semiautonomous-agents/sharepoint_wif_portal/frontend/src/App.tsx` (React layout pattern)
- [x] Read `semiautonomous-agents/sharepoint_wif_portal/frontend/src/index.css` (CSS design system pattern)
- [x] Confirm `.env` exists with `PROJECT_ID`, `LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI=true` (YELP_API_KEY needs to be added for full functionality)

---

## Phase 1 — Project Scaffold

- [x] Create `agent/` directory
- [x] Create `backend/` directory
- [x] Create `frontend/` directory
- [x] Create `.env.example` with all required variables (see PRODUCT-PLAN.md)
- [x] Create `.env` (copy from `.env.example`, fill in real values)
- [x] Create `agent/pyproject.toml` — deps: `google-cloud-aiplatform[adk,agent_engines]`, `google-adk`, `httpx`, `python-dotenv`
- [x] Create `backend/pyproject.toml` — deps: `fastapi[standard]`, `uvicorn`, `httpx`, `pydantic`, `python-dotenv`, `google-cloud-aiplatform`
- [x] Run `cd agent && uv sync` — verify no errors
- [x] Run `cd backend && uv sync` — verify no errors

---

## Phase 2 — Agent: Nominatim Geocoding Client

File: `agent/nominatim_client.py`

- [x] Create `NominatimClient` class
- [x] Implement `async def geocode(self, location: str) -> tuple[float, float]`
  - GET `https://nominatim.openstreetmap.org/search`
  - Params: `q=location`, `format=json`, `limit=1`, `countrycodes=us`
  - User-Agent header required: `"VibesNYC/1.0 (venue discovery)"`
  - Cache results in-memory (dict) to respect 1 req/sec limit
  - Fallback: return `(40.7549, -73.9840)` (Manhattan midtown) if geocoding fails
- [x] Test: `asyncio.run(NominatimClient().geocode("Williamsburg, Brooklyn"))` → returns `(40.71, -73.95)` approx

---

## Phase 3 — Agent: Foursquare Places Client (switched from Yelp due to pricing)

File: `agent/foursquare_client.py`

- [x] Create `FoursquareClient` class
- [x] Load `FOURSQUARE_CLIENT_ID` and `FOURSQUARE_CLIENT_SECRET` from env (v2 API)
- [x] Implement `async def search(query, lat, lon, radius=1500, limit=20, open_now=True) -> list[dict]`
  - GET `https://api.foursquare.com/v2/venues/search`
  - Params: `client_id`, `client_secret`, `v` (date), `query`, `ll`, `radius`, `limit`
  - Use `httpx.AsyncClient` (not requests)
  - Return empty list on error, log error
- [x] Implement `_normalize(venue: dict) -> dict` that extracts:
  - `fsq_id`, `name`, `rating`, `review_count`, `price`, `address`, `neighborhood`
  - `categories` (list of strings), `is_closed`, `photos` (list), `url`, `coordinates`, `distance`
- [x] Implement `async def get_details(venue_id: str) -> dict`
  - GET `https://api.foursquare.com/v2/venues/{venue_id}`
- [x] Test: search "coffee" near Williamsburg → returns list of venues with expected fields

---

## Phase 4 — Backend: Vibe Engine

File: `backend/vibe_engine.py`

- [x] Implement `compute_underground_score(venue: dict, web_signals: dict) -> int`
  - Start at 100
  - Penalize: review_count > 2000 (-50), > 1000 (-35), > 500 (-20), > 200 (-10)
  - Penalize: known chain names (-60) — list: starbucks, dunkin, mcdonald, subway, chipotle, sweetgreen, blue bottle, gregorys, joe coffee
  - Penalize: listicle_appearances > 5 (-25), > 2 (-10)
  - Reward: reddit_mentions * 8 (max +25)
  - Reward: niche_blog_count * 5 (max +15)
  - Reward: review_count < 100 AND rating >= 4.0 (+15)
  - Clamp to 0–100
- [x] Implement `tag_aesthetic(venue: dict, agent_analysis: str) -> list[str]`
  - Returns 3–5 single-word vibe tags from: contemporary, cozy, industrial, minimal, eclectic, vintage, bright, dark, intimate, spacious
- [x] Implement `tag_accessibility(venue: dict, web_signals: dict) -> str`
  - Returns: "walk-in" | "usually available" | "book ahead" | "impossible to get in"
  - Use review_count, price level, and Reddit reservation mentions as signals

---

## Phase 5 — Agent: VenueResearchAgent

File: `agent/agent.py`

- [x] Set env vars at top of file (BEFORE any ADK imports):
  ```python
  os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
  os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID")
  os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")
  ```
- [x] Call `vertexai.init(project=..., location=...)` after env vars
- [x] Import `from google.adk.tools import google_search` (built-in, no config needed)
- [x] Import `from google.adk.agents import LlmAgent`
- [x] Create `YelpClient()` and `NominatimClient()` instances at module level
- [x] Implement `async def search_yelp_venues(query: str, location: str, tool_context) -> dict`
  - Call `nominatim_client.geocode(location)` to get lat/lon
  - Call `yelp_client.search(term=query, lat=lat, lon=lon)`
  - Return `{"venues": [...], "count": n, "location": location}`
- [x] Define `AGENT_INSTRUCTION` string (see PRODUCT-PLAN.md for full text)
  - Key points: search Yelp first, then google_search for Reddit/blog signals, synthesize vibe profiles, rank by mood match not rating, prioritize walk-in accessible spots
- [x] Create `root_agent = LlmAgent(name="VenueResearchAgent", model="gemini-2.5-flash", instruction=AGENT_INSTRUCTION, tools=[search_yelp_venues, google_search])`
- [x] Implement `async def run_venue_search(mood_query, location, time_of_day, open_now) -> list[dict]`
  - Create `InMemorySessionService` session
  - Create `Runner` with `root_agent`
  - Run with user message: `f"Find venues for: {mood_query} in {location} during {time_of_day}"`
  - Parse response text into list of venue dicts
  - Return sorted by underground score

---

## Phase 6 — Backend: FastAPI

File: `backend/main.py`

- [x] Same Vertex AI env/init setup as agent/agent.py (at top)
- [x] Create `FastAPI` app with CORS middleware (`allow_origins=["*"]`)
- [x] Define `SearchRequest` Pydantic model: `mood_query: str`, `location: str = "Lower East Side, NYC"`, `time_of_day: str = "morning"`, `open_now: bool = True`, `vibe_dims: Optional[dict] = None`
- [x] Implement `POST /api/search` — calls `run_venue_search`, returns ranked venues JSON
- [x] Implement `GET /api/venue/{yelp_id}` — calls `YelpClient().get_details(yelp_id)`
- [x] Implement `GET /api/health` — returns `{"status": "ok"}`
- [ ] Test: `curl -X POST localhost:8000/api/search -H "Content-Type: application/json" -d '{"mood_query":"cozy coffee morning","location":"Williamsburg, Brooklyn"}'`
  - Verify: returns JSON with `venues` array, each with `name`, `underground_score`, `vibe_tags`, `accessibility`

---

## Phase 7 — Frontend: Scaffold

- [x] Copy `sharepoint_wif_portal/frontend/package.json` and adapt (remove MSAL dependencies: `@azure/msal-browser`, `@azure/msal-react`)
- [x] Keep: `react`, `react-dom`, `vite`, `lucide-react`, `react-markdown`, `typescript`
- [x] Create `vite.config.ts` with proxy: `/api` → `http://localhost:8000`
- [x] Create `frontend/.env` with `VITE_API_BASE_URL=http://localhost:8000`
- [x] Run `npm install`

---

## Phase 8 — Frontend: Design System

File: `frontend/src/index.css`

- [x] Define CSS variables (dark palette):
  - `--bg-primary: #0F0F0F`
  - `--bg-secondary: #1A1A1A`
  - `--bg-card: #1F1F1F`
  - `--bg-elevated: #252525`
  - `--accent-amber: #F59E0B` (underground scores, highlights)
  - `--accent-teal: #14B8A6` (vibe match)
  - `--accent-rose: #F43F5E` (accessibility warning)
  - `--text-primary: #F5F5F5`
  - `--text-secondary: #9CA3AF`
  - `--text-muted: #6B7280`
  - `--border-subtle: rgba(255,255,255,0.08)`
- [x] Global reset: `body { background: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', system-ui }`
- [x] Define layout classes: `.app-header`, `.search-section`, `.results-grid`, `.venue-card`
- [x] `.results-grid`: CSS grid, 1 col mobile, 2 col tablet (768px), 3 col desktop (1200px)
- [x] `.venue-card`: dark bg, subtle border, hover elevation effect, cursor pointer
- [x] `.underground-badge`: amber hexagon shape, font-weight bold
- [x] `.vibe-tag`: small pill, `bg-elevated`, `text-secondary`
- [x] `.accessibility-badge`: color-coded — teal for walk-in, amber for book ahead, rose for impossible

---

## Phase 9 — Frontend: VenueCard Component

File: `frontend/src/VenueCard.tsx`

- [x] Props: `venue: VenueResult` (define TypeScript interface)
  - `name`, `yelp_id`, `rating`, `review_count`, `price`, `address`, `distance`
  - `photos: string[]`, `underground_score: number`, `vibe_tags: string[]`
  - `accessibility: string`, `best_time: string`, `vibe_summary: string`
  - `url: string`, `coordinates: {latitude, longitude}`
- [x] Render: photo (img with fallback gradient), name, underground score badge, vibe tags, accessibility badge, distance, vibe_summary
- [x] Hover state: show full vibe breakdown + "Open in Yelp" link
- [x] Photo fallback: dark gradient with category emoji if `photos` is empty

---

## Phase 10 — Frontend: VibeDials Component

File: `frontend/src/VibeDials.tsx`

- [x] Props: `onSearch: (params: SearchParams) => void`
- [x] State: `mood_query: string`, `location: string`, `time_of_day: string`, `sliders: Record<string, number>`
- [x] Render natural language input (primary) — large text input with placeholder "Describe your vibe..."
- [x] Render time-of-day tabs: 🌅 Morning | ☀️ Afternoon | 🌆 Evening | 🌙 Night
- [x] Render collapsible "Dial it in" section with 5 range sliders:
  - Energy (Calm ↔ Buzzing)
  - Accessibility (Walk-in ↔ Book ahead)
  - Crowd vibe (Local regulars ↔ Scene crowd)
  - Aesthetic (Minimal ↔ Eclectic)
  - Sound (Silent ↔ Lo-fi ↔ Live)
- [x] On submit: call `onSearch` with merged NL query + slider values

---

## Phase 11 — Frontend: NeighborhoodPicker Component

File: `frontend/src/NeighborhoodPicker.tsx`

- [x] Props: `value: string`, `onChange: (v: string) => void`
- [x] Text input with suggestions dropdown
- [x] Pre-populate suggestions: Williamsburg, Lower East Side, Nolita, West Village, Astoria, Bed-Stuy, Carroll Gardens, Greenpoint, Bushwick, Harlem, Chelsea, Tribeca
- [x] "Use my location" button → `navigator.geolocation.getCurrentPosition` → reverse geocode display name

---

## Phase 12 — Frontend: App.tsx (Main Layout)

File: `frontend/src/App.tsx`

- [x] No auth (no MSAL) — public app
- [x] State: `venues: VenueResult[]`, `isLoading: boolean`, `error: string | null`, `location: string`
- [x] Layout:
  - Header: `◆ VIBES` logo + NeighborhoodPicker + time-of-day display
  - Search section: VibeDials component
  - Results section: count label + VenueCard grid OR empty state
  - Loading state: skeleton cards (3 placeholder cards with shimmer animation)
- [x] `handleSearch(params)`:
  - `POST /api/search` with `mood_query`, `location`, `time_of_day`, `open_now: true`
  - Set loading, clear error, update venues on response
- [x] Empty state: "No spots found for this vibe — try broadening your search"
- [x] Error state: show error message with retry button

---

## Phase 13 — End-to-End Test

- [x] Start backend: `cd backend && uv run uvicorn main:app --reload`
- [x] Start frontend: `cd frontend && npm run dev`
- [x] Open `http://localhost:5173`
- [x] UI loads correctly with dark moody design
- [x] Search flow works (triggers agent, shows loading, handles empty results)
- [x] **USING FOURSQUARE** (free tier, 200K calls/month) instead of Yelp ($229+/month)
- [x] Verify: results appear with venue names, underground scores, vibe tags
- [x] Verify: underground scores show (100-115 for local spots)
- [x] Verify: accessibility badges show "Walk-in" correctly
- [x] Verify: vibe summaries are 2 sentences and contextual
- [x] Search: "late night cocktails, moody lighting, interesting crowd" in Williamsburg
- [x] Verify: different results (cocktail bars vs coffee shops), appropriate for night context
- [x] Test mobile: resize browser to 375px wide — verify 1-column grid, readable cards

---

## Phase 14 — README

File: `README.md`

- [x] Tagline: *No star ratings. No tourist traps. Just the right place for how you feel.*
- [x] 3-sentence description of what the app does
- [x] Quick start (backend + frontend commands)
- [x] `.env.example` callout
- [x] API stack table (Foursquare free 200K/month, Nominatim, Vertex AI)
- [x] Screenshot of the UI (docs/screenshot.png)

---

## If Anything Is Unclear

1. Read `PRODUCT-PLAN.md` — it has the full architecture, code samples, and reasoning
2. Reference `semiautonomous-agents/sharepoint_wif_portal/` for ALL patterns — the new app follows the same structure
3. The `google_search` ADK tool is truly built-in — `from google.adk.tools import google_search` — no configuration needed
4. Yelp API key must be obtained by the user from `https://api.yelp.com` before this can run end-to-end
5. Vertex AI authentication: `gcloud auth application-default login` sets up ADC automatically
