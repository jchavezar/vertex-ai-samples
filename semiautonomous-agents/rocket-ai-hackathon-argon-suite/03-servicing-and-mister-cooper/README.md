# 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`rocket-demo-servicing`)

> **Domain Theme:** Mr. Cooper x Rocket Servicing Omnichannel CX & Voice Studio (The Sierra AI Killer)  
> **Mission:** Drive 85%+ first-contact resolution across Rocket & Mr. Cooper's multi-million-loan servicing portfolio (escrow shortages, payoffs, Form 1098s, CFPB hardship) and recapture refinances with Gemini Live API.  
> **AWS / Anthropic / Sierra Win-Back:** Replaces expensive third-party Sierra AI per-resolution fees and AWS Connect + Bedrock wrappers with native Gemini Enterprise for CX (GECX), CCAI Agent Assist (upgrading Rocket Logic Synopsis), and sub-200ms Gemini Multimodal Live API.

## Live Cloud Run Service & Shared Private Login
- **Live Domain Cloud Run App:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/servicing](https://rocket-hackathon-portal-254356041555.us-central1.run.app/domain/servicing)
- **Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)
- **Shared Username:** `rocket`
- **Shared Password:** `Argon2026!`

## Bespoke Use-Case Apps in This Domain

| Code | Level | Bespoke UI Archetype | Active Model Routing | Live Demo URL | Cloud Blueprint | GitHub Subfolder (`docs/`, `code/`, `skills/`, `mock_data/`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`[3.1]`** | `L100–L200` | `escrow_waterfall_interactive` | `gemini-3.8-flash` | [Launch `3.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.1) | [Blueprint `/docs/3.1`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.1) | [`3_1-annual-escrow-shortage-resolution-journey/`](./3_1-annual-escrow-shortage-resolution-journey/) |
| **`[3.2]`** | `L200` | `payoff_1098_document_generator` | `gemini-3.8-flash` | [Launch `3.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.2) | [Blueprint `/docs/3.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2) | [`3_2-self-service-payoff-quote-irs-form-1098-voice-ch/`](./3_2-self-service-payoff-quote-irs-form-1098-voice-ch/) |
| **`[3.3]`** | `L200–L300` | `ccai_synopsis_agent_assist` | `gemini-4-argon` | [Launch `3.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.3) | [Blueprint `/docs/3.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.3) | [`3_3-hardship-forbearance-live-servicing-assistant-cf/`](./3_3-hardship-forbearance-live-servicing-assistant-cf/) |
| **`[3.4]`** | `L300` | `gemini_live_bidi_voice_studio` | `gemini-3.8-flash` | [Launch `3.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.4) | [Blueprint `/docs/3.4`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.4) | [`3_4-conversational-rocket-recapture-voice-concierge/`](./3_4-conversational-rocket-recapture-voice-concierge/) |
| **`[3.5]`** | `L300` | `life_event_equity_moveup_planner` | `gemini-3.8-flash` | [Launch `3.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.5) | [Blueprint `/docs/3.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.5) | [`3_5-autonomous-borrower-retention-life-event-orchest/`](./3_5-autonomous-borrower-retention-life-event-orchest/) |
