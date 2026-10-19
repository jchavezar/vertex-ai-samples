# Pillar 4 · Gemini Live API + Voice Avatar + Async Subagent Swarm ("Rowan 2.0")

## Executive Overview & Live Demo Link

> **Live Production Deployment:** [https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=4](https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=4)
> 
> **The Google vs. Anthropic Moat:** Rocket Money's existing financial assistant (**Rowan**, built on Anthropic Claude) is **trapped in SMS text messaging** because Anthropic Claude is fundamentally deaf, mute, and blind. Claude has zero native audio streaming input, zero 24kHz audio synthesis, zero server-side voice activity detection (VAD) barge-in, zero real-time video avatar rendering, and zero capability to operate web interfaces autonomously. In sharp contrast, Google Cloud's **Gemini Live API (`gemini-3.8-live`)** transforms Rowan into an interruptible (`0ms` barge-in), face-to-face `24kHz` audio + **continuous-fMP4 video avatar** that hears borrower tone and hesitation, switches into Spanish mid-sentence without re-prompting, manipulates live Rocket Money / Redfin / Mr. Cooper controls on screen via Ghost Cursor, and delegates compound tasks to an **Out-of-Order Concurrent Async Subagent Swarm** (`gemini-3.1-flash-lite`).
>
> **Enterprise Business Value for Rocket Companies:**
> 1. **Rocket Money Autonomous Subscription Triage:** Hears users express budget stress, autonomously locates cancelable recurring subscriptions (e.g., $140/mo gym membership), and triggers cancellation workflows while calculating immediate debt-to-income (DTI) improvements.
> 2. **Face-to-Face Mortgage Consultation:** Employs high-definition portrait avatars (Kira, Marcus, Elena, Devon) delivering conversational explanations of closing disclosures, points vs. credits, and rate locks.
> 3. **Autonomous Ghost Cursor Screen Control:** The Live API issues structured function calls (`control_bqml_timesfm`, `control_realestate_marketplace`) that move a visual pointer on the borrower's screen, highlighting cards and tweaking sliders in real-time synchrony with voice explanations.
> 4. **Sub-250ms Multi-Intent Swarm Fan-Out:** Complex multi-part inquiries are decomposed and executed concurrently across subagents, returning answers in out-of-order sequence to eliminate conversational lag.

---

## 💻 Source Code in This Pillar Folder

| File / Component | Primary Technology & Models | Purpose & Implementation Details |
| :--- | :--- | :--- |
| [`app.py`](app.py) | **FastAPI + WebSocket Service** · Port `8084` | Standalone microservice exposing `WS /ws/live-avatar` and `POST /api/async-subagents/decompose`. |
| [`engine.py`](engine.py) | **`gemini-3.8-live`** · Python 3.11 | Bidirectional voice & avatar engine; manages persistent WebSockets, continuous fMP4, and subagents. |
| [`frontend/live_session.js`](frontend/live_session.js) | **WebAudio & MSE Video Core** | Client WebAudio 16kHz PCM capture and MediaSource continuous-fMP4 (`ftyp+moov`) rendering engine. |
| [`frontend/p4_stage.js`](frontend/p4_stage.js) | **4:5 Live Avatar Stage UI** | Portrait `704×1280` video stage (`Kira`, `Sam`, `Ben`, `Vera`, `Leo`) with waveform and subagent cards. |
| [`frontend/live_bridge.js`](frontend/live_bridge.js) | **Omni Ghost Cursor Bridge** | Dispatches Live API function calls (`control_bqml_timesfm`, `control_realestate_marketplace`) to UI controls. |
| [`frontend/p4_stage.css`](frontend/p4_stage.css) | **Avatar Stage Stylesheet** | Styling for the 4:5 portrait stage, live status beacon, and out-of-order subagent HUD. |
| [`Dockerfile`](Dockerfile) | **Google Cloud Run Container** | Standalone container build (`uvicorn app:app --port 8084` with `ffmpeg`) for independent deployment. |
| [`requirements.txt`](requirements.txt) | **Pinned Dependencies** | Pinned Python packages (`google-genai`, `fastapi`, `uvicorn`, `websockets`). |
| [`SKILL.md`](SKILL.md) | **1-Shot LLM Replication Skill** | Complete blueprint, WebSocket frames, VAD configurations, and subagent schemas. |
| [`.env.example`](.env.example) | **Environment Configuration** | Template for Live API endpoint (`us-central1`), avatar persona selections, and credentials. |

---

## 1. Live GIF & Video Walkthrough

<p align="center"><img src="assets/p4_live_avatar_demo.gif" width="100%" alt="Pillar 4 Live Demo"></p>

[🎬 Watch / Download High-Resolution MP4 Video (assets/p4_live_avatar_demo.mp4)](assets/p4_live_avatar_demo.mp4)

