# Square `[3.3]`: Hardship & Forbearance Live Servicing Assistant (CFPB Reg X) — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `3.3` |
| **Bespoke Application Title** | **Rocket Logic Synopsis Next-Gen // Real-Time CCAI Agent Assist & Reg X Loss-Mitigation HUD** (`ccai_synopsis_agent_assist`) |
| **Business Domain** | 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Real-time call transcription, distress keyword detection, CFPB loss mitigation waterfall cards, and 1-click post-call wrap-up replacing manual Synopsis work.

**Description:**  
Supercharge Rocket Logic Synopsis: detect borrower financial distress in real time, surface compliant Fannie/Freddie/FHA loss mitigation waterfall options (Forbearance vs. Payment Deferral vs. Flex Modification), and generate a zero-edit wrap-up log.

**Bespoke UI Archetype (`ccai_synopsis_agent_assist`):**  
Rather than displaying a generic text response, Square `[3.3]` renders **Rocket Logic Synopsis Next-Gen // Real-Time CCAI Agent Assist & Reg X Loss-Mitigation HUD** with structured visual artifacts (`Return JSON with keys: caller_sentiment_score, reg_x_compliance_status, live_coaching_cards (list of {title, urgency, script_to_read, policy_citation}), workout_waterfall (list of {rank, program_name, eligibility, monthly_payment_effect}), and auto_crm_disposition.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Upgrades Rocket Logic Synopsis (currently batch/AWS Bedrock) into a real-time in-call co-pilot that prevents CFPB Regulation X dual-tracking violations while cutting wrap-up time by 82%.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `CCAI Agent Assist` · `Chirp 3 Streaming STT` · `Gemini 4 Argon` · `Vertex AI Policy Grounding`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     3.3 CCAI AGENT ASSIST HARDSHIP & FORBEARANCE CO-PILOT (L200-300)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Audio Stream -> Chirp 3 Real-Time STT Transcript]               │
│  • Detects "layoff", "medical surgery", "recall letter Dec 1"          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [CCAI Agent Assist + Gemini 4 Argon Loss Mitigation Waterfall]        │
│  ├─► CFPB Reg X Guardrail: Zero Foreclosure Risk (<120 days)           │
│  ├─► Fannie Mae Waterfall: 2-Mo Forbearance -> Payment Deferral        │
│  └─► Defers $4,360 to non-interest tail; Dec 1 PITI stays $2,180/mo    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Specialist Suggestion Cards + 1-Click Synopsis Wrap-Up Log]     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Create a Conversation Profile in Google Cloud CCAI Agent Assist with Knowledge Assist (grounded in CFPB Reg X & Fannie Mae Servicing Guide D2-3.2) and Summarization enabled.
2. Stream live call audio via gRPC `StreamingAnalyzeContent`.
3. Render the real-time Agent Assist suggestion cards and 1-click Synopsis wrap-up payload in the servicing desktop.

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
  "archetype": "ccai_synopsis_agent_assist",
  "sentiment": "Distressed -> Reassured (+64 Sentiment Shift)",
  "reg_x_gate": "100% COMPLIANT \u2014 Dual-Tracking Foreclosure Freeze Armed",
  "waterfall": [
    {
      "rank": "1st Priority",
      "program": "Fannie Mae Payment Deferral",
      "detail": "Defer 2 Missed Payments ($4,980) to Non-Interest Balance at Maturity",
      "status": "ELIGIBLE NOW"
    },
    {
      "rank": "2nd Priority",
      "program": "3-Month Unemployment Forbearance",
      "detail": "Temporary pause while starting new GM engineering role next month",
      "status": "AVAILABLE"
    },
    {
      "rank": "3rd Priority",
      "program": "Fannie Mae Flex Modification (D2-3.2-06)",
      "detail": "Extend term to 480 months targeting 20% P&I reduction if hardship persists",
      "status": "BACKUP"
    }
  ]
}
```
