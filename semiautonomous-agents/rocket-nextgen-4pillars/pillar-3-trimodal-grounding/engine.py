"""Pillar 3: Tri-Modal Grounding Engine (Google Maps + YouTube Video URI + Google Search) powered by Gemini 4 Argon & Gemini 3.8 Flash."""

import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import re
import time
from typing import Any, AsyncIterator, Dict, List, Optional
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "global")

# All YouTube IDs below are verified public Architectural Digest "Open Door" home tours via YouTube oEmbed API
PROPERTY_HUBS: Dict[str, Dict[str, Any]] = {
    "royal_oak": {
        "id": "royal_oak",
        "address": "418 Elmhurst Ave, Royal Oak, MI 48067",
        "price": "$460,000",
        "lat": 42.4962,
        "lng": -83.1477,
        "youtube_id": "AwhBTrzzqeg",
        "youtube_url": "https://www.youtube.com/watch?v=AwhBTrzzqeg",
        "youtube_title": "Architectural Digest · Mid-Century Craftsman & Garden Tour",
        "maps_query": "Top coffee shops, parks, elementary schools, and grocery stores within 1.5 miles of 418 Elmhurst Ave, Royal Oak, MI 48067",
        "search_query": "2026 Oakland County Royal Oak Michigan property tax millage rate and MSHDA MI Home Loan $10,000 down payment assistance eligibility",
        "video_prompt": "Analyze this home tour clip in 3 concise bullet points (under 45 words total, no emojis): highlight natural light, architectural woodwork/materials, and appraisal appeal for a Rocket Mortgage buyer.",
    },
    "corktown_detroit": {
        "id": "corktown_detroit",
        "address": "1420 Michigan Ave #4B, Corktown, Detroit, MI 48216",
        "price": "$385,000",
        "lat": 42.3314,
        "lng": -83.0645,
        "youtube_id": "PqpCeiYycVM",
        "youtube_url": "https://www.youtube.com/watch?v=PqpCeiYycVM",
        "youtube_title": "Architectural Digest · Sunlit Modern Interior & Custom Kitchen Tour",
        "maps_query": "Best cafes, restaurants, parks, and transit stops near Michigan Central Station and 1420 Michigan Ave in Corktown, Detroit, MI 48216",
        "search_query": "Detroit Down Payment Assistance Grant $25,000 program and Neighborhood Enterprise Zone (NEZ) property tax abatement in Corktown Detroit",
        "video_prompt": "Analyze this home tour clip in 3 concise bullet points (under 45 words total, no emojis): highlight interior styling, daylighting, and kitchen/living finish quality.",
    },
    "ann_arbor": {
        "id": "ann_arbor",
        "address": "2105 Devonshire Rd, Ann Arbor, MI 48104",
        "price": "$695,000",
        "lat": 42.2682,
        "lng": -83.7191,
        "youtube_id": "EobMnSpjfTU",
        "youtube_url": "https://www.youtube.com/watch?v=EobMnSpjfTU",
        "youtube_title": "Architectural Digest · Mid-Century Modern Sanctuary & Courtyard Tour",
        "maps_query": "Parks, schools, coffee shops, and hospitals near Burns Park and 2105 Devonshire Rd, Ann Arbor, MI 48104",
        "search_query": "Washtenaw County Ann Arbor Michigan principal residence exemption (PRE) property tax millage rate and conforming vs jumbo mortgage limits 2026",
        "video_prompt": "Analyze this architectural tour clip in 3 concise bullet points (under 45 words total, no emojis): highlight mid-century design details, indoor-outdoor flow, and structural condition.",
    },
}


