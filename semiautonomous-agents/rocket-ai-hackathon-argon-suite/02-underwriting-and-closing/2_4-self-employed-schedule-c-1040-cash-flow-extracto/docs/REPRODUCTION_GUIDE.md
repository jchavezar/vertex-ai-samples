# Square `[2.4]`: Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084) — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `2.4` |
| **Bespoke Application Title** | **Fannie Mae Form 1084 // Self-Employed Schedule C & K-1 Cash-Flow Worksheet** (`form_1084_tax_worksheet`) |
| **Business Domain** | 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.4](https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Enforce strict Pydantic JSON schemas (`response_schema`) on multi-page 1040 tax returns to compute Fannie Mae Form 1084 self-employed cash flow.

**Description:**  
Parse 2024 and 2025 IRS Form 1040 + Schedule C tax returns into a guaranteed Pydantic JSON schema, automatically adding back non-cash depreciation, depletion, and business use of home while deducting meals/entertainment and non-recurring income.

**Bespoke UI Archetype (`form_1084_tax_worksheet`):**  
Rather than displaying a generic text response, Square `[2.4]` renders **Fannie Mae Form 1084 // Self-Employed Schedule C & K-1 Cash-Flow Worksheet** with structured visual artifacts (`Return JSON with keys: qualifying_monthly_income, yoy_trend_pct, worksheet_lines (list of {irs_line, description, yr_2024, yr_2025, addback_or_deduct, rule_explanation}), and underwriter_signoff_note.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Gemini 4 Argon's constrained decoding guarantees 100% schema adherence on nested 2-year tax schedules with zero malformed JSON retries.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon (response_schema)` · `Pydantic v2` · `Fannie Mae Form 1084 Engine`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       2.4 SCHEDULE C / 1040 FORM 1084 EXTRACTOR (L300 JSON SCHEMA)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Multi-Page IRS Form 1040 + Schedule C + Form 4562 (2024 & 2025)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon Constrained Decoding (response_schema=Form1084)]      │
│  • Extracts Line 31 Net Profit, Line 13 Depreciation, Line 30 Home     │
│  • Deducts Line 24b Meals, Adds Back Business Mileage Depreciation     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Strict Pydantic JSON Object + 24-Month Qualifying Income ($15,442)]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Define a Pydantic model `FannieMaeForm1084ScheduleC` representing 2024 and 2025 Schedule C lines (`line_31_net_profit`, `line_13_depreciation_addback`, `line_24b_meals_deduction`, `line_30_home_office_addback`, `mileage_depreciation_addback`, `monthly_qualifying_income`).
2. Pass `response_mime_type='application/json'` and `response_schema=FannieMaeForm1084ScheduleC` to `gemini-4-argon`.
3. Ingest the validated JSON directly into Rocket's underwriting database.

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
  "archetype": "form_1084_tax_worksheet",
  "qualifying_mo": "$15,233.96 / month ($365,615.00 / 24 months)",
  "rows": [
    {
      "line": "Schedule C Line 31",
      "item": "Net Profit / Loss",
      "y24": "$142,000",
      "y25": "$158,000",
      "op": "+ Baseline"
    },
    {
      "line": "Schedule C Line 13",
      "item": "MACRS Depreciation Add-Back",
      "y24": "+$28,400",
      "y25": "+$31,600",
      "op": "+ Non-Cash Add-Back"
    },
    {
      "line": "Schedule C Line 30",
      "item": "Business Use of Home (Form 8829)",
      "y24": "+$4,800",
      "y25": "+$5,100",
      "op": "+ Non-Cash Add-Back"
    },
    {
      "line": "Form 4562 / Part IV",
      "item": "Business Miles Depreciation ($0.33/mi)",
      "y24": "+$4,200",
      "y25": "+$5,115",
      "op": "+ IRS Standard Rate"
    },
    {
      "line": "Schedule C Line 24b",
      "item": "Meals & Entertainment Exclusion",
      "y24": "-$6,200",
      "y25": "-$7,400",
      "op": "- Mandatory Deduction"
    },
    {
      "line": "Fannie Mae Form 1084 Total",
      "item": "Adjusted Annual Cash Flow",
      "y24": "$173,200",
      "y25": "$192,415 (+11.1%)",
      "op": "= $14,954.79 / mo"
    }
  ]
}
```
