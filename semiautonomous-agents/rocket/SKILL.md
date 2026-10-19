---
name: rocket-nextgen-5pillars-studio
description: Master LLM replication skill to build, verify, and deploy the Rocket Companies × Google Gemini Next-Gen 5-Pillar AI Studio (v35) from scratch using any coding agent (Claude Code, Gemini CLI, Cursor, or Antigravity/Jetski).
---

# 🛠️ Master SKILL: Replicating the Rocket Next-Gen 5-Pillar AI Studio (`v35`) From Scratch

Any autonomous coding agent (`Claude Code`, `Gemini CLI`, `Cursor`, `Windsurf`, or `Antigravity / Jetski`) can rebuild the entire **Rocket Next-Gen 5-Pillar AI Studio (`v35`)** or any single pillar from zero by following this Master Skill and the 5 modular Pillar Sub-Skills.

---

## 1. System Architecture & Non-Negotiable 2026 Next-Gen Model Registry

Every pillar in this repository strictly enforces the **2026 Next-Gen Model Registry** on Vertex AI (zero legacy `gemini-2.5-*`, `gemini-2.0-*`, `gemini-1.5-*`, `imagen-3.0-*`, or `veo-2.0-*` models):

| Capability Tier | Vertex AI Model ID | Location | Used In |
| :--- | :--- | :---: | :--- |
| **High-Speed Multimodal Default (Text, Vision, Grounding, Judge)** | `gemini-3.8-flash` | `global` | Pillars 2, 3, 4, 5 |
| **Ultra-Fast Subagent & Routing Tier** | `gemini-3.1-flash-lite` | `global` | Pillar 4 Out-of-Order Subagents |
| **Frontier Deep Reasoning & Econometric Audit** | `gemini-4-argon` | `global` | Pillars 3 & 4 Deep Analysis |
| **Real-Time Bidirectional 24kHz Voice & Live Video Avatars** | `gemini-3.8-live` | `us-central1` | Pillar 4 & Omni Co-Pilot (`/ws/live-avatar`) |
| **Cinematic 9:16 & 16:9 Video + Native 24kHz Audio** | `veo-3.1-generate-001` / `veo-3.1-fast-generate-001` | `global` / `us-central1` | Pillar 2 Reels & Pillar 5 Walkthroughs |
| **Photorealistic Architectural Keyframe Synthesis** | `gemini-3.1-flash-image` / `imagen-4.0-generate-001` | `global` / `us-central1` | Pillar 2 Reels Keyframes |
| **Dense Semantic Text Embeddings (`256-d` / `3072-d`)** | `gemini-embedding-001` | `us-central1` | Pillar 5 Hybrid Vector Search |
| **Cross-Modal Pixel & Text Embeddings (`512-d`)** | `multimodalembedding@001` | `us-central1` | Pillar 5 Pixel-Level Visual Search |
| **Zero-Shot SQL Time-Series Foundation Model** | `AI.FORECAST` (`TimesFM 2.0`) | BigQuery US | Pillar 1 Servicing & Demand Forecast |

---

## 2. Modular Pillar Build Order (Sub-Skills)

Execute each pillar's standalone `SKILL.md` in sequence, verifying its backend `engine.py` before wiring it into `app.py` and `ui_studio.py`:

1. **[Pillar 1 · BigQuery ML `AI.FORECAST` (`TimesFM 2.0`)](pillar-1-bqml-timesfm/SKILL.md)**
   - **Goal:** Forecast 9.5M Mr. Cooper + Rocket servicing refi locks, Redfin buyer tours, escrow outflows, and warehouse line draws in `<900ms` using zero-shot `AI.FORECAST` in BigQuery SQL with a `-150 bps` to `+100 bps` rate-shock covariate scaler.
   - **Verification:** `python3 pillar-1-bqml-timesfm/engine.py`

2. **[Pillar 2 · Text-to-9:16 Reels Studio (`Veo 3.1` + `Imagen 4` + `24kHz Audio`)](pillar-2-veo-reels-studio/SKILL.md)**
   - **Goal:** Convert MLS property prompts into vertical `9:16` social reels with parallel script generation (`gemini-3.8-flash`), architectural keyframes (`gemini-3.1-flash-image` / `imagen-4.0-generate-001`), live `veo-3.1-generate-001` MP4 synthesis, burned-in Rocket Mortgage PITI stickers, and an 11-reel instant edge vault (`static/reels/`).
   - **Verification:** `python3 pillar-2-veo-reels-studio/engine.py`

