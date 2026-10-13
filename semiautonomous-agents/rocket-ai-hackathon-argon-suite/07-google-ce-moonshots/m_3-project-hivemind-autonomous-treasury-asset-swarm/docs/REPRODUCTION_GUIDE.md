# Square `[M.3]`: Project HiveMind: Autonomous Treasury & Asset Swarm — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `M.3` |
| **Bespoke Application Title** | **Project HiveMind // 4-Agent Treasury Yield Drop & Mr. Cooper Portfolio Lock Swarm** (`project_hivemind_treasury_swarm`) |
| **Business Domain** | 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`rocket-demo-moonshots`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.3](https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Cooperative 4-agent swarm coordinating 10-Yr Treasury rate dips, Mr. Cooper servicing cohorts, underwriting pre-clearance, and instant lock execution.

**Description:**  
When the 10-Year US Treasury yield drops 12 bps intraday, Project HiveMind autonomously wakes up, scans 50,000 Mr. Cooper & Rocket pipeline loans, pre-clears automated underwriting (AUS) & AVM waivers, and dispatches 1-tap rate-lock offers before the market rebounds.

**Bespoke UI Archetype (`project_hivemind_treasury_swarm`):**  
Rather than displaying a generic text response, Square `[M.3]` renders **Project HiveMind // 4-Agent Treasury Yield Drop & Mr. Cooper Portfolio Lock Swarm** with structured visual artifacts (`Return JSON with keys: treasury_trigger_event, recaptured_volume_usd, swarm_agents (list of 4 agents {agent_id, role, model, latency_ms, input_signal, output_artifact}), and sample_borrower_1tap_offer ({borrower_name, old_rate, new_rate, monthly_savings, appraisal_waiver_code}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Demonstrates stateful A2A / Swarm coordination across Capital Markets, Underwriting, and Servicing in under 3 seconds.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Google Antigravity Native Swarm` · `Google Cloud Agent Registry` · `Gemini 4 Argon` · `Gemini 3.8 Flash Worker Pool`

```text
┌────────────────────────────────────────────────────────────────────────┐
│        M.3 PROJECT HIVEMIND: AUTONOMOUS ASSET SWARM (L300)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [@treasury-watcher]: Detects -14 bps 10Y Treasury Drop (5.75% Window) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Parallel Antigravity Swarm Execution Board]                          │
│  ├─► @mr-cooper-miner:   Filters 1,240 loans >= 6.875% & <= 80% LTV    │
│  ├─► @aus-preclear-bot:  Batch-verifies Fannie Desktop Underwriter AVM │
│  └─► @one-tap-dispatcher: Sends 1-Tap Lock Push to Rocket Mobile App   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [$91.6M Locked Refi Volume in 4 Hrs | $342/mo Saved per Household]    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Spawn a 4-worker Antigravity Swarm (`treasury-watcher`, `mr-cooper-miner`, `aus-preclear-bot`, `one-tap-dispatcher`) pinned to `gemini-4-argon` and `gemini-3.8-flash`.
2. Connect the swarm to BigQuery servicing cohorts and Rocket Capital Markets hedge capacity via MCP.
3. Execute parallel pre-clearance and push 1-tap rate-lock tokens to the Rocket Mobile App.

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
  "archetype": "project_hivemind_treasury_swarm",
  "speed": "2.84 Seconds across 4 Parallel Antigravity Agents",
  "cohort": "1,240 Households Pre-Cleared via AUS + Fannie Value Acceptance Waiver",
  "savings": "$293.43/month ($3,521.16/yr)",
  "volume": "229 Instant 1-Tap Locks = $91,600,000 Recaptured Loan Volume",
  "swarm_nodes": [
    {
      "id": "1. Capital-Markets-Watcher",
      "model": "gemini-3.8-flash",
      "task": "Detected 10Y Treasury -12 bps drop to 3.94%; unlocked 5.75% 30Y par pricing window"
    },
    {
      "id": "2. BigQuery-Cohort-Miner",
      "model": "gemini-3.8-flash",
      "task": "Filtered 4.2M Mr. Cooper loans -> 1,240 MI/TX/NC loans w/ >6.75% rate & >22% equity"
    },
    {
      "id": "3. AUS-Waiver-Certifier",
      "model": "gemini-3.8-flash",
      "task": "Pre-ran Fannie Mae DU Value Acceptance (Appraisal Waiver) & title check in batch"
    },
    {
      "id": "4. Rocket-Push-Dispatcher",
      "model": "gemini-3.8-flash",
      "task": "Sent personalized 1-Tap Rate-Lock push notification to Rocket Money & Mr. Cooper apps"
    }
  ]
}
```
