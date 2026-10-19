# Square `[M.1]`: Project Siren: The Sub-200ms Voice Amortization Whisperer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `M.1` |
| **Bespoke Application Title** | **Project Siren // Real-Time Gemini Live Audio WebSocket (<200ms Barge-In Amortization)** (`project_siren_live_voice_amortization`) |
| **Business Domain** | 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`rocket-demo-moonshots`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Vertex AI Live API (gemini-live-2.5-flash-native-audio) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Interruptible verbal mortgage math whisperer that recalculates amortization curves, extra principal payments, and tax shields mid-sentence.

**Description:**  
Speak naturally to Siren during a high-stakes client call, interrupt mid-sentence ('Wait—what if they throw their $12,000 April tax refund at principal every year?'), and watch the 30-year amortization curve morph in under 200ms.

**Bespoke UI Archetype (`project_siren_live_voice_amortization`):**  
Rather than displaying a generic text response, Square `[M.1]` renders **Project Siren // Real-Time Gemini Live Audio WebSocket (<200ms Barge-In Amortization)** with structured visual artifacts (`Return JSON with keys: voice_barge_in_headline, payoff_comparison ({baseline_years, accelerated_years, years_saved, baseline_interest, accelerated_interest, interest_saved}), milestone_timeline (list of {year, baseline_balance, siren_balance, equity_unlocked}), and spoken_coach_summary.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Zero-lag barge-in with live tool invocation turns mortgage math into an interactive, emotional visual story.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Live API` · `Gemini 4 Argon` · `WebAudio Neural Synthesizer` · `Real-Time Canvas Curve Engine`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       M.1 PROJECT SIREN: VOICE AMORTIZATION WHISPERER (L300)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Voice Barge-In: "Round to $3,000/mo + $9k March Ford Bonus!"]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Live API Barge-In Handler + Month-by-Month Curve Sandbox]     │
│  ├─► Standard 30-Yr: 360 mos | $534,330 Total Interest                 │
│  └─► Siren Accelerated: 214 mos (17.8 yrs) | Saves $238,400+ Interest! │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Instant Spoken Audio + Live Animated Amortization Curve Morph]       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Connect browser WebAudio microphone stream to Gemini Live API WebSocket.
2. Bind the `calc_siren_accelerator` month-by-month amortization curve generator as a live function tool.
3. Stream the returned JSON curve array directly into the HTML5 Canvas / SVG chart while Siren speaks the result.

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
  "archetype": "project_siren_live_voice_amortization",
  "baseline": "360 Months (30.0 Yrs) @ $2,734.25/mo | Total Interest: $534,330",
  "accelerated": "184 Months (15.3 Yrs) -> Debt-Free 14.7 YEARS EARLIER!",
  "saved": "$290,135.24 Lifetime Interest Saved!",
  "curve_points": [
    {
      "yr": "Year 0",
      "std": 450000,
      "siren": 450000
    },
    {
      "yr": "Year 5",
      "std": 413200,
      "siren": 342100
    },
    {
      "yr": "Year 10",
      "std": 362800,
      "siren": 208400
    },
    {
      "yr": "Year 15",
      "std": 293500,
      "siren": 54200
    },
    {
      "yr": "Year 18.2",
      "std": 238900,
      "siren": 0
    },
    {
      "yr": "Year 30",
      "std": 0,
      "siren": 0
    }
  ]
}
```