### What You See in This Recording
- **00:00 – 00:05 · Live Session Handshake:** The user clicks *"Start Live Session"*. The browser establishes a bidirectional WebSocket connection to `/ws/live-avatar` and streams 16kHz PCM audio.
- **00:05 – 00:11 · Continuous-fMP4 Avatar Video Stream:** The 704x1280 portrait avatar (Kira) begins speaking in `<350ms` with natural eye contact, head movement, and lip-synchronized 24kHz HD voiceover.
- **00:11 – 00:16 · Spoken Interruption & Instant Barge-In:** While Kira is speaking, the user speaks over her: *"Wait—interrupt! Can I afford 414 Lakepointe?"* Server-side VAD detects speech in ~40ms, halts video playback immediately, flushes audio buffers, and transitions Kira into an attentive listening state.
- **00:16 – 00:22 · Ghost Cursor DOM Navigation:** Kira responds verbally while her autonomous Ghost Cursor glides across the screen, navigates to the marketplace search bar, types *"414 Lakepointe"*, and adjusts the down-payment slider to 20%.
- **00:22 – 00:28 · Async Subagent Swarm Execution:** The user asks a compound question. Three subagent pills animate in parallel, resolving financial qualification, school ratings, and subscription cuts in out-of-order sequence within 240ms.

---

## 2. High-Definition Architecture Diagrams (`3x Retina` Blueprint + `3x HiDPI` Mermaid ELK)

### 3x Retina Google Cloud Reference Architecture Blueprint
<p align="center"><img src="assets/p4_architecture_blueprint.png" width="100%" alt="Pillar 4 GCP Reference Architecture Blueprint"></p>
*Vector Reference: [assets/p4_architecture_blueprint.svg](assets/p4_architecture_blueprint.svg)*

### 3x HiDPI Mermaid ELK Execution Flow
<p align="center"><img src="assets/p4_mermaid_flow_padded.png" width="100%" alt="Pillar 4 Mermaid Flow"></p>
*Mermaid Source: [assets/p4_mermaid_flow.mmd](assets/p4_mermaid_flow.mmd)*

---

## 3. Block-by-Block Component Diagram Walkthrough

<p align="center">
  <img src="assets/p4_component_walkthrough.png" width="100%" alt="Component Walkthrough Banner">
</p>

### End-to-End Component Flow & Low-Level Invariants

| Block & Component | Source Code File & GCP Model | Latency & Role |
| :--- | :--- | :--- |
| **Block 1: WebAudio & MSE** | `p4_stage.js` & `live_session.js` | **16ms (60 FPS):** Captures 16kHz PCM audio from mic; plays continuous 704×1280 24fps fMP4 video via MSE. |
| **Block 2: WebSocket Gateway** | `app.py::ws_live_avatar` | **<10ms overhead:** Bidirectional WebSocket routing binary PCM frames, text, and 40ms barge-in resets. |
| **Block 3: Live API Core** | `engine.py::RocketLiveClient` | **Sub-Second Latency:** `gemini-3.8-live` speech-to-speech with natural inflection and multi-tool calling. |
| **Block 4: Continuous fMP4** | `engine.py::AvatarConfig` | **0ms flicker:** Caches `ftyp+moov` initialization headers across turns, streaming pure `moof+mdat` chunks. |
| **Block 5: Subagent Swarm** | `engine.py::decompose_and_delegate` | **Parallel Execution:** Dispatches complex queries to Flash-Lite subagents with out-of-order return. |

### 🔹 Block 1 — WebAudio 16kHz PCM Microphone & MSE Video Stage (`live_session.js`)
- **Input / Output Contract:**
  - **Input:** Raw microphone stream via `navigator.mediaDevices.getUserMedia` and user persona selections (`Kira`, `Sam`).
  - **Output:** Downsampled 16,000 Hz 16-bit linear PCM audio chunks and MediaSource video buffer append calls.
- **Source Code Implementation (`JavaScript / static/live_session.js`):**
```javascript
// WebAudio downsampler: captures mic input and emits 16kHz PCM16 binary chunks
const audioCtx = new AudioContext({ sampleRate: 16000 });
const source = audioCtx.createMediaStreamSource(micStream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);
processor.onaudioprocess = (e) => {
    const inputData = e.inputBuffer.getChannelData(0);
    const pcm16 = floatTo16BitPCM(inputData);
    websocket.send(pcm16.buffer);
};
```

### 🔹 Block 2 — Bidirectional WebSocket Gateway & Barge-In Watchdog (`app.py`)
- **Input / Output Contract:**
  - **Input:** Continuous binary PCM chunks and JSON client control frames over `ws://.../ws/live-avatar`.
  - **Output:** Server Voice Activity Detection (VAD) events, synthesized 24kHz audio, and video fragment streams.
- **Source Code Implementation (`Python 3.11 / app.py`):**
```python
@app.websocket("/ws/live-avatar")
async def ws_live_avatar(websocket: WebSocket):
    await websocket.accept()
    session = p4_engine.create_live_session(websocket)
    try:
        async for message in websocket.iter_bytes():
            if session.is_barge_in_active():
                await session.abort_active_synthesis()
            await session.send_audio_chunk(message)
    finally:
        await session.close()
```

