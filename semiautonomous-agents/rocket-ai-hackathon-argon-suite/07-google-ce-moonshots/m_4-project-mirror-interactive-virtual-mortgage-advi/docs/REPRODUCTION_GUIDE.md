# Square `[M.4]`: Project Mirror: Interactive Virtual Mortgage Advisor ('Astra Pro') — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `M.4` |
| **Bespoke Application Title** | **Project Mirror ('Astra Pro') // Interactive Live Voice & Dynamic Closing-Table Whiteboard** (`project_mirror_live_whiteboard_advisor`) |
| **Business Domain** | 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`rocket-demo-moonshots`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Vertex AI Live API (gemini-live-2.5-flash-native-audio) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.4](https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Low-latency interactive virtual human advisor with real-time phoneme lip-sync, eye-gaze tracking, and dynamic visual whiteboard rendering.

**Description:**  
Upgrade the hackathon portal's SVG avatar into a full interactive Virtual Mortgage Advisor ('Astra Pro') that speaks with natural cadence, animates lip-sync visemes in real time, and draws interactive closing-cost whiteboards as she explains complex loan structures.

**Bespoke UI Archetype (`project_mirror_live_whiteboard_advisor`):**  
Rather than displaying a generic text response, Square `[M.4]` renders **Project Mirror ('Astra Pro') // Interactive Live Voice & Dynamic Closing-Table Whiteboard** with structured visual artifacts (`Return JSON with keys: advisor_reassurance_headline, cash_to_close_buckets (list of {bucket_name, amount, color_tag, plain_english_note}), pmi_drop_schedule ({monthly_pmi, auto_drop_month, hpa_78_ltv_balance, early_redfin_avm_option}), and borrower_faq_cards (list of {question, simple_answer}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Delivers a warm, empathetic face-to-face digital advisor for first-time homebuyers at 1/20th the GPU cost of heavy pixel-streamed Unreal Engine avatars.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Live API` · `Gemini 4 Argon` · `WebAudio FFT Viseme Lip-Sync` · `Interactive SVG/Canvas Whiteboard`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       M.4 PROJECT MIRROR: INTERACTIVE VIRTUAL ADVISOR (L300)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [First-Time Buyer Voice/Text Question: "$25k saved on $350k home"]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon + WebAudio FFT Viseme Lip-Sync + Whiteboard Engine]   │
│  ├─► Animates Neural SVG Visemes (A/E/I/O/U/M) + Natural Eye Blinks    │
│  ├─► Draws Cash-to-Close Allocation Bar ($17.5k Down + $4.8k Escrow)   │
│  └─► Marks Homeowners Protection Act 78% LTV Automatic PMI Drop        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Synchronized Voice + Lip-Sync Avatar + Interactive Visual Whiteboard]│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Stream audio chunks from Gemini Live API (`BidiGenerateContent`) into a browser `AudioContext` connected to an `AnalyserNode` (`fftSize = 256`).
2. Map real-time frequency band energy to SVG mouth viseme paths (`open_wide`, `rounded_o`, `closed_m`, `smile_e`) at 60 FPS.
3. Simultaneously render structured tool-call JSON payloads onto the companion Closing Whiteboard.

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
  "archetype": "project_mirror_live_whiteboard_advisor",
  "cash_to_close": "5% Down ($17,500) + Net Closing/Escrow ($4,800) = $22,300 -> Leaves $2,700 Cushion in Rocket Money!",
  "monthly_piti": "P&I $2,020.31 + Royal Oak Tax/Ins $495 + PMI $118 = $2,633.31/mo",
  "pmi_drop": "Month 84 (Year 7.0) \u2014 PMI ($118/mo) automatically terminates under Homeowners Protection Act (or earlier via Redfin AVM appreciation!)"
}
```
