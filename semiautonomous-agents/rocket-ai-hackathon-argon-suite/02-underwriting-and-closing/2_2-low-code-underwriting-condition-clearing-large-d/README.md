# `[2.2]` Low-Code Underwriting Condition Clearing & Large-Deposit Agent

> **Bespoke App:** **GEAP Visual Agent Studio + ADK // Bank Statement Large-Deposit Clearing Gate** (`adk_hitl_condition_clearing_DAG`)  
> **Runtime & Model:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.2](https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.2)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.2)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
2_2-low-code-underwriting-condition-clearing-large-d/
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
