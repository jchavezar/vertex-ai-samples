# 5. Risk, Compliance & Legal (CFPB, TRID, Model Armor PII Firewall & Fair Lending) (`rocket-demo-compliance`)

> **Domain Theme:** Rocket Legal, CFPB & Model Armor Governance Vault (Sovereign LegalTech & Compliance UI)  
> **Mission:** Prevent CFPB/TRID/RESPA regulatory violations, enforce zero-leak NPI/PII governance with Model Armor & Sensitive Data Protection, and statistically certify Fair Lending compliance.  
> **AWS / Anthropic / Sierra Win-Back:** Replaces black-box AWS Bedrock Guardrails with Google Cloud Model Armor + Sensitive Data Protection (deterministic + semantic PII redaction), Document AI TRID LE-vs-CD auditing, and Vertex AI Fair Lending statistical evaluation.

## Live Cloud Run Service & Shared Private Login
- **Live Domain Cloud Run App:** [https://rocket-demo-compliance-254356041555.us-central1.run.app](https://rocket-demo-compliance-254356041555.us-central1.run.app)
- **Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)
- **Shared Username:** `rocket`
- **Shared Password:** `Argon2026!`

## Bespoke Use-Case Apps in This Domain

| Code | Level | Bespoke UI Archetype | Active Model Routing | Live Demo URL | Cloud Blueprint | GitHub Subfolder (`docs/`, `code/`, `skills/`, `mock_data/`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`[5.1]`** | `L100–L200` | `cfpb_respa_regulatory_diff_vault` | `gemini-3.8-flash` | [Launch `5.1`](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.1) | [Blueprint `/docs/5.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.1) | [`5_1-cfpb-regulatory-circular-state-law-audit-navigat/`](./5_1-cfpb-regulatory-circular-state-law-audit-navigat/) |
| **`[5.2]`** | `L100–L200` | `model_armor_pii_firewall_inspector` | `gemini-4-argon` | [Launch `5.2`](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.2) | [Blueprint `/docs/5.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.2) | [`5_2-ethical-walls-pii-npi-masking-governance-layer/`](./5_2-ethical-walls-pii-npi-masking-governance-layer/) |
| **`[5.3]`** | `L200–L300` | `trid_le_cd_tolerance_grid` | `gemini-4-argon` | [Launch `5.3`](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.3) | [Blueprint `/docs/5.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.3) | [`5_3-automated-trid-3-day-tolerance-disclosure-checke/`](./5_3-automated-trid-3-day-tolerance-disclosure-checke/) |
| **`[5.4]`** | `L300` | `vendor_glba_contract_redliner` | `gemini-3.8-flash` | [Launch `5.4`](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.4) | [Blueprint `/docs/5.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.4) | [`5_4-automated-vendor-contract-risk-glba-sla-scorer/`](./5_4-automated-vendor-contract-risk-glba-sla-scorer/) |
| **`[5.5]`** | `L300` | `ecoa_fair_lending_twin_certifier` | `gemini-4-argon` | [Launch `5.5`](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.5) | [Blueprint `/docs/5.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.5) | [`5_5-fair-lending-disparate-impact-bias-audit-engine/`](./5_5-fair-lending-disparate-impact-bias-audit-engine/) |
