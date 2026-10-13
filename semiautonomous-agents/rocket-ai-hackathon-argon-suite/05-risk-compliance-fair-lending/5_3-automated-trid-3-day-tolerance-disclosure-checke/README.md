# `[5.3]` Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)

> **Bespoke App:** **CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor** (`trid_le_cd_tolerance_grid`)  
> **Runtime & Model:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.3](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.3)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.3)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
5_3-automated-trid-3-day-tolerance-disclosure-checke/
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
