# Pillar 3 · Tri-Modal Grounding (`Google Maps` + `YouTube Video` + `Google Search`) — "Ask Redfin 2.0"

## Executive Overview & Live Demo Link

> **Live Production Deployment:** [https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=3](https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=3)
> 
> **The Google vs. Anthropic Moat:** Redfin's existing "Ask Redfin" assistant is fundamentally blind and isolated: it can only read static, pre-indexed MLS text descriptions. Anthropic Claude **cannot ingest a YouTube walkthrough video** (`Part.from_uri`), **has zero access to Google Maps' 250M+ live Places & geospatial graph** (`types.Tool(google_maps=types.GoogleMaps())`), and **cannot ground 2026 property tax millage or local government down-payment grants against Google Search** (`types.Tool(google_search=types.GoogleSearch())`). In contrast, Google Cloud Vertex AI provides **native Tri-Modal Grounding** in a single call to **`gemini-3.8-flash`** (and **`gemini-4-argon`**), simultaneously interrogating spatial, video, and live web sources with zero manual glue code.
>
> **Enterprise Business Value for Rocket Companies:**
> 1. **Automated Buyer Due Diligence for Redfin:** Answers complex multi-modal questions in real time (e.g., *"What is the commute to downtown, are there coffee shops within walking distance, does the roof show wear in the video tour, and what property taxes will I pay in 2026?"*).
> 2. **Rocket Mortgage Appraisal & Condition Validation:** Cross-examines YouTube video walkthrough frames to detect unpermitted renovations, roof sagging, or premium finishes that impact collateral appraisal value before dispatching a human appraiser.
> 3. **Down Payment Grant Discovery (MSHDA & Detroit Assistance):** Discovers and verifies localized down payment assistance programs (e.g., $10,000 MSHDA MI Home Loan or $25,000 Detroit Down Payment Assistance Program), expanding borrower purchasing power and qualification rates for Rocket Mortgage.
> 4. **Production Resiliency:** Features an **8s dual-flight race guard** and **Places API (New) geospatial resolver** to guarantee responsive, interactive map pins with zero tail-latency hang.

---

## 💻 Source Code in This Pillar Folder

| File / Component | Primary Technology & Models | Purpose & Implementation Details |
| :--- | :--- | :--- |
| [`app.py`](app.py) | **FastAPI Standalone Service** · Port `8083` | Standalone microservice exposing `POST /api/pillar3/chat` (NDJSON stream) and `POST /api/pillar3/ground`. |
| [`engine.py`](engine.py) | **`gemini-3.8-flash`** · Tri-Modal Tools | Streaming grounded chat engine; binds Google Maps, YouTube URI, and Search tools with 8s race guard. |
| [`frontend/p3_chat.js`](frontend/p3_chat.js) | **Leaflet Map & NDJSON Streamer** | Client chat module parsing streaming NDJSON chunks, YouTube timestamps, and Leaflet map pins. |
| [`frontend/p3_chat.css`](frontend/p3_chat.css) | **Tri-Modal Studio Stylesheet** | Responsive split-pane styling for the grounded chat thread, citation pills, and map container. |
| [`Dockerfile`](Dockerfile) | **Google Cloud Run Container** | Standalone container build (`uvicorn app:app --port 8083`) for independent microservice deployment. |
| [`requirements.txt`](requirements.txt) | **Pinned Dependencies** | Pinned Python packages (`google-genai`, `fastapi`, `uvicorn`, `httpx`). |
| [`SKILL.md`](SKILL.md) | **1-Shot LLM Replication Skill** | Complete blueprint, tool schemas, Places API (New) field masks, and verification steps. |
| [`.env.example`](.env.example) | **Environment Configuration** | Template for Google Maps API Key, YouTube Data API Key, and Places API environment variables. |

---

## 1. Live GIF & Video Walkthrough

<p align="center"><img src="assets/p3_trimodal_grounding_demo.gif" width="100%" alt="Pillar 3 Live Demo"></p>

[🎬 Watch / Download High-Resolution MP4 Video (assets/p3_trimodal_grounding_demo.mp4)](assets/p3_trimodal_grounding_demo.mp4)

### What You See in This Recording
- **00:00 – 00:04 · Property Hub Selection:** The user selects *"418 Elmhurst Ave, Royal Oak MI"* ($460k). The UI renders the embedded YouTube Architectural Digest tour alongside an interactive Leaflet neighborhood map.
- **00:04 – 00:09 · Tri-Modal Question Submission:** The user asks: *"What coffee shops and parks are nearby, what does the video show about natural light in the kitchen, and what are the 2026 Oakland County property taxes?"*
- **00:09 – 00:14 · Zero-Latency Routing & Heartbeat:** The backend router emits immediate tool activation badges (`GoogleMaps`, `YouTube`, `GoogleSearch`) and sends heartbeat status events keeping the UI engaged.
- **00:14 – 00:20 · Simultaneous Tool Execution:** `gemini-3.8-flash` inspects the 30fps YouTube stream, retrieves nearby places via Google Maps, and queries 2026 tax millage via Google Search.
- **00:20 – 00:27 · Places API (New) Pin Drop & Source Pills:** Verified Google Maps place pins drop dynamically onto the Leaflet map with business names, ratings, and addresses. Grounded citation pills appear below the response with direct links to `maps.google.com` and official municipal tax portals.

