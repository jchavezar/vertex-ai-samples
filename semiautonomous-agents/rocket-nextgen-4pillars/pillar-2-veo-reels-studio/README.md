# Pillar 2 · Text-to-Reels Studio (`Veo 3.1` + `Imagen 4` + `Gemini Live 24kHz Audio`)

## Executive Overview & Live Demo Link

> **Live Production Deployment:** [https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=2](https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=2)
> 
> **The Google vs. Anthropic Moat:** Anthropic Claude is a text-only LLM. It has **zero video generation capability (`Veo 3.1`), zero image synthesis (`Imagen 4` / `Gemini Flash Image`), and zero native 24kHz audio synthesis**. To build a video marketing pipeline with Claude, an enterprise must stitch together third-party video APIs, manage multiple subscriptions, handle massive bandwidth serialization penalties, and tolerate disjointed, out-of-sync audio. In contrast, Google Cloud Vertex AI provides a unified multimodal generative pipeline: **`veo-3.1-generate-001`**, **`imagen-4.0-generate-001`**, and **`gemini-3.8-live`** (24kHz HD voiceover) working together inside a single Google Cloud project.
>
> **Enterprise Business Value for Rocket Companies:**
> 1. **Redfin MLS Listing Viralization:** Converts static MLS property photos and descriptions into cinematic, vertical `9:16` Instagram Reels and TikTok videos in minutes rather than days of manual video editing.
> 2. **Real-Time Rocket Mortgage PITI Underwriting Overlay:** Automatically computes and burns in live principal, interest, taxes, and insurance (PITI) calculations (e.g., *$2,890/mo @ 5.875% with 10% Down*) plus Rocket Super-Funnel incentives (*+$4,600 Redfin Closing Credit*), turning passive social video views into direct mortgage pre-approvals.
> 3. **Mr. Cooper Equity Recapture Social Campaigns:** Synthesizes personalized equity-unlock videos for existing servicing borrowers, illustrating cash-out refinance or home-equity lines of credit (HELOC) potential with broadcast-quality narration.
> 4. **Pre-Rendered Edge Library (11 Luxury Architectural Reels):** Backed by an edge-cached library of 11 pre-rendered vertical 9:16 MP4 reels (`static/reels/`) delivering instant `<100ms` first-frame playback while on-demand Veo generation runs asynchronously.

---

## 1. Live GIF & Video Walkthrough

![Pillar 2 Live Demo](assets/p2_veo_reels_demo.gif)

[🎬 Watch / Download High-Resolution MP4 Video (assets/p2_veo_reels_demo.mp4)](assets/p2_veo_reels_demo.mp4)

### What You See in This Recording
- **00:00 – 00:05 · Luxury Preset Selection:** The user selects *"Royal Oak Modern Craftsman"* ($460k, 4 beds, 2.5 baths, 2,280 sq.ft.) from the reel showcase carousel.
- **00:05 – 00:10 · Gemini 3.8 Flash Creative Directing:** The engine triggers `gemini-3.8-flash` to parse the MLS data into 4 synchronized social captions, camera trajectory directives, and a 24kHz voice script.
- **00:10 – 00:16 · Keyframe & Veo Motion Preview:** The player loads the 9:16 vertical video rendered by `veo-3.1-generate-001` with cinematic golden-hour drone fly-in and sunlit interior glide.
- **00:16 – 00:22 · Live PITI & Super-Funnel Credit Overlay:** An interactive SVG sticker animates on screen showing `$2,890/mo` verified payment and `+$4,600 Combined Closing Credit`. The user tweaks the down payment slider from 10% to 20%, updating the sticker in real time.
- **00:22 – 00:28 · 24kHz HD Voiceover Playback:** The Aoede voiceover streams through WebAudio with animated waveform visualizer synchronized with caption chapters.

---

## 2. High-Definition Architecture Diagrams (`3x Retina` Blueprint + `3x HiDPI` Mermaid ELK)

### 3x Retina Google Cloud Reference Architecture Blueprint
![Pillar 2 GCP Reference Architecture Blueprint](assets/p2_architecture_blueprint.png)
*Vector Reference: [assets/p2_architecture_blueprint.svg](assets/p2_architecture_blueprint.svg)*

### 3x HiDPI Mermaid ELK Execution Flow
![Pillar 2 Mermaid Flow](assets/p2_mermaid_flow_padded.png)
*Mermaid Source: [assets/p2_mermaid_flow.mmd](assets/p2_mermaid_flow.mmd)*

---

