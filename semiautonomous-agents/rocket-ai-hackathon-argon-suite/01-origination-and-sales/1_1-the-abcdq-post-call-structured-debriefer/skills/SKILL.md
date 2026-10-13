---
name: rocket-square-1_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [1.1] (The ABCDQ Post-Call Structured Debriefer) with bespoke UI archetype `1003_intake_cockpit`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[1.1]` — The ABCDQ Post-Call Structured Debriefer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Rocket Logic // Form 1003 Pre-Qual & CRM Intake Cockpit`
- **UI Archetype Slug:** `1003_intake_cockpit` (`layout_mode: fintech_ledger`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#3B82F6` · Surface `#060B16`
- **Interactive Controls:** `[{"id": "price", "label": "Target Redfin Home ($)", "type": "range", "min": 250000, "max": 850000, "step": 5000, "default": 460000}, {"id": "down_pct", "label": "Down Payment (%)", "type": "range", "min": 3, "max": 25, "step": 1, "default": 10}, {"id": "rate", "label": "30Y Fixed Note Rate (%)", "type": "range", "min": 5.0, "max": 7.5, "step": 0.125, "default": 6.125}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: executive_verdict, borrower_profile (name, fico, target_property), income_breakdown ( list of {source, monthly_amount, rule_note} ), dti_gauges ({front_dti, back_dti, max_allowed, status}), salesforce_payload (dict), and outlook_email_html (str).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
