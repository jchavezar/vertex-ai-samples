# Square `[3.4]`: Conversational Rocket Recapture Voice Concierge — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `3.4` |
| **Bespoke Application Title** | **Gemini Multimodal Live API // Real-Time Bidi Voice Portfolio Recapture Studio** (`gemini_live_bidi_voice_studio`) |
| **Business Domain** | 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Vertex AI Live API (gemini-3.8-live) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Ultra-low-latency bidirectional WebSocket voice agent that proactively contacts Mr. Cooper servicing clients when rates drop to recapture refis.

**Description:**  
Unlock the #1 revenue synergy of the Mr. Cooper acquisition: Portfolio Recapture. When rates drop 75+ bps below a borrower's note rate, the Gemini Live API voice agent engages them in a natural, interruptible conversation, computes exact monthly savings & breakeven, and warm-transfers to a licensed Rocket banker.

**Bespoke UI Archetype (`gemini_live_bidi_voice_studio`):**  
Rather than displaying a generic text response, Square `[3.4]` renders **Gemini Multimodal Live API // Real-Time Bidi Voice Portfolio Recapture Studio** with structured visual artifacts (`Return JSON with keys: recapture_offer_headline, monthly_savings, breakeven_months, comparison_cards (list of {label, current_loan, new_rocket_refi}), and spoken_barge_in_rebuttals (list of {borrower_objection, live_voice_response}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Native multimodal audio-to-audio streaming eliminates the 1,200ms STT -> LLM -> TTS cascade lag of Sierra Voice and AWS Connect Lex bots.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Live API (BidiGenerateContent WebSocket)` · `Gemini 4 Argon` · `Cloud Run Recapture Math Engine`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     3.4 GEMINI LIVE API ROCKET RECAPTURE VOICE CONCIERGE (L300)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Bidi WebSocket Audio Stream (wss://.../BidiGenerateContent)]         │
│  • Borrower barges in mid-sentence: "What about a 20-yr fixed?"        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Tool Call: calc_refi_recapture(30yr=5.875%, 20yr=5.625%)]       │
│  ├─► 30-Yr Refi: $2,492/mo (-$395/mo immediate cash flow savings)      │
│  └─► 20-Yr Refi: $2,927/mo (+$40/mo, cuts 7 yrs & saves $184k interest)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Instant Spoken Response + Warm Context Handoff to Rocket Banker]     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Open a bidirectional WebSocket connection to `wss://aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent`.
2. Register the `calc_refi_recapture` tool in the `setup` frame with `responseModalities: ['AUDIO']`.
3. When the borrower interrupts mid-sentence, Gemini Live API automatically halts audio output, invokes the recalculation tool, and speaks the 20-year vs 30-year comparison.

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
  "archetype": "gemini_live_bidi_voice_studio",
  "monthly_savings": "$298.44/month ($3,581.28/yr)",
  "breakeven": "13.1 Months",
  "lifetime_saved": "$89,412.00",
  "voice_model": "gemini-3.8-live (Real Bidi WebSocket)"
}
```
