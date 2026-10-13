# `[2.1]` Fannie Mae / Freddie Mac Selling Guide Citation Assistant

> **Bespoke App:** **NotebookLM Enterprise & StreamAssist // Fannie B3-3.1 & Freddie 5303 Citation Desk** (`notebooklm_gse_citation_desk`)  
> **Runtime & Model:** `Gemini Enterprise streamAssist API (v1alpha) + Vertex AI`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.1](https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.1)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.1)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
2_1-fannie-mae-freddie-mac-selling-guide-citation-as/
├── README.md                      # Overview & quick links
├── docs/
│   └── REPRODUCTION_GUIDE.md      # Architecture diagram, bespoke UI spec & reproduction steps
├── skills/
│   └── SKILL.md                   # Reusable Antigravity / Jetski skill to reproduce this bespoke app
├── code/
│   ├── agent.py                   # Standalone structured Vertex AI runner (gemini-3.8-flash)
│   └── sandbox_tool.py            # Deterministic gVisor sandbox & bespoke visual artifact builder
└── mock_data/
    └── sample_payload.json        # Realistic Rocket Mortgage / Redfin / Mr. Cooper mock dataset
```
