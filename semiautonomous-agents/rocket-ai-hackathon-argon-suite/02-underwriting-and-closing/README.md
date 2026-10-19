# 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`)

> **Domain Theme:** Rocket Logic Underwriting Workbench & Document AI Lightbox (Executive Slate Paper-Audit UI)  
> **Mission:** Ingest and validate unstructured borrower documents (W-2s, Paystubs, 1040 Schedule C, Bank Statements, Title Commitments), compute Fannie Mae Form 1084 income, and clear conditions 10x faster.  
> **AWS / Anthropic / Sierra Win-Back:** Replaces fragile AWS Textract + Bedrock post-processing scripts with Google Cloud Document AI specialized mortgage processors + Gemini 4 Argon 2M-token strict Pydantic JSON schemas and Vertex AI Policy Grounding.

## Live Cloud Run Service & Shared Private Login
- **Live Domain Cloud Run App:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/underwriting](https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/underwriting)
- **Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)
- **Shared Username:** `rocket`
- **Shared Password:** `Argon2026!`

## Bespoke Use-Case Apps in This Domain

| Code | Level | Bespoke UI Archetype | Active Model Routing | Live Demo URL | Cloud Blueprint | GitHub Subfolder (`docs/`, `code/`, `skills/`, `mock_data/`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`[2.1]`** | `L100–L200` | `notebooklm_gse_citation_desk` | `gemini-3.8-flash` | [Launch `2.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.1) | [Blueprint `/docs/2.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.1) | [`2_1-fannie-mae-freddie-mac-selling-guide-citation-as/`](./2_1-fannie-mae-freddie-mac-selling-guide-citation-as/) |
| **`[2.2]`** | `L200` | `adk_hitl_condition_clearing_DAG` | `gemini-3.8-flash` | [Launch `2.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.2) | [Blueprint `/docs/2.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.2) | [`2_2-low-code-underwriting-condition-clearing-large-d/`](./2_2-low-code-underwriting-condition-clearing-large-d/) |
| **`[2.3]`** | `L200–L300` | `docai_paystub_w2_ocr_inspector` | `gemini-4-argon` | [Launch `2.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.3) | [Blueprint `/docs/2.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3) | [`2_3-automated-w-2-paystub-entity-extraction-variance/`](./2_3-automated-w-2-paystub-entity-extraction-variance/) |
| **`[2.4]`** | `L300` | `form_1084_tax_worksheet` | `gemini-4-argon` | [Launch `2.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.4) | [Blueprint `/docs/2.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.4) | [`2_4-self-employed-schedule-c-1040-cash-flow-extracto/`](./2_4-self-employed-schedule-c-1040-cash-flow-extracto/) |
| **`[2.5]`** | `L300` | `amrock_title_curative_map` | `gemini-3.8-flash` | [Launch `2.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.5) | [Blueprint `/docs/2.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.5) | [`2_5-rocket-close-amrock-title-exception-municipal-li/`](./2_5-rocket-close-amrock-title-exception-municipal-li/) |
