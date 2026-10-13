---
name: rocket-square-3_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [3.4] (Conversational Rocket Recapture Voice Concierge) with bespoke UI archetype `gemini_live_bidi_voice_studio`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[3.4]` — Conversational Rocket Recapture Voice Concierge

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Gemini Multimodal Live API // Real-Time Bidi Voice Portfolio Recapture Studio`
- **UI Archetype Slug:** `gemini_live_bidi_voice_studio` (`layout_mode: live_voice_waveform`)
- **Color Palette:** Primary Accent `#14B8A6` · Secondary Accent `#EC4899` · Surface `#020E14`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Vertex AI Live API WebSocket (gemini-live-2.5-flash-native-audio) + gemini-3.8-flash`
- **Routing Rationale:** Real-time 16kHz->24kHz PCM Bidi Audio via gemini-live-2.5-flash-native-audio (us-central1)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: recapture_offer_headline, monthly_savings, breakeven_months, comparison_cards (list of {label, current_loan, new_rocket_refi}), and spoken_barge_in_rebuttals (list of {borrower_objection, live_voice_response}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
