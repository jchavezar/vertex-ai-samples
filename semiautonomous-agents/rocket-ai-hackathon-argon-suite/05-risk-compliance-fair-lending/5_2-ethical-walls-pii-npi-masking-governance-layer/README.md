# `[5.2]` Ethical Walls & PII/NPI Masking Governance Layer

> **Bespoke App:** **Google Cloud Model Armor + SDP // GLBA Ethical Wall & Live PII/SSN Redaction Firewall** (`model_armor_pii_firewall_inspector`)  
> **Runtime & Model:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`  
> **Shared Login:** Username `rocket` | Password `Argon2026!`

- **🚀 Launch Live Bespoke Demo (Cloud Run):** [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.2](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.2)
- **📘 Hosted Cloud Reproduction Blueprint:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.2)
- **✨ Open Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)

## Folder Structure (GitHub Best Practices)

```text
5_2-ethical-walls-pii-npi-masking-governance-layer/
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
