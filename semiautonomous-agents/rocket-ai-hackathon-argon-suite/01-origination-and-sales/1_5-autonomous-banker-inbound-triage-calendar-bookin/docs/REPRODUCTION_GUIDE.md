# Square `[1.5]`: Autonomous Banker Inbound Triage & Calendar Booking Suite — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `1.5` |
| **Bespoke Application Title** | **Antigravity MCP // Redfin Tour Webhook & Banker Calendar Dispatch Board** (`mcp_webhook_router_board`) |
| **Business Domain** | 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-demo-origination-254356041555.us-central1.run.app/?case=1.5](https://rocket-demo-origination-254356041555.us-central1.run.app/?case=1.5) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.5) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Multi-agent Antigravity workflow that ingests Redfin/RocketMortgage.com webhooks, queries O365 Calendar MCP, scores lead urgency, and provisions a 1003 sandbox draft.

**Description:**  
Ingest live webhook events when a homebuyer books a Redfin tour or completes a Rocket Money readiness check, verify NMLS state licensing & banker availability via Outlook Calendar MCP, and auto-provision the complete borrower profile.

**Bespoke UI Archetype (`mcp_webhook_router_board`):**  
Rather than displaying a generic text response, Square `[1.5]` renders **Antigravity MCP // Redfin Tour Webhook & Banker Calendar Dispatch Board** with structured visual artifacts (`Return JSON with keys: lead_urgency_score, redfin_tour_event ({property, tour_time, agent}), mcp_tool_trace (list of {step, mcp_server, latency_ms, payload_summary}), assigned_banker ({name, nmls, license_state, match_reason, booked_slot}), and instant_sms_draft.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Directly replaces Anthropic Claude Code + custom glue scripts with Antigravity's enterprise-governed Managed Agents API, native MCP harness, and VPC-SC sandboxed execution.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Google Antigravity 2.0` · `Antigravity gVisor Sandbox` · `MCP Server (O365 Calendar + Redfin Lead Webhook)` · `Gemini 4 Argon`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     1.5 ANTIGRAVITY INBOUND TRIAGE & CALENDAR BOOKING SUITE (L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Inbound Webhook: Redfin Tour Booked + Rocket Money Asset Link]       │
│  • Buyer touring $585k Ann Arbor home in 48 hrs with NO pre-approval   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Google Antigravity Multi-Agent Harness (Gemini 4 Argon)]             │
│  ├─► Subagent 1: Lead Scorer & Sandbox DTI/Asset Pre-Check             │
│  ├─► Subagent 2: MCP Call -> nmls_roster_lookup(state="MI")            │
│  └─► Subagent 3: MCP Call -> o365_calendar_book_slot(banker_id)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Provisioned 1003 Draft + Booked O365 Meeting + SMS Pre-Tour Alert]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Register the O365 Calendar & NMLS Roster MCP server in `~/.gemini/antigravity/mcp_config.json` (or Gemini Enterprise Agent Registry).
2. Use the Antigravity CLI (`agy`) or ADK orchestrator with `gemini-4-argon` to wire the 3-step pipeline: Webhook Validator -> NMLS/Calendar MCP Lookup -> 1003 Sandbox Provisioner.
3. Deploy the webhook triage service to Cloud Run.

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
  "archetype": "mcp_webhook_router_board",
  "urgency": "98 / 100 (CRITICAL \u2014 Redfin Tour in <48 Hours without Pre-Approval)",
  "buying_power": "Pre-Approved up to $680,000 | Target Home: $585,000 (86.3% LTV w/ $80,000 down)",
  "banker": " Brandon Kowalski (Sr. Premier Banker \u2022 NMLS #1498212 \u2022 MI Licensed \u2022 94% Redfin Conversion)",
  "slot": "Today at 4:30 PM EDT (15-Min Fast-Track Verified Approval Video Call)",
  "mcp_nodes": [
    {
      "server": "redfin-tour-events-mcp",
      "latency": "18ms",
      "event": "Tour Booked: 812 Brookwood, Birmingham MI ($585k) \u2014 Saturday 11:00 AM"
    },
    {
      "server": "rocket-money-plaid-mcp",
      "latency": "42ms",
      "event": "Verified Liquid Assets: $94,500 across Chase + Rocket Vault (764 FICO)"
    },
    {
      "server": "antigravity-gvisor-sandbox",
      "latency": "11ms",
      "event": "1003 Pre-Flight: 86.3% LTV ($80k Down) -> DU Approve/Eligible"
    },
    {
      "server": "o365-graph-calendar-mcp",
      "latency": "64ms",
      "event": "Booked Brandon Kowalski (MI Licensed) for 4:30 PM EDT Video Call + SMS Sent"
    }
  ]
}
```
