# Square `[3.5]`: Autonomous Borrower Retention & Life-Event Orchestrator — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `3.5` |
| **Bespoke Application Title** | **Mr. Cooper + Redfin + Rocket // Autonomous Move-Up & Home Equity Bridge Planner** (`life_event_equity_moveup_planner`) |
| **Business Domain** | 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.5](https://rocket-demo-servicing-254356041555.us-central1.run.app/?case=3.5) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.5) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Stateful multi-agent swarm across Redfin listing signals, Mr. Cooper equity ledgers, and Rocket Money to prevent portfolio runoff before a borrower lists their home.

**Description:**  
Coordinate an Ecosystem Listener Agent (detecting when a Mr. Cooper servicing customer favorites homes or requests a Redfin home value estimate), a Financial Benefit Calculator Agent (computing portable equity + bridge/purchase options), and a Communication Dispatch Agent.

**Bespoke UI Archetype (`life_event_equity_moveup_planner`):**  
Rather than displaying a generic text response, Square `[3.5]` renders **Mr. Cooper + Redfin + Rocket // Autonomous Move-Up & Home Equity Bridge Planner** with structured visual artifacts (`Return JSON with keys: current_home_equity_summary ({avm_value, current_loan_balance, current_rate, net_usable_equity}), option_a_keep_and_second_lien ({program, blended_rate, combined_payment}), option_b_sell_and_redfin_buy ({target_redfin_home, down_payment_from_equity, new_loan_amount, new_monthly_pi, rocket_closing_credit}), and recommended_path.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Unifies Rocket's 3 crown-jewel datasets (Mr. Cooper Servicing + Redfin Search + Rocket Money) through Google Cloud Agent Registry & A2A protocol with zero cross-account AWS IAM sprawl.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `GEAP Multi-Agent Orchestrator` · `Google Cloud Agent Registry (A2A)` · `Gemini 4 Argon` · `BigQuery Cross-Brand Event Hub`

```text
┌────────────────────────────────────────────────────────────────────────┐
│    3.5 GEAP MULTI-AGENT RETENTION & LIFE-EVENT ORCHESTRATOR (L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 1: Ecosystem Listener Agent (BigQuery + Pub/Sub)]              │
│  • Correlates Mr. Cooper ($285k equity) + Redfin (Northville search)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 2: Financial Benefit Calculator Agent (Gemini 4 Argon)]        │
│  ├─► Scenario A: Sell w/ Redfin 1% Listing Fee + 34% Down on $750k     │
│  └─► Scenario B: Retain 3.25% Loan as Rental + Rocket Equity Bridge    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 3: Communication Dispatch Agent (Redfin App + Rocket Mobile)]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Register `EcosystemListenerAgent`, `EquityCalculatorAgent`, and `DispatchAgent` in Google Cloud Agent Registry (`apphub` / `agentregistry`).
2. Wire the parent `RetentionOrchestrator` using Google ADK (`LlmAgent` with `sub_agents=[...]`) running on `gemini-4-argon`.
3. Trigger the multi-agent pipeline via Cloud Run when Redfin search telemetry matches an active Mr. Cooper servicing loan.

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
  "archetype": "life_event_equity_moveup_planner",
  "usable_equity": "$184,000.00 Net Equity",
  "option_a": "Keep 3.25% 1st Mtg + $95k Rocket Closed-End 2nd Lien (Blended 4.48% Rate)",
  "option_b": "Sell & Buy $620k Troy 4-Bed on Redfin w/ $155k Down + $4,500 Rocket Loyalty Credit"
}
```
