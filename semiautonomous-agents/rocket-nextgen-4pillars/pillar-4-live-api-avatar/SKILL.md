---
name: pillar-4-live-api-avatar
description: Step-by-step LLM replication skill to build and deploy Pillar 4 (Gemini Live API + Voice Avatar + Async Subagent Swarm) from scratch for Rocket Companies & Rocket Money.
---

# SKILL: Replicating Pillar 4 (`Gemini Live API` & Voice Avatar) From Scratch

Any frontier coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) can rebuild Pillar 4 from zero by executing the following 5 engineering steps:

## Step 1: Initialize the Vertex AI Live Client

Use the official `google-genai` SDK (`google-genai >= 2.31.0`) in `us-central1` (required for real-time bidirectional WebSockets):

```python
import os
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
client_live = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
```

## Step 2: Configure Live Audio, VAD, and Built-In Video Avatar

```python
def create_live_config(persona_name="Kira", voice_name="Aoede"):
    return types.LiveConnectConfig(
        response_modalities=[types.LiveModality.AUDIO],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        ),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
                end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                prefix_padding_ms=200,
                silence_duration_ms=600,
            ),
            activity_handling=types.ActivityHandling.START_OF_ACTIVITY_INTERRUPTS,
        ),
        avatar_config=types.AvatarConfig(
            preset_avatar=types.PresetAvatar(name=persona_name)
        ),
        system_instruction=types.Content(
            parts=[types.Part.from_text(
                "You are Kira, Rowan 2.0 at Rocket Money and Redfin. "
                "Keep spoken responses concise (1-3 sentences). Speak naturally, never use emojis or markdown."
            )]
        ),
    )
```

## Step 3: Implement Continuous-fMP4 `ftyp+moov` Caching & FFmpeg Remuxing

To prevent MediaSource decoder crashes when Gemini 3.8 Live streams continuous video fragments:

```python
class GeminiLiveAvatarSession:
    def __init__(self, ws_client):
        self.ws = ws_client
        self.init_segment_bytes = None
        self.remuxer_proc = None

    async def handle_server_media_chunk(self, chunk_bytes):
        # 1. Detect and cache ftyp+moov initialization atoms from chunk 1
        if self.init_segment_bytes is None and b"ftyp" in chunk_bytes:
            moov_idx = chunk_bytes.find(b"moov")
            if moov_idx != -1:
                # Approximate atom boundary; extract init header
                moov_len = int.from_bytes(chunk_bytes[moov_idx:moov_idx+4], "big")
                self.init_segment_bytes = chunk_bytes[:moov_idx + moov_len]
        
        # 2. Pipe media to remuxer and forward to WebSocket client
        if self.remuxer_proc and self.remuxer_proc.stdin:
            self.remuxer_proc.stdin.write(chunk_bytes)
            await self.remuxer_proc.stdin.drain()

    async def handle_interrupt(self):
        """Barge-in occurred: restart remuxer with cached init segment prepended."""
        if self.remuxer_proc:
            self.remuxer_proc.kill()
        self.start_remuxer()
        if self.init_segment_bytes:
            self.remuxer_proc.stdin.write(self.init_segment_bytes)
```

## Step 4: Implement Out-of-Order Concurrent Async Subagent Swarm

```python
import asyncio

async def run_async_swarm(prompt: str):
    """Decomposes prompt and yields first-ready responses concurrently."""
    tasks = [
        ("rates", evaluate_dti_and_rates(prompt)),
        ("schools", pull_school_ratings(prompt)),
        ("subs", scan_rocket_money_subs(prompt)),
    ]
    for coro in asyncio.as_completed([t[1] for t in tasks]):
        result = await coro
        yield result
```

## Step 5: Verification & CLI Testing

```bash
python3 -c "import engine; print(len(engine.AVATAR_PROFILES), 'personas available')"
python3 pillar-4-live-api-avatar/engine.py
```