3. **[Pillar 3 · "Ask Redfin 2.0" Streaming Tri-Modal Grounded Chat (`Maps` + `YouTube` + `Search`)](pillar-3-trimodal-grounding/SKILL.md)**
   - **Goal:** Stream NDJSON (`POST /api/pillar3/chat`) from `gemini-3.8-flash` (`location="global"`, `thinking_level="LOW"`) combining `types.GoogleMaps()`, YouTube `Part.from_uri()`, and `types.GoogleSearch()` in a single call, with a zero-latency keyword router, an 8s tail-latency dual-flight race guard, and Places API (New) coordinate resolution for Leaflet pins (`static/p3_chat.js`).
   - **Verification:** `python3 pillar-3-trimodal-grounding/engine.py`

4. **[Pillar 4 · `gemini-3.8-live` Video Avatar Stage & Out-of-Order Async Subagents](pillar-4-live-api-avatar/SKILL.md)**
   - **Goal:** Stream 16kHz browser mic PCM over `/ws/live-avatar` to `gemini-3.8-live` with server VAD (`START_OF_ACTIVITY_INTERRUPTS`) and 40ms native barge-in. Cache the `ftyp+moov` init segment of the continuous fragmented MP4 stream to drive 704×1280 24fps official Live Video Avatars (`Kira`, `Sam`, `Ben`, `Vera`, `Leo`) in `static/live_session.js` + `static/p4_stage.js`, plus out-of-order concurrent subagents (`asyncio.as_completed` on `gemini-3.1-flash-lite` + `gemini-3.8-flash`).
   - **Verification:** `python3 pillar-4-live-api-avatar/engine.py`

5. **[Pillar 5 · 108-Home Multimodal Vector Marketplace, UMAP Topology, Pre-Rendered Tours & Honest Judge](pillar-5-realestate-marketplace/SKILL.md)**
   - **Goal:** Serve 108 architecturally distinct homes with weighted hybrid search (`0.45` semantic `gemini-embedding-001` + `0.35` visual `multimodalembedding@001` + `0.20` BM25 keyword), interactive 3072-D UMAP 2D topology canvas (`#btn-toggle-behind-scenes`), 108 pre-rendered 720p cinematic MP4 tours (`render_tours.py`), Veo 3.1 walkthroughs (`veo_tours.py`), photo lightbox (`static/p5_media.js`), and an honest 8-photo live multimodal Gemini Judge (`evaluate_listing_live_with_gemini`).
   - **Verification:** `python3 pillar-5-realestate-marketplace/test_hybrid_search.py`

---

## 3. Coordinator Module Pattern (Zero DOM Clobbering)

When extending the frontend UI (`ui_studio.py` + `static/*.js`):
- Keep feature enhancements modular inside self-contained IIFEs in `static/` loaded at the bottom of `<body>` with cache-busting `?v=__ASSET_V__`:
  - `static/live_session.js` (`window.RocketLive` WebSocket + MSE continuous-fMP4 engine)
  - `static/live_bridge.js` (Bridges Omni Co-Pilot & legacy globals to `RocketLive`)
  - `static/p4_stage.js` + `static/p4_stage.css` (Rebuilds `#pillar-4` into the 4:5 portrait conversation stage while parking legacy IDs in `#p4-legacy-shim`)
  - `static/p3_chat.js` + `static/p3_chat.css` (Rebuilds `#pillar-3` into the streaming "Ask Redfin 2.0" grounded chat while preserving `#grounding-map` and `#p3-yt-iframe`)
  - `static/p5_media.js` + `static/p5_media.css` (Adds `#p5m-lightbox` and pre-rendered Veo/Cinematic tour playback to `#pillar-5`)
  - `static/gcp_strip.js` (Dynamic per-tab "Built on Google Cloud" strip that lights up active services on every API/WebSocket call)

---

## 4. One-Shot Prompt to Replicate With Any LLM

Copy and paste this prompt into **Claude Code**, **Gemini CLI**, **Cursor**, or **Antigravity**:

```text
Read SKILL.md, docs/CUSTOMER_ENV_REPLICATION.md, and the 5 pillar-*/SKILL.md files in this repository.
Using my environment variables in .env (GCP_PROJECT_ID, GCP_LOCATION, GCP_LIVE_LOCATION, BQ_DATASET_ID, BQ_TABLE_ID, GCS_MEDIA_BUCKET), provision the BigQuery TimesFM table, verify all 5 pillar engines (pillar-1 through pillar-5), run syntax checks on all Python and JS files, and deploy the unified FastAPI + WebSocket studio to Cloud Run with --timeout 3600.
```
