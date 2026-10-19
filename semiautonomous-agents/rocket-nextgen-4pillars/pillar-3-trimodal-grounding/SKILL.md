---
name: pillar-3-trimodal-grounding
description: Step-by-step LLM replication skill to build and deploy Pillar 3 (Tri-Modal Grounding with Google Maps, YouTube Video, and Google Search) from scratch for Rocket Companies & Redfin.
---

# SKILL: Replicating Pillar 3 (`Tri-Modal Grounding` "Ask Redfin 2.0") From Scratch

Any frontier coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) can rebuild Pillar 3 from zero by executing the following 4 engineering steps:

## Step 1: Initialize the Vertex AI GenAI SDK Client

Use the official `google-genai` SDK (`google-genai >= 2.31.0`):

```python
import os
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
# Global endpoint for Gemini 3.8 Flash multi-tool grounding
client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
```

## Step 2: Implement the Tri-Modal Grounding Configuration

```python
def build_grounding_config(lat: float, lng: float, include_maps: bool = True, include_search: bool = True):
    tools = []
    if include_maps:
        tools.append(types.Tool(google_maps=types.GoogleMaps()))
    if include_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))
    
    tool_config = None
    if include_maps:
        tool_config = types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(latitude=lat, longitude=lng)
            )
        )
    
    return types.GenerateContentConfig(
        tools=tools,
        tool_config=tool_config,
        temperature=0.2,
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
    )
```

## Step 3: Implement YouTube Video Ingestion & Dual-Flight Race Guard

```python
async def stream_grounded_chat(messages, hub, youtube_url=""):
    """Streams NDJSON events: route, status, delta, sources, done."""
    # 1. Inspect user query and determine active routes (maps, youtube, search)
    routes = route_question(messages[-1]["text"])
    yield {"type": "route", "tools": routes, "hub_id": hub["id"]}
    
    # 2. Attach YouTube video Part if requested
    video_part = types.Part.from_uri(file_uri=youtube_url, mime_type="video/mp4") if "youtube" in routes else None
    
    # 3. 8-second tail-latency hedge: dispatch twin worker if first token has not arrived
    queue = asyncio.Queue()
    task1 = asyncio.create_task(run_worker(tag=1, queue=queue, ...))
    
    # Monitor queue with heartbeat status events
    # If time.perf_counter() - t0 > 8.0s and no token, spawn task2
    # Cancel the losing task when winner emits first chunk
```

## Step 4: Resolve Places API (New) Coordinates for Map Pins

```python
import urllib.request
import json
import google.auth
import google.auth.transport.requests

def resolve_place_coordinates(place_id: str, project_id: str) -> dict:
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {creds.token}",
            "X-Goog-User-Project": project_id,
            "X-Goog-FieldMask": "location,primaryTypeDisplayName",
        }
    )
    with urllib.request.urlopen(req, timeout=3.0) as resp:
        data = json.loads(resp.read().decode())
        loc = data.get("location", {})
        return {
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
            "type": (data.get("primaryTypeDisplayName") or {}).get("text", "Place")
        }
```

## Step 5: Verification & CLI Testing

```bash
python3 -c "import engine; print(engine.PROPERTY_HUBS['royal_oak']['address'])"
python3 pillar-3-trimodal-grounding/engine.py
```