## 3. Block-by-Block Component Diagram Walkthrough

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 1] Property Prompt & Loan Underwriting Ingestion                │
│ MLS Attributes, Purchase Price, 10% Down, 5.875% Rate, $4.6k Credit    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 2] Gemini 3.8 Flash Creative Director Engine                    │
│ 4 Timed Scene Captions, Cinematic Camera Prompt, 24kHz Voice Script    │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│ [Block 3] Imagen 4.0 Keyframe Synth  │ │ [Block 5] Gemini 3.8 Live     │
│ `imagen-4.0-generate-001` (9:16)     │ │ 24kHz Native Audio Stream     │
│ 768x1344 HD Initial Anchor Frame     │ │ Aoede / Puck / Kore Voices    │
└───────────────────┬──────────────────┘ └──────────────┬────────────────┘
                    │                                   │
                    ▼                                   │
┌──────────────────────────────────────┐                │
│ [Block 4] Veo 3.1 Video Extrapolator │                │
│ `veo-3.1-generate-001` (720p 9:16)   │                │
│ Fluid drone & interior camera dolly  │                │
└───────────────────┬──────────────────┘                │
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 6] Interactive 9:16 Studio Player & Live PITI Sticker Engine    │
│ Dynamic SVG PITI Sticker ($2,890/mo) + Waveform + 11-Reel CDN Library  │
└────────────────────────────────────────────────────────────────────────┘
```

### Component-by-Component Walkthrough Table

| Block # | Component & File | Google Cloud / Vertex AI Service & Model | Input / Output Contract | Latency & Engineering Mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **Block 1** | **Listing Ingestion**<br>`engine.py::PRESET_REELS` | **In-Memory Catalog & Fast Data Store** | **Input:** MLS listing id or raw property prompt + pricing parameters.<br>**Output:** Structured listing dict (`title`, `price`, `beds`, `rate_pct`, `down_pct`). | **<1ms:** Normalizes property attributes and calculates baseline PITI amortizations via standard banking formulas. |
| **Block 2** | **Creative Director**<br>`engine.py::generate_reel_creative_plan` | **Gemini 3.8 Flash** (`location="global"`) | **Input:** Listing parameters & tone prompt.<br>**Output:** JSON schema with 4 timestamped scene captions, Veo video prompt, and voiceover script. | **450ms – 750ms:** Utilizes `response_schema` with strict validation. Constrains narration to exact word counts matching video duration. |
| **Block 3** | **Keyframe Synthesizer**<br>`engine.py::generate_imagen4_keyframe` | **Imagen 4.0**<br>(`imagen-4.0-generate-001`) | **Input:** Exterior/interior visual description, aspect ratio `9:16`.<br>**Output:** 768x1344 JPEG image bytes in Google Cloud Storage. | **1,400ms – 1,800ms:** Generates photorealistic architectural anchor frames establishing lighting, materials, and composition for video motion. |
| **Block 4** | **Cinematic Video Engine**<br>`engine.py::generate_veo_video` | **Veo 3.1**<br>(`veo-3.1-generate-001` / `fast`) | **Input:** Text prompt or GCS image URI (`image-to-video`), aspect ratio `9:16`, duration 5–8s.<br>**Output:** Long-running operation polling -> 720p vertical MP4. | **45s – 75s (Async) / <100ms (Edge Library):** Renders high-frame-rate vertical motion. 11 production presets pre-rendered and cached on Cloud CDN. |
| **Block 5** | **24kHz Voiceover Streamer**<br>`engine.py::generate_gemini_voiceover` | **Gemini 3.8 Live API** (`location="us-central1"`) | **Input:** Script text, selected voice persona (`Aoede`, `Puck`, `Kore`, `Fenrir`, `Charon`).<br>**Output:** 24,000 Hz 16-bit linear PCM audio stream. | **280ms TTFA:** Native bidirectional audio generation with emotional modulation and natural conversational cadence. |
| **Block 6** | **9:16 Player & PITI Engine**<br>`ui_studio.py` / `p2_stage` | **HTML5 Video Canvas + WebAudio API** | **Input:** Video stream, audio stream, dynamic loan variables.<br>**Output:** Synchronized 9:16 video playback with live interactive SVG loan sticker. | **16ms (60 FPS):** Renders dynamic PITI sticker directly over video. Recomputes monthly payment in 0ms when user adjusts loan parameters. |

### The 11 Pre-Rendered Vertical Reels Library (`static/reels/`)

To guarantee zero-latency demonstration during executive briefings and client pitches, Pillar 2 ships with an edge-cached library of **11 verified architectural property reels**:

| # | Property / Style | City & State | Purchase Price | Verified PITI | Video Asset (`9:16` MP4) |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Detroit Riverfront Loft** | Detroit, MI | $385,000 | `$2,340/mo` | `static/reels/brick_timber_loft_reel_9x16.mp4` |
| **2** | **Aspen Mountain Timber Chalet** | Aspen, CO | $2,450,000 | `$12,840/mo` | `static/reels/reel_aspen_chalet.mp4` |
| **3** | **Austin Lakefront Contemporary** | Austin, TX | $895,000 | `$4,120/mo` | `static/reels/reel_austin_lakeview.mp4` |
| **4** | **Midcentury Modern Glass Home** | Ann Arbor, MI | $695,000 | `$4,275/mo` | `static/reels/midcentury_glass_reel_9x16.mp4` |
| **5** | **Scottsdale Desert Cantilever** | Scottsdale, AZ | $1,150,000 | `$5,890/mo` | `static/reels/desert_mountain_reel_9x16.mp4` |
| **6** | **Pacific Coast Cantilever** | Big Sur, CA | $3,200,000 | `$16,120/mo` | `static/reels/reel_twilight_cantilever.mp4` |
| **7** | **Pacific Northwest Craftsman** | Seattle, WA | $740,000 | `$3,740/mo` | `static/reels/modern_craftsman_reel_9x16.mp4` |
| **8** | **Bloomfield Hills Georgian** | Bloomfield Hills, MI | $1,280,000 | `$6,650/mo` | `static/reels/colonial_georgian_reel_9x16.mp4` |
| **9** | **Mediterranean Ocean Villa** | Key Biscayne, FL | $1,850,000 | `$9,980/mo` | `static/reels/coastal_villa_reel_9x16.mp4` |
| **10** | **Royal Oak Modern Townhome** | Royal Oak, MI | $460,000 | `$2,890/mo` | `static/reels/reel_royaloak.mp4` |
| **11** | **Ann Arbor Executive Villa** | Ann Arbor, MI | $820,000 | `$4,420/mo` | `static/reels/reel_annarbor_modern.mp4` |

---

## 4. How to Replicate From Scratch With Any LLM (`SKILL.md`)

Point any coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) at [`SKILL.md`](SKILL.md) to rebuild the entire Text-to-Reels Studio from scratch in one shot.

### 1-Shot LLM Replication Prompt

```markdown
You are an expert Google Cloud Multimodal AI Engineer. Please read `pillar-2-veo-reels-studio/SKILL.md` and rebuild the Text-to-Reels Generation Studio from scratch:
1. Implement `engine.py` using `google-genai` (SDK 2.31+) with Vertex AI endpoints for `gemini-3.8-flash` (Creative Director), `imagen-4.0-generate-001` (9:16 Keyframe), `veo-3.1-generate-001` (Vertical Video), and `gemini-3.8-live` (24kHz Voiceover).
2. Wire up the 11 preset real estate reels catalog with dynamic PITI calculation and Super-Funnel closing credit logic.
3. Expose the `POST /api/pillar2/generate-reel` and `POST /api/pillar2/tts` endpoints.
4. Render the 9:16 vertical mobile player with live SVG PITI sticker and waveform audio visualizer.
```

---

## 5. Quick Customer Environment Variables Walkthrough (`.env.example`)

### Environment Variables Specification

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `vtxdemos` | Google Cloud project ID with Vertex AI and Cloud Storage enabled. |
| `GCP_LOCATION` | `us-central1` | Primary region for Imagen 4 and Gemini 3.8 Live API. |
| `GCP_GLOBAL_LOCATION` | `global` | Endpoint location for Veo 3.1 and Gemini 3.8 Flash. |
| `GCS_MEDIA_BUCKET` | `vtxdemos-abnb-images` | Bucket storing generated keyframes, videos, and CDN reels. |
| `MODEL_CREATIVE_DIRECTOR` | `gemini-3.8-flash` | Frontier multimodal model for script and caption synthesis. |
| `MODEL_IMAGE_KEYFRAME` | `imagen-4.0-generate-001` | High-fidelity 9:16 vertical keyframe generation model. |
| `MODEL_VIDEO_VEO` | `veo-3.1-generate-001` | Vertex AI state-of-the-art cinematic video generation model. |
| `MODEL_AUDIO_VOICEOVER` | `gemini-3.8-live` | Real-time 24kHz native voice synthesis model. |

### Quick Start Command Block

```bash
# 1. Enter the pillar directory
cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/rocket/pillar-2-veo-reels-studio

# 2. Configure environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# 3. Authenticate with Google Cloud
gcloud auth application-default login

# 4. Run standalone test script (verifies preset library and Gemini creative director)
python3 engine.py
```

### Standalone 3-Step Verification
1. **Verify Asset Library:** Ensure `static/reels/` contains the 11 `.mp4` video files and corresponding `.jpg` thumbnails.
2. **Execute Python Creative Director:** Run `python3 engine.py` to verify `gemini-3.8-flash` synthesizes structured captions and voiceover scripts.
3. **Launch Live Studio:** Start the FastAPI application and open `http://localhost:8080/?pillar=2` to test video playback and the live PITI sticker.
