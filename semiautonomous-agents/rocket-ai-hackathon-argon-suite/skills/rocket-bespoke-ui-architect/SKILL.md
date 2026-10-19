---
name: rocket-bespoke-ui-architect
description: Master skill to design and reproduce the 33 bespoke use-case applications, real Gemini Multimodal Live API WebSocket audio (gemini-3.8-live), real Gemini Enterprise streamAssist grounding, and automatic ADK model routing (gemini-3.8-flash vs gemini-4-argon) for Rocket Companies.
---

# Rocket Companies AI Hackathon — Bespoke UI/UX & Model Routing Skill

## 1. Never Render Generic Chat/Markdown Walls
Every business use case (`1.1` through `M.5`) must render its own purpose-built interactive application archetype (`shared/bespoke_apps.py` + `shared/bespoke_renderers.py`):
- **Financial / Wealth Vault Use Cases (`1.4`)**: Render a **Monark™ x Rocket Money Personal CFO OS** with connected SimpleFIN/Plaid accounts, Down-Payment Vault allocation sliders, and LTV tier comparison cards.
- **Underwriting & Tax Use Cases (`2.1`–`2.5`)**: Render an **Executive Light-Mode Paper Audit Workbench (`#F8FAFC`)** with zero gridlines, high-contrast red-flag blocker pills, Fannie Mae Form 1084 worksheets, and Document AI OCR bounding-box confidence gates.
- **Real-Time Voice Use Cases (`3.4`, `M.1`, `M.4`)**: Connect a real **Bidirectional WebSocket (`/ws/live-voice/{code}`)** to Vertex AI Live API (`gemini-3.8-live` in `us-central1`) streaming 16kHz microphone PCM in and 24kHz native voice PCM out.
- **Gemini Enterprise Use Cases (`1.3`, `2.1`, `2.5`, `3.1`, `5.1`)**: Call live Discovery Engine `v1alpha` `streamAssist` (`projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023/assistants/default_assistant:streamAssist`) AND surface direct 1-click links to the real Gemini Enterprise Web UI (`https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023`) and Sobi (`/work`).

## 2. Strict Model Routing Policy
- **Google ADK & Vertex AI Agent Engine Runtime (`2.2`, `3.2`, `3.5`, `4.1`, `4.3`, `5.4`, `M.3`, `M.5`)**: Always route to **`gemini-3.8-flash`** (`gemini-4-argon` is not an Agent Engine Runtime endpoint).
- **Gemini Multimodal Live API (`3.4`, `M.1`, `M.4`)**: Route real-time audio WebSockets to **`gemini-3.8-live`** (`us-central1`) and structured cards to **`gemini-3.8-flash`**.
- **Frontier Reasoning, CodeMender & Antigravity IDE (`1.1`, `1.2`, `1.4`, `1.5`, `2.3`, `2.4`, `3.3`, `4.2`, `4.4`, `4.5`, `5.2`, `5.3`, `5.5`, `6.1`–`6.3`, `M.2`)**: Route to **`gemini-4-argon`** on the Vertex AI Global Endpoint (`locations/global/publishers/google/models/gemini-4-argon`) with automatic fallback to `gemini-3.8-flash`.
