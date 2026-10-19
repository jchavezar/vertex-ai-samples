# Square `[2.3]`: Automated W-2 & Paystub Entity Extraction & Variance Pipeline — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `2.3` |
| **Bespoke Application Title** | **Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector** (`docai_paystub_w2_ocr_inspector`) |
| **Business Domain** | 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** OCR & key-value extraction from scanned paystubs and W-2s, cross-checking stated 1003 income and flagging >5% discrepancies.

**Description:**  
Extract employer name, FEIN, pay frequency, YTD gross earnings, base hourly/salary rate, and overtime lines into normalized key-value pairs with confidence scores and bounding-box coordinates, flagging any variance >5% against the 1003 application.

**Bespoke UI Archetype (`docai_paystub_w2_ocr_inspector`):**  
Rather than displaying a generic text response, Square `[2.3]` renders **Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector** with structured visual artifacts (`Return JSON with keys: dba_entity_resolution ({paystub_name, w2_name, fein, match_confidence}), extracted_fields (list of {field_name, box_ref, extracted_value, ocr_confidence}), variance_analysis ({stated_monthly, documented_monthly, variance_pct, tolerance_limit, status}), and los_remediation_action.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Pre-trained Lending Document AI processors achieve 99.2% field accuracy on noisy mobile phone photos of W-2s/Paystubs without custom AWS Textract template tuning.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Document AI W-2 & Paystub Parsers` · `Gemini 4 Argon Cross-Document Reconciliation` · `Cloud Run`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     2.3 DOCUMENT AI W-2 & PAYSTUB EXTRACTION PIPELINE (L200-L300)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Borrower Uploaded PDF / Mobile Photo: Paystub + 2025 W-2]            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Google Cloud Document AI Lending Processors]                         │
│  ├─► Paystub Parser: Pay Rate, YTD Base, YTD Overtime, Pay Period      │
│  └─► W-2 Parser: FEIN, Box 1, Box 3, Box 5 Wages + Confidence Scores   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon + Variance Verifier]                                  │
│  • Resolves DBA ("Stellantis" == "FCA US LLC")                         │
│  • Flags +8.06% Stated vs Documented Variance (>5% threshold)          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Create a Paystub Processor (`PAY_STUB_PROCESSOR`) and W-2 Processor (`US_W2_PROCESSOR`) in Google Cloud Document AI.
2. Send the Document AI `document.entities` JSON to `gemini-4-argon` alongside the borrower's Form 1003 stated income.
3. Run the automated 5% variance check and output the Encompass/Rocket Logic income adjustment payload.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-4-argon structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "docai_paystub_w2_ocr_inspector",
  "dba_match": "MATCH CONFIRMED \u2014 'Stellantis NV' == 'FCA US LLC' (FEIN 38-2678910)",
  "doc_income": "$9,716.67/mo (Base $9,166.67/mo + 9-Mo YTD Overtime $550.00/mo)",
  "variance": "+8.06% (+$783.33/mo over-stated -> BREACHES 5.0% Tolerance Threshold!)",
  "ocr_boxes": [
    {
      "field": "Employer Legal Entity",
      "box": "W-2 Box c",
      "val": "FCA US LLC (DBA Stellantis NV)",
      "conf": "99.8%"
    },
    {
      "field": "Employer FEIN",
      "box": "W-2 Box b",
      "val": "38-2678910",
      "conf": "99.9%"
    },
    {
      "field": "YTD Base Earnings (9.0 Mos)",
      "box": "Paystub Line 1",
      "val": "$82,500.00 ($9,166.67/mo)",
      "conf": "99.6%"
    },
    {
      "field": "YTD Overtime (9.0 Mos)",
      "box": "Paystub Line 2",
      "val": "$4,950.00 ($550.00/mo)",
      "conf": "99.4%"
    },
    {
      "field": "Form 1003 Stated Income",
      "box": "1003 Section 1b",
      "val": "$10,500.00/mo (+8.06% Overstated)",
      "conf": "\ud83d\udea9 5% BREACH"
    }
  ]
}
```
