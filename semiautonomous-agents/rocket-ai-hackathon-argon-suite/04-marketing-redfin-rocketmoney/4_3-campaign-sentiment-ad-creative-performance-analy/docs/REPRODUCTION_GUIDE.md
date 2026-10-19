# Square `[4.3]`: Campaign Sentiment & Ad Creative Performance Analyzer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `4.3` |
| **Bespoke Application Title** | **Rocket Growth // Multi-Touch ROAS Attribution & Creative Sentiment Optimizer** (`roas_attribution_funnel_board`) |
| **Business Domain** | 4. Marketing, Growth & Client Acquisition (Redfin, Rocket Money & DTC Funnel) (`rocket-demo-marketing`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Analyze CTR, CPA, ROAS, and funded-loan conversion across Redfin/Rocket campaigns, classify borrower review sentiment, and generate Excel VBA / Sheets formulas.

**Description:**  
Import cross-channel marketing telemetry and thousands of borrower reviews into an interactive spreadsheet grid; let Gemini 4 Argon classify sentiment, compute Cost-Per-Funded-Loan (CPFL), and generate ready-to-run Excel VBA & Google Sheets formulas.

**Bespoke UI Archetype (`roas_attribution_funnel_board`):**  
Rather than displaying a generic text response, Square `[4.3]` renders **Rocket Growth // Multi-Touch ROAS Attribution & Creative Sentiment Optimizer** with structured visual artifacts (`Return JSON with keys: budget_reallocation_headline, channel_performance (list of {channel, creative_theme, cpl, funded_roas, sentiment_driver, budget_action}), and new_ab_test_hypotheses (list of {variant_name, hook_script, target_segment}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Combines natural-language sentiment clustering with deterministic ROAS & Cost-Per-Funded-Loan (CPFL) attribution across Rocket Money, Redfin, and Paid Search.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon` · `Gemini Code Assist` · `BigQuery Connected Sheets / Excel`

```text
┌────────────────────────────────────────────────────────────────────────┐
│    4.3 CAMPAIGN SENTIMENT & AD PERFORMANCE EXCEL ANALYZER (L200-300)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Raw Ad Telemetry (CTR, Spend, Funded Loans) + Borrower Reviews]      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Sandboxed CPFL & ROAS Engine + Gemini 4 Argon Sentiment Classifier]  │
│  ├─► Rocket Money Vault: $277 CPFL | 29.2x ROAS                        │
│  ├─► Redfin Tour Banner: $465 CPFL | 18.1x ROAS                        │
│  └─► Generic Search:     $4,659 CPFL | 1.7x ROAS (Flagged for Cut)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Reallocation Plan (+89 Funded Loans/mo) + Excel VBA / Sheets Code]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Load campaign performance CSVs into Google Sheets / BigQuery or Excel.
2. Use `gemini-4-argon` to classify unstructured review sentiment and generate the VBA / Apps Script automation macro.
3. Verify ROAS and CPFL metrics via the Python sandbox before publishing executive budget shifts.

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
  "archetype": "roas_attribution_funnel_board",
  "winner": "Redfin Embedded Calculator Banner (6.4x Funded Loan ROAS)",
  "reallocation": "Shift $85,000/wk from Generic Brand Video to Redfin Tour + Payment Shock Reels (+28% Funded Volume)",
  "channels": [
    {
      "name": "Redfin Tour-to-PreApproval Native Card",
      "cpl": "$42",
      "funded_roas": "6.4x",
      "sentiment": "+88% High Intent",
      "action": "SCALE +$55k/wk"
    },
    {
      "name": "YouTube Shorts 'Escrow Shock Explainer'",
      "cpl": "$68",
      "funded_roas": "4.9x",
      "sentiment": "+74% Trust Score",
      "action": "SCALE +$30k/wk"
    },
    {
      "name": "Generic 'Lower Rates Soon' Display Ads",
      "cpl": "$195",
      "funded_roas": "1.2x",
      "sentiment": "-32% Ad Fatigue",
      "action": "PAUSE -$85k/wk"
    }
  ]
}
```
