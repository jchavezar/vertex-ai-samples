# Square `[3.2]`: Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `3.2` |
| **Bespoke Application Title** | **Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator** (`payoff_1098_document_generator`) |
| **Business Domain** | 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`) |
| **Complexity Level** | `L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.2](https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Deterministic state-machine bot with MFA/SSN verification for official payoff quotes (with per-diem interest) and instant Form 1098 delivery.

**Description:**  
Automate the two highest-volume transactional servicing requests across Mr. Cooper & Rocket Servicing with strict state-machine authentication gates, computing exact per-diem interest through a good-through closing date.

**Bespoke UI Archetype (`payoff_1098_document_generator`):**  
Rather than displaying a generic text response, Square `[3.2]` renders **Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator** with structured visual artifacts (`Return JSON with keys: payoff_letter ({loan_number, good_through_date, unpaid_principal, accrued_interest, per_diem_rate, recording_release_fee, total_payoff_due, wire_aba, wire_account}), and irs_form_1098 ({tax_year, box1_mortgage_interest, box5_mip, box6_points, property_address}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Combines rock-solid deterministic state transitions (mandatory for PII/SSN authentication and payoff wire instructions) with generative natural language slot-filling.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Dialogflow CX State Machine` · `Gemini 3.8 Flash` · `Cloud Run Payoff Per-Diem Calculator`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       3.2 DIALOGFLOW CX PAYOFF QUOTE & FORM 1098 BOT (L200)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [State 1: Identity Verification Gate (SSN4 + Property ZIP + OTP)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [State 2: Deterministic Fulfillment Webhook (Cloud Run)]              │
│  ├─► Per-Diem Interest: ($284,500 * 6.00%) / 365 = $46.77/day          │
│  ├─► 42-Day Good-Through Payoff Total: $286,494.34                     │
│  └─► Generates Official Payoff PDF + Dispatches IRS Form 1098          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Define a Dialogflow CX flow with deterministic pages: `Authenticate_Borrower` -> `Collect_Good_Through_Date` -> `Execute_Payoff_Webhook`.
2. Configure route guards requiring session parameters `$session.params.auth_verified = true` before exposing payoff wire numbers.
3. Connect the Cloud Run fulfillment webhook to compute exact per-diem interest.

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
  "archetype": "payoff_1098_document_generator",
  "payoff_total": "$314,289.45",
  "per_diem": "$46.77/day (at 6.000% Note Rate)",
  "form_1098_box1": "$19,420.18",
  "certificate_fields": [
    {
      "label": "Loan Account",
      "val": "Mr. Cooper #0649821140 (Marcus Vance)"
    },
    {
      "label": "Unpaid Principal Balance",
      "val": "$312,450.00"
    },
    {
      "label": "Accrued Interest (Good Thru Nov 15)",
      "val": "$1,784.45 ($52.68/day Per Diem)"
    },
    {
      "label": "County Lien Release Recording",
      "val": "$55.00 (Oakland County Register of Deeds)"
    },
    {
      "label": "Total Certified Payoff Wire Due",
      "val": "$314,289.45 (ABA #021000021)"
    }
  ]
}
```
