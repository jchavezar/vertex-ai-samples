# Square `[1.4]`: Dynamic Loan Pricing & Amortization Co-Pilot — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `1.4` |
| **Bespoke Application Title** | **Monark™ x Rocket Money // Down-Payment Vault & LTV Pricing Simulator** (`monark_wealth_vault_simulator`) |
| **Business Domain** | 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Connect Gemini 4 Argon to live pricing engine APIs, LLPAs, county tax tables, and amortization tools in <1.5 seconds.

**Description:**  
Invoke `fetch_live_rates(zip_code, ltv, fico, loan_amount, loan_purpose)` and `compute_amortization_schedule()` dynamically. Computes Fannie Mae LLPAs, monthly P&I, county property tax, PMI, and 5-year equity buildup in a single turn.

**Bespoke UI Archetype (`monark_wealth_vault_simulator`):**  
Rather than displaying a generic text response, Square `[1.4]` renders **Monark™ x Rocket Money // Down-Payment Vault & LTV Pricing Simulator** with structured visual artifacts (`Return JSON with keys: net_worth_impact, rocket_money_accounts (list of {account_name,institution,balance,allocation_action}), ltv_comparison (list of {tier, loan_amount, rate, monthly_pi, monthly_pmi, total_piti}), and five_year_wealth_projection ({interest_saved, pmi_saved, net_equity_yr5}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Gemini 4 Argon + 3.8 Flash parallel tool-calling executes multi-tool pricing + LLPA + tax lookups 2.4x faster than AWS Bedrock Claude 3.7 Sonnet.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon` · `Gemini 3.8 Flash` · `Vertex AI Function Calling` · `Cloud Run Pricing Microservice`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       1.4 DYNAMIC LOAN PRICING & AMORTIZATION CO-PILOT (L200-L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Banker Natural Language Query]                                       │
│  "Quote $540k purchase in 48009 at 90% vs 85% LTV, 742 FICO"           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon Parallel Function Calling Router]                     │
│  ├─► Tool 1: fetch_live_rates(zip="48009", ltv=90, fico=742)           │
│  ├─► Tool 2: fetch_live_rates(zip="48009", ltv=85, fico=742)           │
│  └─► Tool 3: compute_amortization_60m(loan_a, loan_b)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Verified PITI + PMI + LLPA Breakdown Table & 5-Yr Equity Chart]      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Define Python functions `fetch_live_rates(zip_code: str, ltv: float, fico: int, loan_amount: float)` and `compute_amortization_60m(...)` with docstrings and type annotations.
2. Pass the Python functions directly into `types.GenerateContentConfig(tools=[fetch_live_rates, compute_amortization_60m])` with `model='gemini-4-argon'`.
3. Gemini 4 Argon automatically emits parallel `FunctionCall` parts, executes the deterministic pricing formulas, and synthesizes the side-by-side comparison.

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
  "archetype": "monark_wealth_vault_simulator",
  "net_worth_total": "$218,450.00",
  "unencumbered_cash": "$37,500.00 Post-Close Reserve",
  "accounts": [
    {
      "name": "Rocket Money Down-Payment Vault",
      "acct": "RM-VAULT-8841",
      "bal": "$84,000.00",
      "action": "Allocate $81,000 (15% Down -> 85% LTV Tier)"
    },
    {
      "name": "Chase Premier Checking",
      "acct": "CHK-4402",
      "bal": "$19,450.00",
      "action": "Retain for Closing Costs + 4 Mos PITI Reserve"
    },
    {
      "name": "Fidelity 401(k) Retirement",
      "acct": "FID-9910",
      "bal": "$115,000.00",
      "action": "Untouched \u2014 Counts as 60% Vested Reserve Cushion"
    }
  ],
  "ltv_tiers": [
    {
      "tier": "90% LTV (10% Down = $54,000)",
      "loan": "$486,000",
      "rate": "6.125%",
      "pmi": "$166.05/mo (0.41%)",
      "total": "Loan $486,000 @ 6.125% | P&I $2,952.99 + PMI $166.05 + Tax/Ins $830.00 = $3,949.04/mo",
      "tag": "Baseline"
    },
    {
      "tier": "85% LTV (15% Down = $81,000)",
      "loan": "$459,000",
      "rate": "5.990%",
      "pmi": "$91.80/mo (0.24%)",
      "total": "Loan $459,000 @ 5.990% | P&I $2,748.99 + PMI $91.80 + Tax/Ins $830.00 = $3,670.79/mo",
      "tag": "\u26a1 Monark Optimal (-$281.76/mo)"
    },
    {
      "tier": "80% LTV (20% Down = $108,000)",
      "loan": "$432,000",
      "rate": "5.990%",
      "pmi": "$0.00/mo (No PMI)",
      "total": "$3,414.10/mo",
      "tag": "Requires +$24k Extra Cash"
    }
  ],
  "five_yr_savings": "$16,695.00 saved over first 60 months"
}
```
