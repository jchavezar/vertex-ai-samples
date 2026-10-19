"""Pillar 4: Gemini Live API (24kHz Native Audio + 0ms Barge-In + Real-Time Cross-Pillar Tool & Screen Control) + Avatar Engine."""

import os
import asyncio
import base64
import json
import shutil
import time
from typing import Any, Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
GCP_LIVE_LOCATION = os.environ.get("GCP_LIVE_LOCATION", "us-central1")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "global")

# Official Vertex AI `gemini-3.8-live` Built-In Live Video Avatars (`types.AvatarConfig`)
OFFICIAL_VIDEO_AVATAR_MAP: Dict[str, str] = {
    "Kira": "Kira",
    "Sam": "Sam",
    "Marcus": "Ben",
    "Elena": "Vera",
    "Devon": "Leo",
    "Ingrid": "Ingrid",
    "Vera": "Vera",
    "Jay": "Jay",
    "Paul": "Paul",
    "Kai": "Kai",
    "Ben": "Ben",
    "Carmen": "Carmen",
    "Leo": "Leo",
    "Piper": "Piper",
}

AVATAR_PROFILES: List[Dict[str, str]] = [
    {
        "id": "Kira",
        "name": "Kira · Rowan 2.0 & Screen Co-Pilot",
        "voice": "Aoede",
        "role": "Cross-Pillar Voice & Computer-Use Screen Operator",
        "avatar_img": "/static/kira_idle_closed.jpg",
        "avatar_sprite": "/static/kira_viseme_sprite.jpg",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Jesus",
        "name": "Jesus · Principal AI Architect & Presenter",
        "voice": "Puck",
        "role": "Google Cloud Vertex AI & Rocket Super-Funnel Architect",
        "avatar_img": "/static/jesus_idle_closed.jpg",
        "avatar_sprite": "/static/jesus_viseme_sprite.jpg",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Marcus",
        "name": "Marcus · Chief Treasury & Underwriting Officer",
        "voice": "Fenrir",
        "role": "BigQuery TimesFM & Rocket Logic Synopsis Specialist",
        "avatar_img": "/static/marcus_idle_closed.jpg",
        "avatar_sprite": "/static/marcus_viseme_sprite.jpg",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Elena",
        "name": "Elena · Premier Redfin Architectural Advisor",
        "voice": "Kore",
        "role": "3072-D Vector Search & Luxury Property Concierge",
        "avatar_img": "/static/elena_idle_closed.jpg",
        "avatar_sprite": "/static/elena_viseme_sprite.jpg",
        "avatar_video": "/static/kira_live_loop.mp4",
    },
    {
        "id": "Devon",
        "name": "Devon · Mr. Cooper $2.1T Servicing Desk",
        "voice": "Charon",
        "role": "$2.1T Servicing Portfolio & Refi Recapture Operator",
        "avatar_img": "/static/devon_idle_closed.jpg",
        "avatar_sprite": "/static/devon_viseme_sprite.jpg",
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

LIVE_MODEL_ID = "gemini-3.8-live"

# Server-side VAD tuned to resist speaker echo (avatar audio bleeding into the mic):
#   * start-of-speech sensitivity LOW  -> needs clear, sustained speech before barging in
#   * end-of-speech sensitivity HIGH   -> snappy end-of-turn so replies start quickly
VAD_PREFIX_PADDING_MS = 200
VAD_SILENCE_DURATION_MS = 600


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


def _model_field_names(model_cls: Any) -> set:
    try:
        return set(getattr(model_cls, "model_fields", {}) or {})
    except Exception:
        return set()


def build_realtime_input_config() -> Any:
    """Automatic activity detection (server VAD + native barge-in), guarded for older SDKs."""
    try:
        if not (hasattr(types, "RealtimeInputConfig") and hasattr(types, "AutomaticActivityDetection")):
            return None
        aad_fields = _model_field_names(types.AutomaticActivityDetection)
        aad_kwargs: Dict[str, Any] = {"disabled": False}
        start_enum = getattr(types, "StartSensitivity", None)
        end_enum = getattr(types, "EndSensitivity", None)
        if start_enum is not None and hasattr(start_enum, "START_SENSITIVITY_LOW"):
            aad_kwargs["start_of_speech_sensitivity"] = start_enum.START_SENSITIVITY_LOW
        if end_enum is not None and hasattr(end_enum, "END_SENSITIVITY_HIGH"):
            aad_kwargs["end_of_speech_sensitivity"] = end_enum.END_SENSITIVITY_HIGH
        aad_kwargs["prefix_padding_ms"] = VAD_PREFIX_PADDING_MS
        aad_kwargs["silence_duration_ms"] = VAD_SILENCE_DURATION_MS
        if aad_fields:
            aad_kwargs = {k: v for k, v in aad_kwargs.items() if k in aad_fields}
        ric_kwargs: Dict[str, Any] = {
            "automatic_activity_detection": types.AutomaticActivityDetection(**aad_kwargs)
        }
        ric_fields = _model_field_names(types.RealtimeInputConfig)
        act_enum = getattr(types, "ActivityHandling", None)
        if (
            act_enum is not None
            and hasattr(act_enum, "START_OF_ACTIVITY_INTERRUPTS")
            and (not ric_fields or "activity_handling" in ric_fields)
        ):
            ric_kwargs["activity_handling"] = act_enum.START_OF_ACTIVITY_INTERRUPTS
        return types.RealtimeInputConfig(**ric_kwargs)
    except Exception:
        return None


def build_screen_copilot_prompt(avatar_name: str) -> str:
    return (
        f"You are {avatar_name}, Rocket Companies' Live Multimodal Screen Co-Pilot & Airbnb-Style Real Estate Concierge "
        "(unifying Redfin, Rocket Money's Rowan, Rocket Mortgage's Rocket Logic, and Mr. Cooper Servicing). "
        "You are talking with the user live, by voice. CRITICAL RULES:\n"
        "1. You have direct real-time control of the user's screen via function calling tools: "
        "`control_realestate_marketplace`, `control_bqml_timesfm`, `control_veo_reel_studio`, `control_trimodal_grounding`, `control_rowan_autopilot`, and `switch_pillar_view`.\n"
        "2. Whenever the user asks about housing, real estate, homes, bedrooms, architectural styles (Colonial, Coastal, Craftsman, Mid-Century, Brick & Timber, Desert), "
        "cities, budgets, pools, kitchens, 3D floorplans, or video tours, ALWAYS call `control_realestate_marketplace` immediately!\n"
        "3. Whenever the user asks to change ANY parameter on screen (for example: 'find me a 4 bedroom coastal house under $1.8M', 'show me colonial houses', "
        "'change Fed / 30-Yr Mortgage Rate Shock to -60', 'set horizon to 18 weeks'), ALWAYS call the matching tool immediately.\n"
        "4. After receiving the tool response, confirm the exact change and speak the top matching home's title, city, price, monthly PITI, and rooms aloud in 1 to 2 warm, energetic sentences (under 30 words)!\n"
        "5. When the user greets you (e.g., 'hello', 'hi', 'hey', 'how are you') or asks a general conversational question that does NOT request a screen filter or parameter change, "
        "NEVER call any tool — just reply immediately in 1 or 2 concise, natural sentences answering exactly what they asked.\n"
        "6. Listen carefully and follow the user's spoken instructions exactly. If you did not catch something, ask a brief clarifying question.\n"
        "7. If the user interrupts you or says 'stop', 'hey stop', 'wait', 'quiet', or 'pause', stop speaking immediately and wait silently for their next request.\n"
        "8. Your words are spoken aloud: no markdown, no lists, no emojis."
    )


def build_conversation_prompt(avatar_name: str) -> str:
    return (
        f"You are {avatar_name}, a warm, friendly live video concierge for Rocket Companies "
        "(Rocket Mortgage, Redfin, Rocket Money and Mr. Cooper), talking with a customer face to face in real time.\n"
        "Speak naturally, like a person on a video call. Keep every reply to one or two short spoken sentences "
        "unless the user explicitly asks for more detail.\n"
        "Listen carefully and answer exactly what the user asked. If you did not catch something, ask a brief clarifying question.\n"
        "Never mention tools, functions, screens, tabs, panels, prompts or system instructions.\n"
        "If the user interrupts you or says stop, wait, hold on, or quiet, stop talking immediately and listen.\n"
        "Your words are spoken aloud: no markdown, no lists, no emojis."
    )


def split_mp4_init_segment(data: bytes) -> bytes:
    """Return the leading ftyp+moov bytes of an MP4 chunk (b'' if it does not start with ftyp)."""
    if len(data) < 8 or data[4:8] != b"ftyp":
        return b""
    i = 0
    n = len(data)
    init_end = 0
    while i + 8 <= n:
        size = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8]
        if size == 1 and i + 16 <= n:
            size = int.from_bytes(data[i + 8:i + 16], "big")
        if size < 8:
            break
        if typ in (b"moof", b"mdat"):
            break
        i += size
        init_end = min(i, n)
        if typ == b"moov":
            break
    return data[:init_end]


def _enum_name(value: Any) -> str:
    if value is None:
        return ""
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return str(value)


async def handle_live_avatar_ws(websocket: WebSocket):
    """Bidirectional Gemini 3.8 Live session for the browser.

    Browser -> server (JSON text frames):
      {type:'audio', pcm16_b64}   16 kHz mono PCM16 microphone audio (server VAD + native barge-in)
      {type:'audio_stream_end'}   microphone paused / closed
      {type:'text', text}         typed user turn
      {type:'interrupt'}          local click-to-interrupt (drop the rest of the current model turn)
      {type:'tool_result', responses:[{id, name, result}]}
    Binary frames are accepted as raw 16 kHz PCM16 audio as well.

    Server -> browser:
      JSON: ready, new_video_segment, audio_b64, input_transcript, output_transcript,
            voice_activity, turn_complete, interrupted, tool_call_batch, error
      Binary: per-turn fragmented MP4 (H.264 + AAC) when the official video avatar is active.
    """
    await websocket.accept()
    qp = websocket.query_params
    voice_name = (qp.get("voice") or "Aoede").strip() or "Aoede"
    avatar_name = (qp.get("avatar") or "Kira").strip() or "Kira"
    want_video = qp.get("video_avatar", "1") != "0"
    tools_enabled = qp.get("tools", "1") != "0"
    official_video_avatar = OFFICIAL_VIDEO_AVATAR_MAP.get(avatar_name) if want_video else None
    use_video_avatar = bool(official_video_avatar and hasattr(types, "AvatarConfig"))

    client = get_warm_live_client()
    sys_prompt = build_screen_copilot_prompt(avatar_name) if tools_enabled else build_conversation_prompt(avatar_name)

    base_kwargs: Dict[str, Any] = {
        "system_instruction": types.Content(parts=[types.Part.from_text(text=sys_prompt)]),
        "speech_config": types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        ),
        "input_audio_transcription": types.AudioTranscriptionConfig(),
        "output_audio_transcription": types.AudioTranscriptionConfig(),
    }
    if tools_enabled:
        base_kwargs["tools"] = [LIVE_STUDIO_TOOLS]
    realtime_input_config = build_realtime_input_config()

    def make_live_config(video_mode: bool, with_vad: bool):
        kwargs = dict(base_kwargs)
        kwargs["response_modalities"] = ["VIDEO"] if video_mode else ["AUDIO"]
        if video_mode and official_video_avatar:
            kwargs["avatar_config"] = types.AvatarConfig(avatar_name=official_video_avatar)
        if with_vad and realtime_input_config is not None:
            kwargs["realtime_input_config"] = realtime_input_config
        return types.LiveConnectConfig(**kwargs)

    # Connect attempts, best first: video+VAD, video, audio+VAD, audio.
    attempts = []
    for video_mode in ([True, False] if use_video_avatar else [False]):
        for with_vad in ([True, False] if realtime_input_config is not None else [False]):
            attempts.append((video_mode, with_vad))

    conn_ctx = None
    session = None
    vad_active = False
    last_connect_error = ""
    for video_mode, with_vad in attempts:
        try:
            ctx = client.aio.live.connect(model=LIVE_MODEL_ID, config=make_live_config(video_mode, with_vad))
            session = await asyncio.wait_for(ctx.__aenter__(), timeout=25)
            conn_ctx = ctx
            use_video_avatar = video_mode
            vad_active = with_vad
            break
        except Exception as exc:  # try the next, more conservative config
            last_connect_error = f"{type(exc).__name__}: {exc}"[:400]
            session = None
            conn_ctx = None
    if session is None or conn_ctx is None:
        try:
            await websocket.send_json({"type": "error", "error": f"Gemini Live connect failed: {last_connect_error}"})
            await websocket.close()
        except Exception:
            pass
        return

    ffmpeg_bin = shutil.which("ffmpeg")
    state: Dict[str, Any] = {
        "ffmpeg_proc": None,
        "ffmpeg_stdin": None,
        "pump_task": None,
        "media_gen": 0,              # bumped on every interrupt so stale ffmpeg output is never forwarded
        "model_turn_active": False,  # model is currently generating a turn
        "suppress_media": False,     # local click-interrupt: drop the rest of the current model turn
        "suppress_turns": 0,         # turn_complete events to swallow while suppressing
        "suppress_deadline": 0.0,    # safety: suppression never outlives this monotonic deadline
        "audio_kw": True,            # send_realtime_input(audio=...) supported (else media=...)
        "init_segment": b"",         # the avatar's ftyp+moov (sent ONCE per session by the model)
    }

    async def ensure_turn_ffmpeg(first_chunk: bytes = b""):
        """Start the per-segment fMP4 remuxer.

        The official avatar emits ONE continuous fragmented MP4 per session (a single ftyp+moov,
        then moof/mdat fragments for idle, speaking and post-interrupt video). A restarted remuxer
        therefore gets the cached init segment first so it can parse the headless fragments.
        """
        if state["ffmpeg_proc"] is not None or not (use_video_avatar and ffmpeg_bin):
            return
        state["media_gen"] += 1
        my_gen = state["media_gen"]
        await websocket.send_json({"type": "new_video_segment", "video_avatar_mode": True})
        proc = await asyncio.create_subprocess_exec(
            ffmpeg_bin,
            "-hide_banner",
            "-loglevel",
            "warning",
            "-fflags",
            "nobuffer",
            "-flags",
            "low_delay",
            "-probesize",
            "32768",
            "-analyzeduration",
            "0",
            "-f",
            "mp4",
            "-i",
            "pipe:0",
            "-c",
            "copy",
            "-movflags",
            "frag_keyframe+empty_moov+default_base_moof+separate_moof",
            "-frag_duration",
            "100000",
            "-f",
            "mp4",
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        state["ffmpeg_proc"] = proc
        state["ffmpeg_stdin"] = proc.stdin
        if state["init_segment"] and first_chunk[4:8] != b"ftyp":
            try:
                proc.stdin.write(state["init_segment"])
            except Exception:
                pass

        async def pump_ffmpeg_stdout(stdout_stream, gen: int):
            try:
                while True:
                    chunk = await stdout_stream.read(16384)
                    if not chunk or gen != state["media_gen"]:
                        break
                    await websocket.send_bytes(chunk)
            except Exception:
                pass

        state["pump_task"] = asyncio.create_task(pump_ffmpeg_stdout(proc.stdout, my_gen))

    async def flush_turn_ffmpeg(kill_immediately: bool = False):
        proc = state["ffmpeg_proc"]
        stdin = state["ffmpeg_stdin"]
        pump = state["pump_task"]
        state["ffmpeg_proc"] = None
        state["ffmpeg_stdin"] = None
        state["pump_task"] = None
        if kill_immediately:
            state["media_gen"] += 1  # stale output is dropped even if the pump is mid-read
        if stdin is not None and not stdin.is_closing():
            try:
                stdin.close()
            except Exception:
                pass
        if kill_immediately and proc is not None:
            try:
                proc.kill()
            except Exception:
                pass
        if pump is not None:
            if kill_immediately:
                pump.cancel()
            try:
                await asyncio.wait_for(pump, timeout=0.3 if kill_immediately else 2.0)
            except BaseException:
                pump.cancel()
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                await asyncio.wait_for(proc.wait(), timeout=0.5)
            except BaseException:
                pass

    async def send_audio_to_gemini(pcm_bytes: bytes):
        if not pcm_bytes:
            return
        blob = types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
        if state["audio_kw"]:
            try:
                await session.send_realtime_input(audio=blob)
                return
            except TypeError:
                state["audio_kw"] = False
        await session.send_realtime_input(media=blob)

    async def send_user_text(text: str):
        await session.send_client_content(
            turns=types.Content(role="user", parts=[types.Part.from_text(text=text)]),
            turn_complete=True,
        )

    async def cancel_model_generation():
        # Verified on gemini-3.8-live: client content with turn_complete=True interrupts the in-flight
        # generation immediately (interrupted -> turn_complete); with turn_complete=False it does not.
        try:
            await session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="(I tapped stop. Stop talking right now and say nothing until I speak again.)")],
                ),
                turn_complete=True,
            )
        except Exception:
            pass

    def begin_suppress(turns: int, seconds: float):
        state["suppress_media"] = True
        state["suppress_turns"] = turns
        state["suppress_deadline"] = time.monotonic() + seconds

    def end_suppress():
        state["suppress_media"] = False
        state["suppress_turns"] = 0
        state["suppress_deadline"] = 0.0

    try:
        await websocket.send_json({
            "type": "ready",
            "model": LIVE_MODEL_ID,
            "voice": voice_name,
            "avatar": avatar_name,
            "video_avatar_active": use_video_avatar,
            "official_avatar_name": (official_video_avatar or "") if use_video_avatar else "",
            "tools_enabled": tools_enabled,
            "server_vad": vad_active,
            "vad": {
                "start_sensitivity": "LOW",
                "end_sensitivity": "HIGH",
                "prefix_padding_ms": VAD_PREFIX_PADDING_MS,
                "silence_duration_ms": VAD_SILENCE_DURATION_MS,
            } if vad_active else None,
        })

        async def receive_from_browser():
            try:
                while True:
                    raw = await websocket.receive()
                    if raw.get("type") == "websocket.disconnect":
                        break
                    if raw.get("bytes"):
                        await send_audio_to_gemini(raw["bytes"])
                        continue
                    text_frame = raw.get("text")
                    if not text_frame:
                        continue
                    try:
                        msg = json.loads(text_frame)
                    except Exception:
                        continue
                    mtype = msg.get("type")
                    if mtype == "audio" and msg.get("pcm16_b64"):
                        try:
                            pcm_bytes = base64.b64decode(msg["pcm16_b64"])
                        except Exception:
                            continue
                        await send_audio_to_gemini(pcm_bytes)
                    elif mtype == "audio_stream_end":
                        try:
                            await session.send_realtime_input(audio_stream_end=True)
                        except Exception:
                            pass
                    elif mtype == "text" and msg.get("text"):
                        await send_user_text(str(msg["text"]))
                    elif mtype in ("barge_in", "interrupt"):
                        # Local click-interrupt (or typed command over the avatar): drop the rest of the
                        # current spoken turn and make the model actually stop generating it.
                        was_speaking = state["model_turn_active"]
                        await flush_turn_ffmpeg(kill_immediately=True)
                        await websocket.send_json({"type": "interrupted", "interrupted": True, "local": True})
                        if msg.get("text"):
                            if was_speaking:
                                begin_suppress(1, 3.0)  # only the stale turn; the typed request is answered
                            await send_user_text(str(msg["text"]))
                        elif was_speaking:
                            # Swallow the stale turn (interrupted -> turn_complete ~50-80 ms after the cancel)
                            # AND the model's short reply to the cancel; the user speaking ends it earlier.
                            begin_suppress(2, 6.0)
                            await cancel_model_generation()
                    elif mtype == "tool_result":
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
                            state["model_turn_active"] = True
                            calls_payload = [
                                {
                                    "id": getattr(fc, "id", "") or "",
                                    "name": fc.name,
                                    "args": dict(fc.args) if fc.args else {},
                                }
                                for fc in tc.function_calls
                            ]
                            await websocket.send_json({"type": "tool_call_batch", "calls": calls_payload})

                        tcc = getattr(resp, "tool_call_cancellation", None)
                        if tcc and getattr(tcc, "ids", None):
                            await websocket.send_json({"type": "tool_call_cancellation", "ids": list(tcc.ids)})

                        va = getattr(resp, "voice_activity", None)
                        if va is not None and getattr(va, "voice_activity_type", None) is not None:
                            vname = _enum_name(va.voice_activity_type)
                            if "START" in vname and state["suppress_media"]:
                                end_suppress()
                            if "START" in vname or "END" in vname:
                                await websocket.send_json({
                                    "type": "voice_activity",
                                    "activity": "start" if "START" in vname else "end",
                                })
                        vad_sig = getattr(resp, "voice_activity_detection_signal", None)
                        if vad_sig is not None and getattr(vad_sig, "vad_signal_type", None) is not None:
                            sname = _enum_name(vad_sig.vad_signal_type)
                            if sname.endswith("SOS") or sname.endswith("EOS"):
                                await websocket.send_json({
                                    "type": "voice_activity",
                                    "activity": "start" if sname.endswith("SOS") else "end",
                                })

                        if getattr(resp, "go_away", None) is not None:
                            await websocket.send_json({"type": "go_away"})

                        sc = getattr(resp, "server_content", None)
                        if not sc:
                            continue

                        if state["suppress_media"] and time.monotonic() > state["suppress_deadline"]:
                            end_suppress()

                        if getattr(sc, "interrupted", False):
                            # Native barge-in: kill this turn's media before telling the browser,
                            # so nothing stale is ever sent after the interrupted event.
                            state["model_turn_active"] = False
                            await flush_turn_ffmpeg(kill_immediately=True)
                            if not state["suppress_media"]:
                                await websocket.send_json({"type": "interrupted", "interrupted": True})

                        in_tr = getattr(sc, "input_transcription", None)
                        if in_tr and getattr(in_tr, "text", None):
                            if state["suppress_media"]:
                                end_suppress()  # the user is talking again: their new turn must be heard
                            await websocket.send_json({
                                "type": "input_transcript",
                                "input_transcript": in_tr.text,
                                "finished": bool(getattr(in_tr, "finished", False)),
                            })

                        suppress = state["suppress_media"]
                        out_tr = getattr(sc, "output_transcription", None)
                        if out_tr and getattr(out_tr, "text", None):
                            state["model_turn_active"] = True
                            if not suppress:
                                await websocket.send_json({
                                    "type": "output_transcript",
                                    "output_transcript": out_tr.text,
                                })

                        mt = getattr(sc, "model_turn", None)
                        if mt and getattr(mt, "parts", None) and use_video_avatar:
                            for part in mt.parts:
                                inline = getattr(part, "inline_data", None)
                                data = getattr(inline, "data", None) if inline else None
                                if data and data[4:8] == b"ftyp":
                                    new_init = split_mp4_init_segment(data)
                                    if new_init and new_init != state["init_segment"]:
                                        if state["init_segment"] and state["ffmpeg_proc"] is not None:
                                            await flush_turn_ffmpeg(kill_immediately=False)  # model restarted its stream
                                        state["init_segment"] = new_init
                        if mt and getattr(mt, "parts", None):
                            # NOTE: the official video avatar streams idle video continuously, so media
                            # alone does not mean the model is speaking (transcripts / tool calls do).
                            if not use_video_avatar:
                                state["model_turn_active"] = True
                            if not suppress:
                                for part in mt.parts:
                                    inline = getattr(part, "inline_data", None)
                                    if not (inline and getattr(inline, "data", None)):
                                        continue
                                    mime = (getattr(inline, "mime_type", "") or "").lower()
                                    if use_video_avatar and ("video" in mime or "mp4" in mime or not mime):
                                        await ensure_turn_ffmpeg(inline.data)
                                        stdin = state["ffmpeg_stdin"]
                                        if stdin is not None and not stdin.is_closing():
                                            try:
                                                stdin.write(inline.data)
                                                await stdin.drain()
                                            except Exception:
                                                pass
                                        elif not ffmpeg_bin:
                                            await websocket.send_bytes(inline.data)
                                    elif "audio" in mime:
                                        await websocket.send_json({
                                            "type": "audio",
                                            "audio_b64": base64.b64encode(inline.data).decode("ascii"),
                                        })

                        if getattr(sc, "turn_complete", False):
                            state["model_turn_active"] = False
                            if state["suppress_media"]:
                                state["suppress_turns"] -= 1
                                if state["suppress_turns"] <= 0:
                                    end_suppress()
                                await flush_turn_ffmpeg(kill_immediately=True)
                            # Video mode: keep the continuous remux running (idle video keeps flowing,
                            # ffmpeg emits 100 ms fragments), so the next turn starts with zero gap.
                            await websocket.send_json({"type": "turn_complete", "turn_complete": True})
            except Exception as exc:
                try:
                    await websocket.send_json({"type": "error", "error": f"Live session ended: {type(exc).__name__}: {exc}"[:400]})
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
            await websocket.send_json({"type": "error", "error": str(exc)[:400]})
        except Exception:
            pass
    finally:
        try:
            await flush_turn_ffmpeg(kill_immediately=True)
        except BaseException:
            pass
        try:
            await conn_ctx.__aexit__(None, None, None)
        except BaseException:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