def _call_google_maps_grounding(query: str, lat: float, lng: float) -> Dict[str, Any]:
    # Uses newest Argolis model `gemini-4-argon` (with `gemini-3.8-flash` fallback) in `location="global"`
    client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    model_used = "gemini-4-argon"
    try:
        resp = client_global.models.generate_content(
            model="gemini-4-argon",
            contents=f"{query}. Keep your summary to 3 crisp bullet points under 50 words total. No emojis.",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=lat, longitude=lng)
                    )
                ),
                temperature=0.2,
                thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            ),
        )
    except Exception:
        model_used = "gemini-3.8-flash"
        resp = client_global.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"{query}. Keep your summary to 3 crisp bullet points under 50 words total. No emojis.",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=lat, longitude=lng)
                    )
                ),
                temperature=0.2,
                thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            ),
        )

    places: List[Dict[str, str]] = []
    gm = resp.candidates[0].grounding_metadata if resp.candidates else None
    for ch in (getattr(gm, "grounding_chunks", None) or []):
        m = getattr(ch, "maps", None)
        if m and getattr(m, "title", None):
            places.append({
                "title": m.title.replace(" - Google Maps", ""),
                "place_id": getattr(m, "place_id", "") or "",
                "uri": getattr(m, "uri", "") or "https://maps.google.com",
            })
    return {
        "model": model_used,
        "summary": resp.text or "",
        "places": places[:8],
    }


def _call_google_search_grounding(query: str) -> Dict[str, Any]:
    client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    resp = client_global.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"{query}. Provide 3 concise, number-backed bullet points under 55 words total. No emojis.",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.2,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        ),
    )
    sources: List[Dict[str, str]] = []
    gm = resp.candidates[0].grounding_metadata if resp.candidates else None
    for ch in (getattr(gm, "grounding_chunks", None) or []):
        w = getattr(ch, "web", None)
        if w and getattr(w, "uri", None):
            sources.append({
                "title": getattr(w, "title", None) or getattr(w, "domain", "Web Source"),
                "domain": getattr(w, "domain", "") or "",
                "uri": w.uri,
            })
    return {
        "model": "gemini-3.8-flash",
        "summary": resp.text or "",
        "sources": sources[:6],
    }


def _call_youtube_video_grounding(youtube_url: str, video_prompt: str) -> Dict[str, Any]:
    # Uses `gemini-3.8-flash` (`location="global"`) with a 12-second `VideoMetadata` window for ~2.5s latency
    client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    resp = client_global.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            types.Part(
                file_data=types.FileData(file_uri=youtube_url, mime_type="video/mp4"),
                video_metadata=types.VideoMetadata(start_offset="0s", end_offset="12s"),
            ),
            video_prompt,
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        ),
    )
    return {
        "model": "gemini-3.8-flash",
        "youtube_url": youtube_url,
        "summary": resp.text or "",
    }


def run_trimodal_grounding(
    hub_id: str = "royal_oak",
    custom_maps_query: str = "",
    custom_search_query: str = "",
    custom_youtube_url: str = "",
) -> Dict[str, Any]:
    """Executes Google Maps Grounding + YouTube Video URI Grounding + Google Search Grounding concurrently."""
    t0 = time.perf_counter()
    hub = PROPERTY_HUBS.get(hub_id, PROPERTY_HUBS["royal_oak"]).copy()

    maps_q = (custom_maps_query or "").strip() or hub["maps_query"]
    search_q = (custom_search_query or "").strip() or hub["search_query"]
    yt_url = (custom_youtube_url or "").strip() or hub["youtube_url"]

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_maps = pool.submit(_call_google_maps_grounding, maps_q, hub["lat"], hub["lng"])
        f_search = pool.submit(_call_google_search_grounding, search_q)
        f_yt = pool.submit(_call_youtube_video_grounding, yt_url, hub["video_prompt"])

        try:
            maps_res = f_maps.result(timeout=15)
        except Exception as e:
            maps_res = {"model": "gemini-4-argon", "summary": f"Maps grounding note: {e}", "places": []}

        try:
            search_res = f_search.result(timeout=15)
        except Exception as e:
            search_res = {"model": "gemini-3.8-flash", "summary": f"Search grounding note: {e}", "sources": []}

        try:
            yt_res = f_yt.result(timeout=15)
        except Exception as e:
            yt_res = {"model": "gemini-3.8-flash", "youtube_url": yt_url, "summary": f"YouTube inspection note: {e}"}

    latency_ms = int((time.perf_counter() - t0) * 1000)
    return {
        "ok": True,
        "pillar": "Pillar 3 · Tri-Modal Grounding (Google Maps + YouTube + Google Search)",
        "models_used": {
            "maps": maps_res.get("model", "gemini-4-argon"),
            "youtube": yt_res.get("model", "gemini-3.8-flash"),
            "search": search_res.get("model", "gemini-3.8-flash"),
        },
        "latency_ms": latency_ms,
        "hub": hub,
        "maps": maps_res,
        "search": search_res,
        "youtube": yt_res,
    }


