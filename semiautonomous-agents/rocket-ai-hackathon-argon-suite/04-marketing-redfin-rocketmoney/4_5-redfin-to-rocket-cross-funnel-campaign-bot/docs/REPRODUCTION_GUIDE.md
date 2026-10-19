# Square `[4.5]`: Redfin-to-Rocket Cross-Funnel Campaign Bot — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `4.5` |
| **Bespoke Application Title** | **Antigravity Cross-Brand Flywheel // Rocket Money Vault -> Redfin Tour -> Mortgage Close** (`redfin_rocketmoney_flywheel_journey`) |
| **Business Domain** | 4. Marketing, Growth & Client Acquisition (Redfin, Rocket Money & DTC Funnel) (`rocket-demo-marketing`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.5) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.5) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Autonomous Antigravity marketing sub-agents connected via MCP to Redfin tour telemetry and Rocket Money savings vaults.

**Description:**  
The ultimate demonstration of Rocket's ecosystem flywheel: when a user books a Redfin home tour, Antigravity subagents query their linked Rocket Money Down Payment Vault via MCP, calculate exact personalized affordability (including the Redfin + Rocket bundle credit), and dispatch a tailored pre-tour approval package.

**Bespoke UI Archetype (`redfin_rocketmoney_flywheel_journey`):**  
Rather than displaying a generic text response, Square `[4.5]` renders **Antigravity Cross-Brand Flywheel // Rocket Money Vault -> Redfin Tour -> Mortgage Close** with structured visual artifacts (`Return JSON with keys: household_readiness_score, flywheel_stages (list of 4 stages {brand, event_detected, financial_metric, next_automated_trigger}), and bundled_incentive_offer ({rocket_money_perk, redfin_rebate, mortgage_credit, total_household_savings}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Demonstrates why Antigravity + MCP is the ideal fabric to connect Rocket's acquired subsidiaries (Redfin + Rocket Money + Mr. Cooper) without multi-quarter monolithic ERP integrations.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Google Antigravity Subagents` · `Redfin Telemetry MCP` · `Rocket Money Vault MCP` · `Gemini 4 Argon`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       4.5 ANTIGRAVITY REDFIN-TO-ROCKET CROSS-FUNNEL BOT (L300)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Antigravity Parent Agent (Gemini 4 Argon)]                           │
│  ├─► MCP Call 1: redfin_tour_mcp.get_upcoming_tour("Maya Lin")         │
│  ├─► MCP Call 2: rocket_money_mcp.get_vault_and_subscriptions()        │
│  └─► MCP Call 3: rocket_pricing_mcp.apply_buy_borrow_credit($3,500)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Personalized Pre-Tour Affordability Package + $7,800 Reserve Proof]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Expose Redfin Tour Telemetry and Rocket Money Goal Vaults as lightweight FastMCP Python servers.
2. Configure an Antigravity workflow script (`run_workflow`) that fans out in `parallel()` to fetch Redfin property details and Rocket Money cash-flow metrics.
3. Synthesize the unified Buy+Borrow pre-approval package with `gemini-4-argon`.

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
  "archetype": "redfin_rocketmoney_flywheel_journey",
  "readiness": "96/100 \u2014 Vault Target Reached + 4 Redfin Favorites in 48067",
  "bundle_savings": "$6,250 Total Ecosystem Savings ($2,500 Redfin Rebate + $3,750 Rocket Closing Credit)",
  "stages": [
    {
      "brand": "1. Rocket Money",
      "signal": "Down-Payment Goal Vault Hit 100% ($48,000 Saved)",
      "status": "COMPLETED"
    },
    {
      "brand": "2. Redfin Search",
      "signal": "Saved 4 Homes in Royal Oak MI ($425k\u2013$465k) & Booked Saturday Tour",
      "status": "ACTIVE SIGNAL"
    },
    {
      "brand": "3. Rocket Mortgage",
      "signal": "Auto-Generated $465k Verified Approval Letter in 1.2s",
      "status": "PRE-APPROVED"
    },
    {
      "brand": "4. Rocket Close & Mr. Cooper",
      "signal": "$6,250 Combined Rebate + Lifetime 0-Cost Refi Recapture Enrolled",
      "status": "LOCKED"
    }
  ]
}
```
