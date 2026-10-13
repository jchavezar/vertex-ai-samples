# Square `[2.1]`: Fannie Mae / Freddie Mac Selling Guide Citation Assistant — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `2.1` |
| **Bespoke Application Title** | **NotebookLM Enterprise & StreamAssist // Fannie B3-3.1 & Freddie 5303 Citation Desk** (`notebooklm_gse_citation_desk`) |
| **Business Domain** | 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.1](https://rocket-demo-underwriting-254356041555.us-central1.run.app/?case=2.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Ingest Fannie Mae B3-3.1 & Freddie Mac Chapter 5300 manuals to verify complex RSU, seasonal bonus, and overtime income with exact paragraph citations.

**Description:**  
Query Fannie Mae and Freddie Mac guidelines in natural language when underwriting complex variable income (RSUs, variable overtime, 1099 transitions) and receive exact calculation formulas with clickable paragraph-level citations.

**Bespoke UI Archetype (`notebooklm_gse_citation_desk`):**  
Rather than displaying a generic text response, Square `[2.1]` renders **NotebookLM Enterprise & StreamAssist // Fannie B3-3.1 & Freddie 5303 Citation Desk** with structured visual artifacts (`Return JSON with keys: total_qualifying_monthly, underwriting_ruling, income_components (list of {component, calculation, monthly_allowed, gse_citation, status_pill}), and red_flag_alerts (list of strings).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Delivers zero-hallucination inline paragraph citations and Audio Overviews for underwriter training, beating Claude Projects' context window limits on 1,400-page GSE selling guides.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `NotebookLM Enterprise` · `Vertex AI Search & Grounding` · `Gemini 4 Argon`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      2.1 FANNIE MAE / FREDDIE MAC SELLING GUIDE ASSISTANT (L100-200)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Underwriter Complex Income Query: RSUs + Declining YoY Bonus]        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Vertex AI Grounding Datastore / NotebookLM Enterprise Corpus]        │
│  ├─► Fannie Mae Selling Guide (Part B3-3: Income Assessment)           │
│  ├─► Freddie Mac Single-Family Seller/Servicer Guide (Ch. 5300)        │
│  └─► Rocket Logic Internal Underwriting Overlay Bulletins              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Cited Underwriting Memo + Verified Monthly Qualifying Income Math]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Upload the Fannie Mae Selling Guide PDF and Freddie Mac Seller/Servicer Guide into a NotebookLM Enterprise notebook or Vertex AI Search unstructured datastore.
2. Configure `gemini-4-argon` with Vertex AI Grounding (`types.Tool(retrieval=...)`) so every response includes grounded `grounding_chunks` and paragraph citations.
3. Pair with the deterministic GSE income calculator to flag YoY declining variable income (`>10%` drop uses lower most-recent year).

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-3.8-flash structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "notebooklm_gse_citation_desk",
  "total_qualifying": "$19,500.00/month ($234,000.00/yr)",
  "citations": [
    {
      "component": "Base Salary (ServiceNow Inc.)",
      "math": "$165,000 / 12 mos",
      "monthly": "$13,750.00/mo ($165,000 / 12)",
      "ref": "Fannie Mae B3-3.1-01 \u00a7 Base Pay",
      "status": "VERIFIED"
    },
    {
      "component": "Vested RSU Income (NYSE: NOW)",
      "math": "($48,000 + $62,000) / 24 mos",
      "monthly": "$4,583.33/mo (($48,000 + $62,000) / 24 mos \u2014 Publicly Traded NYSE: NOW)",
      "ref": "Fannie Mae B3-3.1-09 \u00a7 Restricted Stock",
      "status": "24-MO AVG"
    },
    {
      "component": "Declining Annual Bonus (-36.4% YoY)",
      "math": "Capped at 2025 ($14,000 / 12) \u2014 Do NOT average 2024!",
      "monthly": "$1,166.67/mo (Capped at 2025 $14,000/12 due to -36.4% YoY decline per B3-3.1-01)",
      "ref": "Fannie Mae B3-3.1-01 \u00a7 Declining Trend Blocker",
      "status": "\u26a0\ufe0f CAPPED"
    }
  ]
}
```
