# `[5.5]` Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)

> **Bespoke App:** **ECOA Regulation B // 500-Counterfactual Twin Fair Lending & Adverse Action Certifier** (`ecoa_fair_lending_twin_certifier`)  
> **Runtime & Model:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.5](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.5)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.5)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
5_5-fair-lending-disparate-impact-bias-audit-engine/
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