# =============================================================================
# "ASK REDFIN 2.0" GROUNDED CHAT (STREAMING NDJSON EVENTS)
# Google Maps + YouTube Video + Google Search grounding on gemini-3.8-flash (global)
# =============================================================================
CHAT_MODEL = "gemini-3.8-flash"
_CHAT_CLIENT: Optional[genai.Client] = None
_PLACES_CREDS: Any = None

_YT_RE = re.compile(
    r"(?:https?://)?(?:www\.|m\.|music\.)?(?:youtube\.com/(?:watch\?(?:[^\s#]*&)?v=|shorts/|embed/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
_VIDEO_RE = re.compile(
    r"\b(video|youtube|walk-?\s?through|tour|clip|footage|watch|kitchen|interior|inside|rooms?|bedroom|bathroom|living\s?room|"
    r"design|finish(es)?|materials?|woodwork|natural\s+light|daylight|layout|floor\s?plan|architect\w*|condition|renovat\w*|decor|style|garden|backyard|yard)\b",
    re.I,
)
_MAPS_RE = re.compile(
    r"\b(walk(?:able|ability|ing|s)?|near\w*|around|close\s+to|distance|commute|transit|bus|train|station|coffee|caf[eé]s?|restaurants?|food|dining|eat|"
    r"parks?|schools?|grocer\w*|shops?|shopping|stores?|gyms?|hospitals?|doctors?|clinics?|daycare|bars?|neighbou?rhood|amenit\w*|places?|"
    r"things\s+to\s+do|downtown|drive|minutes|lifestyle|safe\w*|kids|family|pharmac\w*)\b",
    re.I,
)
_SEARCH_RE = re.compile(
    r"\b(tax\w*|millage|grants?|down[\s-]?payment|assistance|dpa|programs?|news|rates?|mortgage|loans?|insurance|prices?|market|trends?|"
    r"apprecia\w*|values?|zoning|permits?|laws?|regulat\w*|20\d\d|hoa|crime|flood\w*|costs?|afford\w*|incentives?|abatement|exemption|"
    r"fha|va|mshda|median|comps?|comparable|forecast|interest|closing|credit|lender|pre-?approv\w*|refinanc\w*|nez|pre)\b",
    re.I,
)
_ALL_RE = re.compile(r"\b(brief|overview|everything|all\s+(three|3)|full\s+(picture|report|rundown)|tri-?modal|ground\s+(this|the)\s+(home|property|listing))\b", re.I)

_STATUS_TEXT = {
    "maps": "Searching Google Maps near {short}…",
    "youtube": "Watching the YouTube walkthrough…",
    "search": "Checking Google Search for current sources…",
}


def _chat_client() -> genai.Client:
    global _CHAT_CLIENT
    if _CHAT_CLIENT is None:
        _CHAT_CLIENT = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    return _CHAT_CLIENT


def _heartbeats(routes: List[str]) -> List[tuple]:
    """Progress status lines emitted every ~6 s while waiting for the first token."""
    beats: List[tuple] = []
    if "youtube" in routes:
        beats.append(("youtube", "Still watching the walkthrough — analyzing frames…"))
    if "maps" in routes:
        beats.append(("maps", "Ranking nearby places by distance and rating…"))
    if "search" in routes:
        beats.append(("search", "Cross-checking current sources…"))
    beats.append(("", "Composing a grounded answer…"))
    return beats


def normalize_youtube_url(url: str) -> Dict[str, str]:
    """Returns {url, id} for a valid YouTube link, else {}."""
    m = _YT_RE.search(url or "")
    if not m:
        return {}
    vid = m.group(1)
    return {"id": vid, "url": f"https://www.youtube.com/watch?v={vid}"}


def route_question(text: str, prior_user_texts: List[str], has_custom_video: bool) -> List[str]:
    """Keyword router -> ordered subset of ['maps', 'youtube', 'search']. Zero-latency (no extra model hop)."""
    t = text or ""
    if _ALL_RE.search(t):
        return ["maps", "youtube", "search"]
    routes: List[str] = []
    if _MAPS_RE.search(t):
        routes.append("maps")
    if _VIDEO_RE.search(t) or _YT_RE.search(t):
        routes.append("youtube")
    if _SEARCH_RE.search(t):
        routes.append("search")
    if not routes:
        # Follow-ups ("tell me more", "which one is closest?") inherit the previous turn's grounding.
        for prev in reversed(prior_user_texts[-2:]):
            prev_routes = route_question(prev, [], False)
            if prev_routes:
                return prev_routes
        routes = ["youtube"] if has_custom_video else ["maps", "search"]
    order = ["maps", "youtube", "search"]
    return [r for r in order if r in routes]


def _system_instruction(hub: Dict[str, Any], yt: Dict[str, str], routes: List[str]) -> str:
    video_line = (
        f"Attached YouTube walkthrough: {yt.get('url')} ({hub.get('youtube_title', 'property walkthrough')})."
        if yt else "No video attached."
    )
    return (
        "You are Ask Redfin 2.0, the grounded home-buying assistant from Rocket Companies (Redfin + Rocket Mortgage), powered by Gemini on Vertex AI.\n"
        f"Current property: {hub['address']} (list price {hub['price']}), lat {hub['lat']}, lng {hub['lng']}.\n"
        f"{video_line}\n"
        "Current date: October 2026.\n"
        f"Grounding tools active for this turn: {', '.join(routes)}.\n"
        "Rules:\n"
        "- Start with one short lead sentence, then 3-5 tight markdown bullets with **bold** key facts. Keep it under 160 words unless asked for more.\n"
        "- Use concrete numbers when grounded: distances or drive/walk minutes, ratings, millage rates, dollar amounts, program names.\n"
        "- Places come from Google Maps grounding; taxes, grants, rates and news come from Google Search grounding.\n"
        "- For the video, describe only what is visible (materials, natural light, layout, finishes, condition) and relate it to the buyer; "
        "cite timestamps like [0:12] when helpful. Do not identify or name people in the video; call it the walkthrough.\n"
        "- If something is not verified by a tool, say so briefly. No emojis. No headings. Never invent sources or URLs."
    )


def _history_to_contents(messages: List[Dict[str, Any]], video_part: Optional[types.Part]) -> List[types.Content]:
    clean: List[Dict[str, str]] = []
    for m in (messages or [])[-14:]:
        role = "model" if str(m.get("role", "user")).lower() in ("model", "assistant", "ai") else "user"
        txt = str(m.get("text") or m.get("content") or "").strip()[:4000]
        if not txt:
            continue
        if clean and clean[-1]["role"] == role:
            clean[-1]["text"] += "\n\n" + txt
        else:
            clean.append({"role": role, "text": txt})
    while clean and clean[0]["role"] != "user":
        clean.pop(0)
    if not clean or clean[-1]["role"] != "user":
        clean.append({"role": "user", "text": "Give me a quick grounded brief on this home."})
    contents: List[types.Content] = []
    for i, m in enumerate(clean):
        parts: List[types.Part] = []
        if i == len(clean) - 1 and video_part is not None:
            parts.append(video_part)
        parts.append(types.Part(text=m["text"]))
        contents.append(types.Content(role=m["role"], parts=parts))
    return contents


def _video_part(yt_url: str, solo: bool = True) -> types.Part:
    # Video-only turns watch the first 60 s at 0.5 fps; multi-tool turns use a 30 s window to keep first-token latency low.
    return types.Part(
        file_data=types.FileData(file_uri=yt_url, mime_type="video/mp4"),
        video_metadata=types.VideoMetadata(start_offset="0s", end_offset="60s" if solo else "30s", fps=0.5),
    )


def _build_config(hub: Dict[str, Any], yt: Dict[str, str], routes: List[str], use_video: bool) -> types.GenerateContentConfig:
    tools: List[types.Tool] = []
    kwargs: Dict[str, Any] = {}
    if "maps" in routes:
        tools.append(types.Tool(google_maps=types.GoogleMaps()))
        kwargs["tool_config"] = types.ToolConfig(
            retrieval_config=types.RetrievalConfig(lat_lng=types.LatLng(latitude=hub["lat"], longitude=hub["lng"]))
        )
    if "search" in routes:
        tools.append(types.Tool(google_search=types.GoogleSearch()))
    if tools:
        kwargs["tools"] = tools
    if use_video:
        kwargs["media_resolution"] = types.MediaResolution.MEDIA_RESOLUTION_LOW
    return types.GenerateContentConfig(
        system_instruction=_system_instruction(hub, yt if use_video else {}, routes),
        temperature=0.3,
        max_output_tokens=1400,
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        **kwargs,
    )


def _collect_grounding(gm: Any, maps_out: Dict[str, Dict[str, Any]], web_out: Dict[str, Dict[str, Any]]) -> None:
    for ch in (getattr(gm, "grounding_chunks", None) or []):
        m = getattr(ch, "maps", None)
        if m and getattr(m, "title", None):
            title = str(m.title).replace(" - Google Maps", "").strip()
            key = getattr(m, "place_id", None) or title
            if key not in maps_out:
                maps_out[key] = {
                    "title": title,
                    "uri": getattr(m, "uri", None) or f"https://www.google.com/maps/search/?api=1&query={title}",
                    "place_id": getattr(m, "place_id", None) or "",
                }
        w = getattr(ch, "web", None)
        if w and getattr(w, "uri", None):
            domain = getattr(w, "domain", None) or ""
            title = getattr(w, "title", None) or domain or "Web source"
            key = f"{domain}|{title}" if domain else w.uri
            if key not in web_out:
                web_out[key] = {"title": title, "uri": w.uri, "domain": domain or title}


def _places_token() -> Optional[str]:
    """ADC access token for Places API (New) lookups (coordinates for the Leaflet markers)."""
    global _PLACES_CREDS
    try:
        import google.auth
        from google.auth.transport.requests import Request as _GARequest
        if _PLACES_CREDS is None:
            _PLACES_CREDS, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not _PLACES_CREDS.valid:
            _PLACES_CREDS.refresh(_GARequest())
        return _PLACES_CREDS.token
    except Exception:
        return None


async def _enrich_places(places: List[Dict[str, Any]]) -> None:
    """Adds real lat/lng (+ rating/address) to Maps-grounded places via Places API (New). Best effort, ~300 ms."""
    todo = [p for p in places if p.get("place_id")]
    if not todo:
        return
    try:
        import httpx
        token = await asyncio.to_thread(_places_token)
        if not token:
            return
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": PROJECT_ID,
            "X-Goog-FieldMask": "location,rating,userRatingCount,formattedAddress,primaryTypeDisplayName",
        }
        async with httpx.AsyncClient(timeout=2.5) as hc:
            async def one(p: Dict[str, Any]) -> None:
                pid = str(p["place_id"]).replace("places/", "")
                try:
                    r = await hc.get(f"https://places.googleapis.com/v1/places/{pid}", headers=headers)
                    if r.status_code != 200:
                        return
                    d = r.json()
                    loc = d.get("location") or {}
                    if "latitude" in loc and "longitude" in loc:
                        p["lat"] = loc["latitude"]
                        p["lng"] = loc["longitude"]
                    if d.get("rating") is not None:
                        p["rating"] = d.get("rating")
                    if d.get("userRatingCount") is not None:
                        p["reviews"] = d.get("userRatingCount")
                    if d.get("formattedAddress"):
                        p["address"] = d["formattedAddress"]
                    if (d.get("primaryTypeDisplayName") or {}).get("text"):
                        p["type"] = d["primaryTypeDisplayName"]["text"]
                except Exception:
                    return
            await asyncio.wait_for(asyncio.gather(*(one(p) for p in todo[:10])), timeout=3.0)
    except Exception:
        return


