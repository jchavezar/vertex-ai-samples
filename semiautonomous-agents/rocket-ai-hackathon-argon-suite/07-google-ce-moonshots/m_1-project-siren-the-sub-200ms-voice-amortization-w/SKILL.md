---
name: rocket-square-m_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [M.1] (Project Siren: The Sub-200ms Voice Amortization Whisperer) with bespoke UI archetype `project_siren_live_voice_amortization`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[M.1]` — Project Siren: The Sub-200ms Voice Amortization Whisperer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Project Siren // Real-Time Gemini Live Audio WebSocket (<200ms Barge-In Amortization)`
- **UI Archetype Slug:** `project_siren_live_voice_amortization` (`layout_mode: live_voice_amortization_curve`)
- **Color Palette:** Primary Accent `#06B6D4` · Secondary Accent `#EC4899` · Surface `#030712`
- **Interactive Controls:** `[{"id": "extra_monthly", "label": "Monthly Round-Up ($/mo)", "type": "range", "min": 0, "max": 1000, "step": 25, "default": 265.75}, {"id": "annual_lump_sum", "label": "Annual Tax-Refund Lump Sum ($/yr)", "type": "range", "min": 0, "max": 20000, "step": 1000, "default": 9000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Vertex AI Live API (gemini-3.8-live) + gemini-3.8-flash`
- **Routing Rationale:** Real-time Bidi Audio via gemini-3.8-live + Reasoning via gemini-3.8-flash
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: voice_barge_in_headline, payoff_comparison ({baseline_years, accelerated_years, years_saved, baseline_interest, accelerated_interest, interest_saved}), milestone_timeline (list of {year, baseline_balance, siren_balance, equity_unlocked}), and spoken_coach_summary.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
