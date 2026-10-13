# `[2.3]` Automated W-2 & Paystub Entity Extraction & Variance Pipeline

> **Bespoke App:** **Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector** (`docai_paystub_w2_ocr_inspector`)  
> **Runtime & Model:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.3](https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.3)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
2_3-automated-w-2-paystub-entity-extraction-variance/
├── README.md                      # Overview & quick links
├── docs/
│   └── REPRODUCTION_GUIDE.md      # Architecture diagram, bespoke UI spec & reproduction steps
├── skills/
│   └── SKILL.md                   # Reusable Antigravity / Jetski skill to reproduce this bespoke app
├── code/
│   ├── agent.py                   # Standalone structured Vertex AI runner (gemini-4-argon)
│   └── sandbox_tool.py            # Deterministic gVisor sandbox & bespoke visual artifact builder
└── mock_data/
    └── sample_payload.json        # Realistic Rocket Mortgage / Redfin / Mr. Cooper mock dataset
```