async def _attempt_worker(
    tag: int,
    att: Dict[str, Any],
    msgs: List[Dict[str, Any]],
    hub: Dict[str, Any],
    yt: Dict[str, str],
    queue: "asyncio.Queue[tuple]",
) -> None:
    """One streaming generate_content call; pushes (tag, kind, payload, grounding_metadata) tuples into queue."""
    try:
        video = _video_part(yt["url"], solo=len(att["routes"]) == 1) if att["video"] else None
        contents = _history_to_contents(msgs, video)
        cfg = _build_config(hub, yt, att["routes"], att["video"])
        stream = await _chat_client().aio.models.generate_content_stream(model=CHAT_MODEL, contents=contents, config=cfg)
        async for chunk in stream:
            cand = chunk.candidates[0] if chunk.candidates else None
            if cand is None:
                continue
            txt = ""
            for p in (getattr(getattr(cand, "content", None), "parts", None) or []):
                if getattr(p, "text", None) and not getattr(p, "thought", False):
                    txt += p.text
            await queue.put((tag, "chunk", txt, getattr(cand, "grounding_metadata", None)))
        await queue.put((tag, "end", None, None))
    except asyncio.CancelledError:
        raise
    except Exception as e:  # noqa: BLE001 - surfaced to the consumer, never raised
        await queue.put((tag, "error", f"{type(e).__name__}: {str(e)[:180]}", None))


