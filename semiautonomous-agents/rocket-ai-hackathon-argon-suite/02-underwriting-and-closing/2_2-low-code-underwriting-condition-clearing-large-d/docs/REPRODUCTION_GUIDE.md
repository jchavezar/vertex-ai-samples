# Square `[2.2]`: Low-Code Underwriting Condition Clearing & Large-Deposit Agent — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `2.2` |
| **Bespoke Application Title** | **GEAP Visual Agent Studio + ADK // Bank Statement Large-Deposit Clearing Gate** (`adk_hitl_condition_clearing_DAG`) |
| **Business Domain** | 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`) |
| **Complexity Level** | `L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Cross-check borrower bank statements against the 1003 loan application, flag unverified deposits >50% of qualifying income, and stage LOE conditions.

**Description:**  
Visually orchestrate an underwriting agent that scans 60 days of bank statements against Fannie Mae B3-4.2-02 Large Deposit rules (50% of total monthly qualifying income threshold) and stages a one-click Letter of Explanation (LOE) request.

**Bespoke UI Archetype (`adk_hitl_condition_clearing_DAG`):**  
Rather than displaying a generic text response, Square `[2.2]` renders **GEAP Visual Agent Studio + ADK // Bank Statement Large-Deposit Clearing Gate** with structured visual artifacts (`Return JSON with keys: fannie_50pct_threshold, deposits_ledger (list of {date, description, amount, exceeds_threshold, disposition}), asset_backout_math ({ending_balance, unverified_deducted, verified_remaining, required_to_close, pass_fail}), and cel_blocking_gate_payload ({stage, policy_rule, condition_text}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Gives Rocket Operations business analysts a low-code visual canvas with built-in HITL (Human-in-the-Loop) CEL policy gates (`RUNTIME_STAGE_BLOCKING`), which AWS Bedrock Flows lacks.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `GEAP Agent Studio` · `Gemini 4 Argon` · `Cloud Run Condition Engine`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     2.2 GEAP LOW-CODE UNDERWRITING CONDITION CLEARING AGENT (L200)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [60-Day Bank Statement Ledger + 1003 Qualifying Income ($11,400/mo)]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [GEAP Agent Studio Workflow + Fannie Mae B3-4.2-02 Rule Engine]       │
│  ├─► Step 1: Compute 50% Threshold ($5,700.00)                         │
│  ├─► Step 2: Flag Non-Payroll Deposits > $5,700 (Crypto + Check)       │
│  └─► Step 3: Run Asset Back-Out Test & Stage PTDF Condition + LOE      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Processor Condition Queue + Pre-Filled Borrower LOE Request]         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Open Gemini Enterprise Agent Studio (`collections/default_collection/engines/global-gemini-enterprise`) and create a workflow agent.
2. Add the `audit_large_deposits` Python sandbox tool to calculate the exact 50% Fannie Mae B3-4.2-02 threshold and asset back-out math.
3. Configure a HITL `RUNTIME_STAGE_BLOCKING` approval policy before dispatching the LOE request to the borrower's Rocket Mortgage portal.

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
  "archetype": "adk_hitl_condition_clearing_DAG",
  "threshold": "$5,700.00 (50% of $11,400.00 Qualifying Monthly Income)",
  "backout_test": "Ending Balance $51,200.00 - Unverified $25,700.00 = $25,500.00 Verified (< $44,000.00 Required!)",
  "condition_staged": "PTDF Condition #402: Provide 60-day Coinbase liquidation statement & canceled image of Check #1042 + signed LOE.",
  "ledger": [
    {
      "date": "09/04/2026",
      "desc": "FORD MOTOR CO DIRECT DEP PAYROLL",
      "amt": "$4,820.00",
      "status": "EXEMPT \u2014 Direct Payroll"
    },
    {
      "date": "09/14/2026",
      "desc": "COINBASE INC WIRE TRANSFER IN",
      "amt": "$18,500.00",
      "status": "\ud83d\udea9 FLAGGED (> $5,700 Threshold \u2014 Crypto Liquidation Trail Required)"
    },
    {
      "date": "09/22/2026",
      "desc": "MOBILE CHECK DEPOSIT #1042",
      "amt": "$7,200.00",
      "status": "\ud83d\udea9 FLAGGED (> $5,700 Threshold \u2014 Front/Back Check Image + LOE Required)"
    },
    {
      "date": "09/28/2026",
      "desc": "US TREASURY TAX REFUND",
      "amt": "$3,110.00",
      "status": "CLEARED \u2014 Government Tax Refund"
    }
  ]
}
```
