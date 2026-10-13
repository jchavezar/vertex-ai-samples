# `[3.2]` Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot

> **Bespoke App:** **Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator** (`payoff_1098_document_generator`)  
> **Runtime & Model:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.2](https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.2)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
3_2-self-service-payoff-quote-irs-form-1098-voice-ch/
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
