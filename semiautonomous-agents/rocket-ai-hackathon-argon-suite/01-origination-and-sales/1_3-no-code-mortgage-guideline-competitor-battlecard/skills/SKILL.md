---
name: rocket-square-1_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [1.3] (No-Code Mortgage Guideline & Competitor Battlecard Agent) with bespoke UI archetype `gemini_enterprise_streamassist_hub`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[1.3]` — No-Code Mortgage Guideline & Competitor Battlecard Agent

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Gemini Enterprise (Sobi / Spark) // GSE Guideline & Competitor Battlecard Hub`
- **UI Archetype Slug:** `gemini_enterprise_streamassist_hub` (`layout_mode: ge_streamassist_split`)
- **Color Palette:** Primary Accent `#8B5CF6` · Secondary Accent `#EC4899` · Surface `#090814`
- **Interactive Controls:** `[{"id": "price", "label": "Macomb County Purchase ($)", "type": "range", "min": 200000, "max": 600000, "step": 10000, "default": 380000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Gemini Enterprise streamAssist API (v1alpha) + Vertex AI`
- **Routing Rationale:** Executed against live Discovery Engine v1alpha streamAssist endpoint (gemini-enterprise-17877637_1787763712023)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: winning_recommendation, monthly_savings_vs_broker, program_matrix (list of 3 programs {program, min_fico, down_pct, monthly_pi, monthly_mi, total_payment, llpa_impact}), and banker_objection_script (list of {broker_claim, rocket_counter}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