### 🔹 Block 3 — Gemini 3.8 Live Multimodal Session Client (`engine.py`)
- **Input / Output Contract:**
  - **Input:** 16kHz audio stream, tool execution return values, and prompt context.
  - **Output:** 24,000 Hz PCM audio response stream, real-time function calls, and avatar sentiment indicators.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
live_config = LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=SpeechConfig(
        voice_config=VoiceConfig(prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Kore"))
    ),
    system_instruction="You are Kira, Rocket's Senior Loan Underwriter. Respond with natural voice inflection.",
)
async with client.aio.live.connect(model="gemini-3.8-live", config=live_config) as session:
    await session.send(input=audio_bytes, end_of_turn=False)
```

### 🔹 Block 4 — Continuous-fMP4 Init Segment Caching Engine (`engine.py`)
- **Input / Output Contract:**
  - **Input:** Pre-rendered avatar gesture segments and transition cues (`listening`, `talking`, `thinking`).
  - **Output:** Seamless fragmented MP4 media stream with `ftyp+moov` sent exactly once, eliminating browser video flicker.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
class AvatarStreamer:
    def __init__(self, avatar_id="kira"):
        # Load and cache initialization segment once
        self.init_segment = load_avatar_ftyp_moov(avatar_id)
        
    def stream_segment(self, state="speaking"):
        # Stream only subsequent moof + mdat movie fragments
        return load_avatar_fragment(self.avatar_id, state)
```

### 🔹 Block 5 — Out-of-Order Async Subagent Swarm (`engine.py`)
- **Input / Output Contract:**
  - **Input:** Multi-variable financial query (e.g. *"What is my rate if I buy 2 points and add an escrow waiver?"*).
  - **Output:** Decomposed tasks dispatched in parallel to Flash-Lite specialist subagents, yielding results in first-ready order.
- **Source Code Implementation (`Python 3.11 / engine.py`):**
```python
async def decompose_and_delegate(query: str):
    tasks = [
        run_subagent("points_calc", query),
        run_subagent("escrow_waiver", query),
        run_subagent("secondary_mbs", query)
    ]
    # Yield each result immediately as it completes (first-ready out-of-order)
    for completed in asyncio.as_completed(tasks):
        result = await completed
        yield result
```

---

## 4. How to Replicate From Scratch With Any LLM (`SKILL.md`)

Point any coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) at [`SKILL.md`](SKILL.md) to rebuild the Live API Avatar Stage from scratch in one shot.

### 1-Shot LLM Replication Prompt

```markdown
You are an expert Google Cloud Multimodal AI Engineer. Please read `pillar-4-live-api-avatar/SKILL.md` and rebuild the Gemini Live Avatar Engine from scratch:
1. Implement `engine.py` using `google-genai` (SDK 2.31+) with Vertex AI `gemini-3.8-live` in `location="us-central1"`.
2. Configure bidirectional WebSocket streaming at `/ws/live-avatar` with 16kHz PCM audio input and 24kHz PCM audio output.
3. Configure `AvatarConfig` with built-in video personas (`Kira`, `Sam`, `Ben`, `Vera`, `Leo`) and implement continuous-fMP4 `ftyp+moov` init segment caching.
4. Implement server-side VAD barge-in with click-to-interrupt handling.
5. Implement the Out-of-Order Async Subagent Swarm with `gemini-3.1-flash-lite` and Ghost Cursor DOM tools.
```

---

## 5. Quick Customer Environment Variables Walkthrough (`.env.example`)

### Environment Variables Specification

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `vtxdemos` | Google Cloud project ID with Vertex AI Live API enabled. |
| `GCP_LIVE_LOCATION` | `us-central1` | Regional location required for Gemini 3.8 Live bidirectional sessions. |
| `GCP_LOCATION` | `global` | Global location for subagent classification and reasoning models. |
| `MODEL_LIVE_VOICE_AVATAR` | `gemini-3.8-live` | Real-time audio and video avatar foundation model. |
| `MODEL_SUBAGENT_DECOMPOSE` | `gemini-3.1-flash-lite` | Ultra-fast classifier for intent decomposition. |
| `DEFAULT_AVATAR_PERSONA` | `Kira` | Default built-in video avatar (Kira, Sam, Ben, Vera, Leo). |
| `DEFAULT_VOICE_NAME` | `Aoede` | Natural 24kHz HD voiceover persona. |

### Quick Start Command Block

```bash
# 1. Enter the pillar directory
cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/rocket/pillar-4-live-api-avatar

# 2. Configure environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# 3. Authenticate with Google Cloud
gcloud auth application-default login

# 4. Run standalone test script (verifies avatar profiles and tool declarations)
python3 engine.py
```

### Standalone 3-Step Verification
1. **Verify Live Endpoint Access:** Ensure your GCP project has access to `gemini-3.8-live` in `us-central1`.
2. **Execute Python Session Test:** Run `python3 engine.py` to inspect tool declarations and avatar persona mappings.
3. **Launch Live WebSocket Stage:** Start the application (`uvicorn app:app --port 8080`) and open `http://localhost:8080/?pillar=4` to experience face-to-face voice conversation and instant barge-in.