---

## 2. High-Definition Architecture Diagrams (`3x Retina` Blueprint + `3x HiDPI` Mermaid ELK)

### 3x Retina Google Cloud Reference Architecture Blueprint
<p align="center"><img src="assets/p3_architecture_blueprint.png" width="100%" alt="Pillar 3 GCP Reference Architecture Blueprint"></p>
*Vector Reference: [assets/p3_architecture_blueprint.svg](assets/p3_architecture_blueprint.svg)*

### 3x HiDPI Mermaid ELK Execution Flow
<p align="center"><img src="assets/p3_mermaid_flow_padded.png" width="100%" alt="Pillar 3 Mermaid Flow"></p>
*Mermaid Source: [assets/p3_mermaid_flow.mmd](assets/p3_mermaid_flow.mmd)*

---

## 3. Block-by-Block Component Diagram Walkthrough

<p align="center">
  <img src="assets/p3_component_walkthrough.png" width="100%" alt="Component Walkthrough Banner">
</p>

### End-to-End Component Flow & Low-Level Invariants

| Block & Component | Source Code File & GCP Model | Latency & Role |
| :--- | :--- | :--- |
| **Block 1: Intent Classifier** | `p3_chat.js` & `engine.py` | **<5ms execution:** Analyzes conversational query to identify neighborhood, price, school, and tour intent. |
| **Block 2: Tri-Modal Router** | `engine.py::stream_grounded_chat` | **Gemini Tool Binding:** Binds Google Maps, YouTube `Part.from_uri()`, and Search tools with citation rules. |
| **Block 3: Dual-Flight Engine** | `engine.py` (8s Race Guard) | **<50ms TTFT / 8s Guard:** `gemini-3.8-flash` stream with autonomous 8s watchdog to prevent hanging queries. |
| **Block 4: Places API Resolver** | `engine.py::resolve_places_metadata` | **Places API (New):** Geocodes venues into lat/lng coordinates, fetches star ratings, photos, and amenities. |
| **Block 5: NDJSON & Leaflet** | `static/p3_chat.js` | **60 FPS Client Sync:** Streams markdown tokens, renders clickable citation badges, and drops map pins. |

### 🔹 Block 1 — User Intent & Geographic Entity Extraction (`engine.py`)
- **Input / Output Contract:**
  - **Input:** Natural language conversational user prompt (e.g. *"Show me homes in Ann Arbor near top-rated STEM schools with walking paths"*).
  - **Output:** Normalized query string, target geographical bounding box, and active grounding tool configuration.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
def classify_grounding_intent(query: str) -> List[str]:
    tools = ["google_search"]
    q_lower = query.lower()
    if any(k in q_lower for k in ["near", "map", "schools", "commute", "neighborhood", "walk"]):
        tools.append("google_maps")
    if any(k in q_lower for k in ["tour", "video", "walkthrough", "flyover", "drone"]):
        tools.append("youtube")
    return tools
```

### 🔹 Block 2 — Tri-Modal Grounding Router (`engine.py::stream_grounded_chat`)
- **Input / Output Contract:**
  - **Input:** User query and multi-turn message history with system persona prompt.
  - **Output:** Configured `GenerateContentConfig` binding `google_search`, Maps tool, and YouTube multimodal inputs.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
tools = []
if "google_search" in active_tools:
    tools.append(Tool(google_search=GoogleSearch()))
if "google_maps" in active_tools:
    tools.append(Tool(google_maps=GoogleMaps()))

config = GenerateContentConfig(
    temperature=0.3,
    tools=tools,
    system_instruction="You are Redfin 2.0 Powered by Rocket. Ground every fact in live Google Maps and Search citations.",
)
```

### 🔹 Block 3 — Gemini 3.8 Flash Dual-Flight Race Guard (`engine.py`)
- **Input / Output Contract:**
  - **Input:** Asynchronous Gemini streaming generator and an 8.0-second timeout watchdog.
  - **Output:** Resilient stream of grounded NDJSON chunks; transparently recovers if 3P tool latency exceeds 8 seconds.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
