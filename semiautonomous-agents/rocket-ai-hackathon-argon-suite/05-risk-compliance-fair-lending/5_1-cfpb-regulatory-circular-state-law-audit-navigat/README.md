# `[5.1]` CFPB Regulatory Circular & State Law Audit Navigator

> **Bespoke App:** **Rocket Legal & NotebookLM // CFPB RESPA Section 8 & State Law Redline Vault** (`cfpb_respa_regulatory_diff_vault`)  
> **Runtime & Model:** `Gemini Enterprise streamAssist API (v1alpha) + Vertex AI`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.1](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.1)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.1)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
5_1-cfpb-regulatory-circular-state-law-audit-navigat/
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