async def stream_grounded_chat(
    messages: List[Dict[str, Any]],
    hub_id: str = "royal_oak",
    youtube_url: str = "",
) -> AsyncIterator[Dict[str, Any]]:
    """Grounded multi-turn chat. Yields NDJSON-ready events: status | delta | sources | done. Never raises."""
    t0 = time.perf_counter()
    hub = PROPERTY_HUBS.get(hub_id or "royal_oak", PROPERTY_HUBS["royal_oak"])
    msgs = [m for m in (messages or []) if isinstance(m, dict)]
    user_texts = [str(m.get("text") or "") for m in msgs if str(m.get("role", "user")).lower() not in ("model", "assistant", "ai")]
    last_q = user_texts[-1] if user_texts else ""

    custom = normalize_youtube_url(youtube_url) or normalize_youtube_url(last_q)
    yt = custom or {"id": hub["youtube_id"], "url": hub["youtube_url"]}
    routes = route_question(last_q, user_texts[:-1], bool(custom))
    short = hub["address"].split(",")[0]

    yield {"type": "route", "tools": routes, "hub_id": hub["id"], "model": CHAT_MODEL}
    for r in routes:
        yield {"type": "status", "tool": r, "text": _STATUS_TEXT[r].format(short=short)}

    # Attempt ladder: full multimodal config -> drop video -> plain search grounding (only before the first token).
    attempts: List[Dict[str, Any]] = [{"routes": routes, "video": "youtube" in routes}]
    if "youtube" in routes and len(routes) > 1:
        attempts.append({"routes": [r for r in routes if r != "youtube"], "video": False})
    if routes != ["search"]:
        attempts.append({"routes": ["search"], "video": False})
    # Tail-latency hedge: if the primary call has not produced a token by this point, race an identical call.
    hedge_after = 8.0 + (4.0 if "youtube" in routes else 0.0) + 2.0 * max(0, len(routes) - 1)

    emitted_text = False
    ttft_ms: Optional[int] = None
    used_routes = routes
    used_video = False
    error_note = ""
    maps_by_tag: Dict[int, Dict[str, Dict[str, Any]]] = {}
    web_by_tag: Dict[int, Dict[str, Dict[str, Any]]] = {}
    queue: "asyncio.Queue[tuple]" = asyncio.Queue()
    tasks: Dict[int, "asyncio.Task[None]"] = {}
    att_of: Dict[int, Dict[str, Any]] = {}
    winner: Optional[int] = None
    next_att = 0
    hedged = False
    beats = _heartbeats(routes)
    beat_i = 0
    t_start = time.perf_counter()
    last_beat = t_start

    def _launch(att: Dict[str, Any]) -> None:
        tag = len(att_of) + 1
        att_of[tag] = att
        maps_by_tag[tag], web_by_tag[tag] = {}, {}
        tasks[tag] = asyncio.create_task(_attempt_worker(tag, att, msgs, hub, yt, queue))

    _launch(attempts[0])
    next_att = 1
    try:
        while True:
            if winner is None and queue.empty() and all(t.done() for t in tasks.values()):
                if next_att < len(attempts):
                    _launch(attempts[next_att])
                    next_att += 1
                else:
                    break
            try:
                tag, kind, payload, gm = await asyncio.wait_for(queue.get(), timeout=(30.0 if winner is not None else 1.0))
            except asyncio.TimeoutError:
                if winner is not None:
                    error_note = "stream stalled"
                    yield {"type": "delta", "text": "\n\n_(The grounded stream stalled — ask again to continue.)_"}
                    break
                now = time.perf_counter()
                if now - t_start > 45:
                    error_note = error_note or "no first token within 45 s"
                    break
                if not hedged and now - t_start > hedge_after:
                    hedged = True
                    _launch(att_of[1])
                if now - last_beat >= 6.0:
                    last_beat = now
                    beat_tool, beat_text = beats[beat_i % len(beats)]
                    beat_i += 1
                    yield {"type": "status", "tool": beat_tool, "text": beat_text}
                continue
            if winner is not None and tag != winner:
                continue
            if kind == "chunk":
                if gm is not None:
                    _collect_grounding(gm, maps_by_tag[tag], web_by_tag[tag])
                if payload:
                    if winner is None:
                        winner = tag
                        ttft_ms = int((time.perf_counter() - t0) * 1000)
                        for other_tag, t in tasks.items():
                            if other_tag != tag and not t.done():
                                t.cancel()
                    emitted_text = True
                    yield {"type": "delta", "text": payload}
            elif kind == "end":
                if tag == winner:
                    break
            elif kind == "error":
                error_note = str(payload)
                if tag == winner:
                    yield {"type": "delta", "text": "\n\n_(The grounded stream was interrupted — ask again to continue.)_"}
                    break
    finally:
        for t in tasks.values():
            if not t.done():
                t.cancel()

    maps_out: Dict[str, Dict[str, Any]] = maps_by_tag.get(winner or 0, {})
    web_out: Dict[str, Dict[str, Any]] = web_by_tag.get(winner or 0, {})
    if winner is not None:
        used_routes = att_of[winner]["routes"]
        used_video = att_of[winner]["video"]

    if not emitted_text:
        yield {
            "type": "delta",
            "text": "I couldn't reach the grounding services for that one just now. Please try again in a moment — "
                    "Google Maps, YouTube and Search grounding are all still available for this home.",
        }

    places = list(maps_out.values())[:8]
    if places:
        yield {"type": "status", "tool": "maps", "text": "Pinning verified places on the map…"}
        await _enrich_places(places)
    yield {
        "type": "sources",
        "maps": places,
        "web": list(web_out.values())[:8],
        "youtube": yt if used_video else None,
        "tools": used_routes,
    }
    done: Dict[str, Any] = {
        "type": "done",
        "latency_ms": int((time.perf_counter() - t0) * 1000),
        "ttft_ms": ttft_ms,
        "model": CHAT_MODEL,
        "tools": used_routes,
        "hub": {k: hub[k] for k in ("id", "address", "price", "lat", "lng", "youtube_id", "youtube_url")},
    }
    if error_note and not emitted_text:
        done["error"] = error_note
    yield done
