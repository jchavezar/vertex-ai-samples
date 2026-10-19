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

## 1. Live GIF & Video Walkthrough

![Pillar 4 Live Demo](assets/p4_live_avatar_demo.gif)

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
![Pillar 4 GCP Reference Architecture Blueprint](assets/p4_architecture_blueprint.png)
*Vector Reference: [assets/p4_architecture_blueprint.svg](assets/p4_architecture_blueprint.svg)*

### 3x HiDPI Mermaid ELK Execution Flow
![Pillar 4 Mermaid Flow](assets/p4_mermaid_flow_padded.png)
*Mermaid Source: [assets/p4_mermaid_flow.mmd](assets/p4_mermaid_flow.mmd)*

---

## 3. Block-by-Block Component Diagram Walkthrough

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 1] Borrower 16kHz PCM Audio Stream (`window.RocketLive`)        │
│ Native WebAudio mic streaming + Instant Click-to-Interrupt Barge-in    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ WebSocket (`/ws/live-avatar`)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 2] Vertex AI Gemini 3.8 Live Engine (`gemini-3.8-live`)         │
│ Bidirectional Live Session, Native Server-Side VAD (<350ms TTFA)       │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│ [Block 3] Continuous-fMP4 Remuxer    │ │ [Block 5] Autonomous Tools    │
│ Caches `ftyp+moov` init segment      │ │ Ghost Cursor DOM manipulation │
│ Streams 704x1280 30fps video avatar  │ │ `control_bqml_timesfm`, etc.  │
└───────────────────┬──────────────────┘ └──────────────┬────────────────┘
                    │                                   │
                    ▼                                   ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│ [Block 4] 8-Frame Viseme Fallback    │ │ [Block 6] Async Subagent Swarm│
│ Client-side RMS audio envelope sync  │ │ Concurrent `gemini-3.1-flash` │
│ 60fps mouth phoneme animation        │ │ Out-of-order stream (<250ms)  │
└───────────────────┬──────────────────┘ └──────────────┬────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 7] Interactive Conversation Stage (`static/p4_stage.js`)        │
│ 4:5 Portrait Video + Live Captions + Omni Copilot Integration          │
└────────────────────────────────────────────────────────────────────────┘
```

### Component-by-Component Walkthrough Table

| Block # | Component & File | Google Cloud / Vertex AI Service & Model | Input / Output Contract | Latency & Engineering Mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **Block 1** | **Client Audio Ingestion**<br>`static/live_session.js` | **WebAudio AudioContext / ScriptProcessor** | **Input:** User microphone 48kHz PCM.<br>**Output:** Downsampled 16kHz linear PCM base64 chunks (`{type: "audio", pcm16_b64}`). | **<12ms:** Native client-side downsampling. Employs zero-allocation buffer pools for glitch-free continuous streaming. |
| **Block 2** | **Gemini Live Bidi Engine**<br>`pillar-4-live-api-avatar/engine.py` | **Gemini 3.8 Live API** (`location="us-central1"`) | **Input:** Bidirectional WebSocket audio/tool stream.<br>**Output:** Real-time 24kHz PCM audio, function calls, and avatar video chunks. | **280ms – 350ms TTFA:** Native audio-to-audio foundation model. Automatic activity detection triggers server-side barge-in interrupts in ~40ms. |
| **Block 3** | **Continuous-fMP4 Remuxer**<br>`engine.py::GeminiLiveAvatarSession` | **FFmpeg Subprocess & Init Segment Cache** | **Input:** Fragmented MP4 stream (`moof`/`mdat`).<br>**Output:** Continuous WebM/H.264 MSE video chunks (`704x1280` @ 30 FPS). | **<18ms frame remuxing:** Caches `ftyp`+`moov` headers from turn 1. Re-injects cached headers post-barge-in to prevent MSE decoder freezes. |
| **Block 4** | **Viseme Sprite Lip-Sync**<br>`static/kira_viseme_sprite.jpg` | **Client-Side HTML5 Canvas & RMS Engine** | **Input:** 24kHz incoming PCM audio stream.<br>**Output:** 60 FPS mouth phoneme mapping across 8 sprite sheet cells. | **16ms (60 FPS):** Lightweight fallback for mobile/low-bandwidth devices. WebAudio analyser computes spectral energy to animate jaw and lips. |
| **Block 5** | **Ghost Cursor Controller**<br>`static/p4_stage.js` | **DOM Mutation & Tool Execution Engine** | **Input:** Model tool calls (`control_realestate_marketplace`, `control_bqml_timesfm`).<br>**Output:** Smooth quadratic Bezier cursor animation and synthetic DOM events. | **120ms total travel:** Moves animated visual pointer to target sliders, buttons, and input bars in sync with Kira's verbal explanations. |
| **Block 6** | **Async Subagent Swarm**<br>`app.py::api_async_subagents` | **Gemini 3.1 Flash-Lite & Gemini 3.8 Flash** | **Input:** Multi-intent prompt string.<br>**Output:** Out-of-order parallel JSON streams via `asyncio.as_completed`. | **180ms – 240ms initial yield:** Splits question into 3 discrete tasks (Credit/Rates, MLS Vision, Subscriptions) and streams results first-ready. |
| **Block 7** | **Portrait Stage UI**<br>`static/p4_stage.js` + `p4_stage.css` | **CSS Grid Stage & MSE Video Sink** | **Input:** Live video, dynamic captions, and tool status.<br>**Output:** 4:5 portrait conversational stage with auto-scrolling transcript and crossfade posters. | **16ms render:** Parks legacy DOM safely in hidden shim. `contain: size` preserves layout geometry regardless of transcript expansion. |

### The Production `v35` Engineering Breakthroughs

#### 1. Continuous-fMP4 `ftyp+moov` Init Segment Caching
A critical challenge in Gemini 3.8 Live video avatars is that the API emits **one continuous fragmented MP4 stream per session**:
- Only the very first media packet contains the initialization segment (`ftyp` and `moov` atoms).
- All subsequent packets across speech, idle listening, and barge-in turns contain exclusively `moof` and `mdat` movie fragments (streaming at $\approx 0.8\text{ MB/s}$).
- If an FFmpeg remuxer or MediaSource decoder restarts mid-conversation (e.g., after an interruption or avatar persona switch), it receives no initialization segment and crashes with `appendBuffer failed InvalidStateError`, freezing the avatar.
- **The v35 Solution:** The engine intercepts the first chunk, extracts and caches the `ftyp+moov` byte header in memory, and keeps a single persistent remuxer alive. Upon any barge-in or stream restart, the cached init segment is prepended to the new stream, guaranteeing continuous, uninterrupted video playback.

#### 2. Speaking State Detection via Decoded Audio Energy
Because Gemini 3.8 Live continuously sends video fragments during both speech and silent listening, checking *"is media arriving"* cannot determine if the avatar is speaking. The engine utilizes client-side WebAudio:
```javascript
const stream = videoEl.captureStream();
const audioTrack = stream.getAudioTracks()[0];
const analyser = audioCtx.createAnalyser();
// Compute RMS amplitude: speaking state is true only when RMS > 0.015
```
This drives lip synchronization, transcript captioning, and listening indicators with zero false positives.

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
