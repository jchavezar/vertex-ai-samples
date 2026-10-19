# 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`)

> **Domain Theme:** Rocket Pro TPO & Banker Velocity Terminal (Bloomberg FinTech Dark UI)  
> **Mission:** Maximize banker conversion, accelerate speed-to-quote under 1.5s, automate Salesforce/LOS logging, and convert Redfin & Rocket Money leads with Gemini 4 Argon.  
> **AWS / Anthropic / Sierra Win-Back:** Replaces high-latency AWS Bedrock Claude 3.7 prompt chains with Gemini 4 Argon native Function Calling, Context Caching (75% lower TCO), and Gemini Enterprise M365/Outlook connectors.

## Live Cloud Run Service & Shared Private Login
- **Live Domain Cloud Run App:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/origination](https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/origination)
- **Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)
- **Shared Username:** `rocket`
- **Shared Password:** `Argon2026!`

## Bespoke Use-Case Apps in This Domain

| Code | Level | Bespoke UI Archetype | Active Model Routing | Live Demo URL | Cloud Blueprint | GitHub Subfolder (`docs/`, `code/`, `skills/`, `mock_data/`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`[1.1]`** | `L100` | `1003_intake_cockpit` | `gemini-4-argon` | [Launch `1.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.1) | [Blueprint `/docs/1.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.1) | [`1_1-the-abcdq-post-call-structured-debriefer/`](./1_1-the-abcdq-post-call-structured-debriefer/) |
| **`[1.2]`** | `L100–L200` | `outlook_addin_composer` | `gemini-4-argon` | [Launch `1.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.2) | [Blueprint `/docs/1.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.2) | [`1_2-outlook-hyper-personalized-rate-lock-pre-approva/`](./1_2-outlook-hyper-personalized-rate-lock-pre-approva/) |
| **`[1.3]`** | `L100–L200` | `gemini_enterprise_streamassist_hub` | `gemini-3.8-flash` | [Launch `1.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.3) | [Blueprint `/docs/1.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.3) | [`1_3-no-code-mortgage-guideline-competitor-battlecard/`](./1_3-no-code-mortgage-guideline-competitor-battlecard/) |
| **`[1.4]`** | `L200–L300` | `monark_wealth_vault_simulator` | `gemini-4-argon` | [Launch `1.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.4) | [Blueprint `/docs/1.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.4) | [`1_4-dynamic-loan-pricing-amortization-co-pilot/`](./1_4-dynamic-loan-pricing-amortization-co-pilot/) |
| **`[1.5]`** | `L300` | `mcp_webhook_router_board` | `gemini-4-argon` | [Launch `1.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.5) | [Blueprint `/docs/1.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.5) | [`1_5-autonomous-banker-inbound-triage-calendar-bookin/`](./1_5-autonomous-banker-inbound-triage-calendar-bookin/) |
