"""Pillar 4: Gemini Live API (24kHz Native Audio + 0ms Barge-In + Real-Time Cross-Pillar Tool & Screen Control) + Avatar Engine."""

import asyncio
import base64
import json
import subprocess
from typing import Any, Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

PROJECT_ID = "vtxdemos"

AVATAR_PROFILES: List[Dict[str, str]] = [
    {
        "id": "Kira",
        "name": "Kira · Rowan 2.0 & Screen Co-Pilot",
        "voice": "Aoede",
        "role": "Cross-Pillar Voice & Computer-Use Screen Operator",
        "avatar_img": "/static/kira_avatar.png",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Ingrid",
        "name": "Ingrid · Chief Economist & Underwriter",
        "voice": "Kore",
        "role": "BigQuery TimesFM & Rocket Logic Synopsis Specialist",
        "avatar_img": "/static/kira_avatar.png",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Jay",
        "name": "Jay · Mr. Cooper Retention Desk",
        "voice": "Puck",
        "role": "$2.1T Servicing Portfolio & Refi Recapture Operator",
        "avatar_img": "/static/kira_avatar.png",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Carmen",
        "name": "Carmen · Bilingual Super-Funnel Advisor",
        "voice": "Aoede",
        "role": "English/Spanish Redfin + Rocket Mortgage Concierge",
        "avatar_img": "/static/kira_avatar.png",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
]

LIVE_STUDIO_TOOLS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="control_bqml_timesfm",
            description=(
                "Modify Pillar 1 (BigQuery ML TimesFM) parameters on the user's screen in real time: "
                "change Fed / 30-Yr Mortgage Rate Shock (any integer bps from -150 to +100, e.g. -60, -125, -50), "
                "change Forecast Horizon (any integer weeks from 4 to 24), change Confidence Interval (80 to 99), "
                "or switch the Rocket cohort, and execute live BigQuery AI.FORECAST."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "metric_id": types.Schema(
                        type="STRING",
                        enum=[
                            "mrcooper_refi_locks",
                            "redfin_tour_demand",
                            "escrow_liquidity_outflow_m",
                            "warehouse_funding_b",
                        ],
                        description="Target Rocket cohort metric in BigQuery.",
                    ),
                    "rate_shock_bps": types.Schema(
                        type="INTEGER",
                        description="Exact Fed / 30-Yr mortgage rate shock in basis points between -150 and 100 (e.g., -60, -125, -75, -50, 0, 25).",
                    ),
                    "horizon": types.Schema(
                        type="INTEGER",
                        description="Forecast horizon in weeks between 4 and 24 (e.g., 8, 12, 16, 18, 24).",
                    ),
                    "confidence_level": types.Schema(
                        type="INTEGER",
                        description="Prediction interval confidence percentage between 80 and 99 (e.g., 85, 90, 95).",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="control_veo_reel_studio",
            description=(
                "Navigate to Pillar 2 (Veo 3.1 Reels Studio) and change the property listing preset, listing price slider, "
                "down payment percentage slider, or 30-year mortgage rate slider on screen in real time."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "preset_id": types.Schema(
                        type="STRING",
                        enum=["royal_oak", "corktown_loft", "ann_arbor"],
                        description="Redfin listing preset to load into the 9:16 Veo 3.1 phone player.",
                    ),
                    "price": types.Schema(
                        type="INTEGER",
                        description="Home listing price in USD between 250000 and 950000 (e.g., 460000, 550000, 650000).",
                    ),
                    "down_pct": types.Schema(
                        type="INTEGER",
                        description="Down payment percentage between 3 and 30 (e.g., 5, 10, 15, 20).",
                    ),
                    "rate_pct": types.Schema(
                        type="NUMBER",
                        description="30-year fixed mortgage interest rate between 5.0 and 7.25 (e.g., 5.5, 5.875, 6.25).",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="control_trimodal_grounding",
            description=(
                "Navigate to Pillar 3 (Tri-Modal Grounding with Google Maps, YouTube, and Google Search) and inspect a property hub "
                "or switch the Google Maps layer between roadmap and satellite."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "hub_id": types.Schema(
                        type="STRING",
                        enum=["royal_oak", "corktown_detroit", "ann_arbor"],
                        description="Property hub to ground across Google Maps, YouTube Video URI, and Google Search.",
                    ),
                    "map_layer": types.Schema(
                        type="STRING",
                        enum=["roadmap", "satellite"],
                        description="Google Maps tile layer mode (roadmap or satellite hybrid).",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="control_rowan_autopilot",
            description=(
                "Control Pillar 4 Rowan 2.0 Subscription-to-Principal Autopilot checkboxes or apply the Mr. Cooper refi rate drop."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "cancel_all_subs": types.Schema(
                        type="BOOLEAN",
                        description="True to check all 4 unused subscriptions (+$285/mo toward mortgage principal).",
                    ),
                    "highlight_card": types.Schema(
                        type="STRING",
                        enum=["subs", "purchase", "refi"],
                        description="Which Super-Funnel card to highlight on screen.",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="control_realestate_marketplace",
            description=(
                "Search, filter, map, and inspect homes in Pillar 5 (Airbnb × Redfin AI Real Estate Hybrid Vector Marketplace) "
                "in real time when the user asks for housing, homes, bedrooms, architectural styles (Colonial, Coastal, Craftsman, "
                "Mid-Century Glass, Brick & Timber Loft, Desert/Mountain), cities, prices, pools, kitchens, 3D floorplans, or Veo reels."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query_text": types.Schema(
                        type="STRING",
                        description="Natural language housing search query (e.g. '4 bedroom coastal waterfront villa with pool', 'stone colonial farmhouse', 'Malibu oceanfront glass villa').",
                    ),
                    "beds_filter": types.Schema(
                        type="INTEGER",
                        description="Number of bedrooms to filter (0 for all, or 2, 3, 4, 5, 6).",
                    ),
                    "family_filter": types.Schema(
                        type="STRING",
                        enum=[
                            "all",
                            "modern_craftsman",
                            "midcentury_glass",
                            "brick_timber_loft",
                            "colonial_georgian",
                            "coastal_villa",
                            "desert_mountain",
                        ],
                        description="Architectural style category to filter.",
                    ),
                    "max_price": types.Schema(
                        type="INTEGER",
                        description="Maximum home price in USD between 450000 and 2500000 (e.g., 800000, 1200000, 1800000, 2500000).",
                    ),
                    "open_top_match": types.Schema(
                        type="BOOLEAN",
                        description="True if the user asks to open, tour, inspect, or see the floorplan/reel of the best matching house.",
                    ),
                    "modal_tab": types.Schema(
                        type="STRING",
                        enum=["rooms", "floorplan", "walkthrough", "reel", "judge"],
                        description="Which tab to open in the Airbnb property detail modal if open_top_match is True.",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="switch_pillar_view",
            description="Switch the active screen tab to Pillar 1, 2, 3, 4, or 5.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "pillar_number": types.Schema(
                        type="INTEGER",
                        description="1=BQML TimesFM, 2=Veo 3.1 Reels, 3=Maps+YouTube+Search Grounding, 4=Live API Avatar, 5=Airbnb AI Real Estate Marketplace.",
                    ),
                },
                required=["pillar_number"],
            ),
        ),
    ]
)

_warm_client = None


def get_warm_live_client():
    global _warm_client
    if _warm_client is None:
        _warm_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="us-central1",
            http_options=types.HttpOptions(api_version="v1beta1"),
        )
    return _warm_client


async def handle_live_avatar_ws(websocket: WebSocket):
    """Bidirectional WebSocket streaming 24kHz PCM native audio + real-time Cross-Pillar Function Calling."""
    await websocket.accept()
    voice_name = websocket.query_params.get("voice", "Aoede")
    avatar_name = websocket.query_params.get("avatar", "Kira")

    client = get_warm_live_client()
    sys_prompt = (
        f"You are {avatar_name}, Rocket Companies' Live Multimodal Screen Co-Pilot & Airbnb-Style Real Estate Concierge "
        "(unifying Redfin, Rocket Money's Rowan, Rocket Mortgage's Rocket Logic, and Mr. Cooper Servicing). "
        "CRITICAL RULES:\n"
        "1. You have direct real-time control of the user's screen via function calling tools: "
        "`control_realestate_marketplace`, `control_bqml_timesfm`, `control_veo_reel_studio`, `control_trimodal_grounding`, `control_rowan_autopilot`, and `switch_pillar_view`.\n"
        "2. Whenever the user asks about housing, real estate, homes, bedrooms, architectural styles (Colonial, Coastal, Craftsman, Mid-Century, Brick & Timber, Desert), "
        "cities, budgets, pools, kitchens, 3D floorplans, or video tours, ALWAYS call `control_realestate_marketplace` immediately!\n"
        "3. Whenever the user asks to change ANY parameter on screen (for example: 'find me a 4 bedroom coastal house under $1.8M', 'show me colonial houses', "
        "'change Fed / 30-Yr Mortgage Rate Shock to -60', 'set horizon to 18 weeks'), ALWAYS call the matching tool immediately.\n"
        "4. After receiving the tool response, confirm the exact change and speak the top matching home's title, city, price, monthly PITI, and rooms aloud in 1 to 2 warm, energetic sentences (under 38 words)!"
    )

    config_kwargs: Dict[str, Any] = {
        "response_modalities": ["AUDIO"],
        "system_instruction": types.Content(parts=[types.Part.from_text(text=sys_prompt)]),
        "speech_config": types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        ),
        "tools": [LIVE_STUDIO_TOOLS],
        "input_audio_transcription": types.AudioTranscriptionConfig(),
        "output_audio_transcription": types.AudioTranscriptionConfig(),
    }

    live_config = types.LiveConnectConfig(**config_kwargs)

    try:
        async with client.aio.live.connect(model="gemini-3.8-live", config=live_config) as session:
            await websocket.send_json({
                "type": "ready",
                "model": "gemini-3.8-live",
                "voice": voice_name,
                "avatar": avatar_name,
            })

            async def receive_from_browser():
                try:
                    while True:
                        raw = await websocket.receive_text()
                        msg = json.loads(raw)
                        mtype = msg.get("type")
                        if mtype == "audio" and msg.get("pcm16_b64"):
                            pcm_bytes = base64.b64decode(msg["pcm16_b64"])
                            await session.send_realtime_input(
                                media=types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
                            )
                        elif mtype == "text" and msg.get("text"):
                            await session.send_client_content(
                                turns=types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text=msg["text"])],
                                ),
                                turn_complete=True,
                            )
                        elif mtype == "barge_in":
                            # Client triggered immediate 0ms barge-in interruption
                            await websocket.send_json({"type": "interrupted", "interrupted": True})
                        elif mtype == "tool_result":
                            # Support both single tool result and batched tool results
                            if msg.get("responses"):
                                fn_resps = [
                                    types.FunctionResponse(
                                        id=r.get("id"),
                                        name=r.get("name"),
                                        response=r.get("result") or {"status": "updated_on_screen"},
                                    )
                                    for r in msg["responses"]
                                ]
                            else:
                                fn_resps = [
                                    types.FunctionResponse(
                                        id=msg.get("id"),
                                        name=msg.get("name"),
                                        response=msg.get("result") or {"status": "updated_on_screen"},
                                    )
                                ]
                            await session.send_tool_response(function_responses=fn_resps)
                except WebSocketDisconnect:
                    pass
                except Exception:
                    pass

            async def send_to_browser():
                try:
                    while True:
                        async for resp in session.receive():
                            tc = getattr(resp, "tool_call", None)
                            if tc and getattr(tc, "function_calls", None):
                                calls_payload = [
                                    {
                                        "id": getattr(fc, "id", ""),
                                        "name": fc.name,
                                        "args": dict(fc.args) if fc.args else {},
                                    }
                                    for fc in tc.function_calls
                                ]
                                await websocket.send_json({
                                    "type": "tool_call_batch",
                                    "calls": calls_payload,
                                })

                            sc = getattr(resp, "server_content", None)
                            if not sc:
                                continue
                            if getattr(sc, "interrupted", False):
                                await websocket.send_json({"interrupted": True})
                            in_tr = getattr(sc, "input_transcription", None)
                            if in_tr and getattr(in_tr, "text", None):
                                await websocket.send_json({"input_transcript": in_tr.text})
                            out_tr = getattr(sc, "output_transcription", None)
                            if out_tr and getattr(out_tr, "text", None):
                                await websocket.send_json({"output_transcript": out_tr.text})
                            mt = getattr(sc, "model_turn", None)
                            if mt and getattr(mt, "parts", None):
                                for part in mt.parts:
                                    inline = getattr(part, "inline_data", None)
                                    if inline and getattr(inline, "data", None):
                                        mime = (getattr(inline, "mime_type", "") or "").lower()
                                        if "audio" in mime:
                                            await websocket.send_json({
                                                "audio_b64": base64.b64encode(inline.data).decode("ascii")
                                            })
                            if getattr(sc, "turn_complete", False):
                                await websocket.send_json({"turn_complete": True})
                except Exception:
                    pass

            tasks = [
                asyncio.create_task(receive_from_browser()),
                asyncio.create_task(send_to_browser()),
            ]
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in tasks:
                t.cancel()
    except Exception as exc:
        try:
            await websocket.send_json({"error": str(exc)})
            await websocket.close()
        except Exception:
            pass