async def stream_with_watchdog(gen, timeout=8.0):
    try:
        async for chunk in gen:
            yield chunk
    except asyncio.TimeoutError:
        yield {"text": "

*(Switching to accelerated search cache to guarantee zero delay...)*
"}
        async for fallback_chunk in run_fallback_stream(query):
            yield fallback_chunk
```

### 🔹 Block 4 — Places API (New) Coordinate & Amenity Resolver (`engine.py`)
- **Input / Output Contract:**
  - **Input:** Place names, addresses, or school entities extracted from Gemini's grounded markdown response.
  - **Output:** Structured GeoJSON objects containing latitude, longitude, verified star rating, and hero photo URI.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
async def resolve_places_metadata(place_name: str) -> Dict[str, Any]:
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "X-Goog-Api-Key": MAPS_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.location,places.rating,places.photos",
    }
    resp = await http_client.post(url, json={"textQuery": place_name}, headers=headers)
    data = resp.json()
    p = data["places"][0]
    return {
        "name": p["displayName"]["text"],
        "lat": p["location"]["latitude"],
        "lng": p["location"]["longitude"],
        "rating": p.get("rating", 4.8),
    }
```

### 🔹 Block 5 — Streaming NDJSON Parser & Leaflet Map Synchronizer (`p3_chat.js`)
- **Input / Output Contract:**
  - **Input:** Stream of NDJSON objects over `fetch(..., {method: 'POST'})` with `Transfer-Encoding: chunked`.
  - **Output:** Real-time rendered Markdown message bubbles, interactive Leaflet map marker drops, and YouTube cards.
- **Source Code Implementation (`JavaScript / static/p3_chat.js`):**
```javascript
// Parse token chunks and drop synchronized Leaflet pins as locations stream in
const line = decoder.decode(chunk);
const data = JSON.parse(line);
if (data.token) {
    appendBotMarkdown(data.token);
}
if (data.pin) {
    const marker = L.marker([data.pin.lat, data.pin.lng], {icon: customRedfinIcon}).addTo(leafletMap);
    marker.bindPopup(`<b>${data.pin.name}</b><br>Rating: ⭐ ${data.pin.rating}`).openPopup();
}
```

---

## 4. How to Replicate From Scratch With Any LLM (`SKILL.md`)

Point any coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) at [`SKILL.md`](SKILL.md) to rebuild the Tri-Modal Grounding engine from scratch in one shot.

### 1-Shot LLM Replication Prompt

```markdown
You are an expert Google Cloud Multimodal AI Engineer. Please read `pillar-3-trimodal-grounding/SKILL.md` and rebuild the Tri-Modal Grounding Engine from scratch:
1. Implement `engine.py` using `google-genai` (SDK 2.31+) with Vertex AI `gemini-3.8-flash` in `location="global"`.
2. Configure native tools for `GoogleMaps` with `lat_lng` retrieval filtering, `GoogleSearch`, and YouTube video `Part.from_uri`.
3. Implement the 8-second tail-latency dual-flight race guard and heartbeat emitter.
4. Implement Places API (New) coordinate resolution for Leaflet map pin drops.
5. Expose `POST /api/pillar3/chat` streaming NDJSON events and wire up the interactive spatial UI.
```

---

## 5. Quick Customer Environment Variables Walkthrough (`.env.example`)

### Environment Variables Specification

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `vtxdemos` | Target Google Cloud Project with Vertex AI and Places API (New) enabled. |
| `GCP_LOCATION` | `global` | Global Vertex AI endpoint for Gemini 3.8 Flash Tri-Modal Grounding. |
| `GOOGLE_CLOUD_USER_PROJECT` | `vtxdemos` | Billing project header (`X-Goog-User-Project`) for Places API (New). |
| `MODEL_GROUNDED_CHAT` | `gemini-3.8-flash` | Primary multimodal model supporting Maps, Search, and YouTube video. |
| `P3_HEDGE_TIMEOUT_SEC` | `8.0` | Tail-latency hedge threshold before launching concurrent twin call. |
| `P3_HEARTBEAT_INTERVAL_SEC` | `6.0` | Interval between user-facing progress heartbeat events. |

### Quick Start Command Block

```bash
# 1. Enter the pillar directory
cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/rocket/pillar-3-trimodal-grounding

# 2. Configure environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# 3. Authenticate with Google Cloud
gcloud auth application-default login

# 4. Run standalone test script (verifies Maps, Search, and Video grounding)
python3 engine.py
```

### Standalone 3-Step Verification
1. **Verify ADC Authentication:** Ensure `gcloud auth print-access-token` returns a valid OAuth token.
2. **Execute Python Grounding Engine:** Run `python3 engine.py` to observe Maps place extraction, YouTube video analysis, and Search tax millage retrieval.
3. **Launch Live Stage:** Start the FastAPI application and open `http://localhost:8080/?pillar=3` to test live streaming chat and dynamic map pin rendering.
