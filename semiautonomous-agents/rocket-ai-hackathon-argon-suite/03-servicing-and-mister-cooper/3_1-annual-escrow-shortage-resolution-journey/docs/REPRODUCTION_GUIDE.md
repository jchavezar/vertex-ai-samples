# Square `[3.1]`: Annual Escrow Shortage Resolution Journey — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `3.1` |
| **Bespoke Application Title** | **Mr. Cooper x GECX // Interactive Annual Escrow Shortage Waterfall & Payment Slider** (`escrow_waterfall_interactive`) |
| **Business Domain** | 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Gemini Enterprise streamAssist API (v1alpha) + Vertex AI |
| **Live Interactive Demo** | [https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.1](https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Self-service omnichannel GECX journey that explains county property tax/insurance increases in plain language and executes 1-click payment plan updates.

**Description:**  
Deflect the #1 post-closing servicing call volume driver across Rocket & Mr. Cooper: annual escrow analysis shortages. Visualizes exact county tax + hazard insurance changes and lets borrowers pick Lump-Sum vs. 12-Month Spread or 24-Month Hardship Spread.

**Bespoke UI Archetype (`escrow_waterfall_interactive`):**  
Rather than displaying a generic text response, Square `[3.1]` renders **Mr. Cooper x GECX // Interactive Annual Escrow Shortage Waterfall & Payment Slider** with structured visual artifacts (`Return JSON with keys: empathetic_headline, payment_comparison ({old_total, new_lump_sum_total, new_12mo_spread_total}), waterfall_bars (list of {component, old_mo, new_mo, delta_mo, explanation}), and repayment_options (list of {option_title, upfront_due, monthly_payment, pros}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Beats Sierra AI by combining deterministic RESPA 2-month cushion escrow math with native GCP omnichannel state persistence across mobile app, web, and voice.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Enterprise for CX (GECX)` · `Gemini 4 Argon` · `Mr. Cooper / MSP Servicing Ledger API`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       3.1 GECX ANNUAL ESCROW SHORTAGE RESOLUTION JOURNEY (L100-200)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Borrower Inquiry: "Why did my fixed mortgage jump $285/mo?!"]        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [GECX Conversational Agent + RESPA Escrow Analysis Sandbox]           │
│  ├─► Verifies P&I ($1,840/mo) is 100% locked                           │
│  ├─► Separates Ongoing Tax/Ins Delta (+$140/mo) vs Shortage (+$145/mo) │
│  └─► Computes Lump-Sum ($2,620/mo) vs 12-Mo Spread ($2,765/mo)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [1-Click Self-Service Billing Update + Michigan PRE Tax Check]        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. In Gemini Enterprise for CX (GECX) Agent Studio, create a hybrid Playbook + Deterministic Flow for `Escrow_Shortage_Resolution`.
2. Bind the `calc_escrow_shortage` OpenAPI/Cloud Run tool to fetch the borrower's RESPA annual escrow statement from MSP/Servicing.
3. Render the 3 interactive payment election cards in the Rocket Mobile App / Web widget.

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
  "archetype": "escrow_waterfall_interactive",
  "pi_locked": "$1,840.00/mo @ 5.250% Fixed (UNCHANGED)",
  "escrow_delta": "+$140.00/mo (Troy Property Tax +$90/mo + Hazard Ins +$50/mo -> New Base Escrow $690.00/mo)",
  "option_a": "Pay $1,740.00 One-Time Shortage -> New Monthly Payment = $2,530.00/mo",
  "option_b": "$0 Upfront -> New Monthly Payment = $2,675.00/mo (Includes $145.00/mo for 12 mos)",
  "bars": [
    {
      "label": "Principal & Interest (5.25% Fixed)",
      "old": 1840,
      "new": 1840,
      "color": "#10B981"
    },
    {
      "label": "Troy MI County Property Taxes",
      "old": 410,
      "new": 500,
      "color": "#F59E0B"
    },
    {
      "label": "Homeowners Hazard Insurance",
      "old": 140,
      "new": 190,
      "color": "#38BDF8"
    },
    {
      "label": "12-Month Interest-Free Shortage Spread",
      "old": 0,
      "new": 145,
      "color": "#EC4899"
    }
  ]
}
```
