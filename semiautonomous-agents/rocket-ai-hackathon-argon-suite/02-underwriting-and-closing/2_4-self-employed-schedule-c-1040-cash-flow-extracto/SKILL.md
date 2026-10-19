---
name: rocket-square-2_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [2.4] (Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084)) with bespoke UI archetype `form_1084_tax_worksheet`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[2.4]` — Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084)

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Fannie Mae Form 1084 // Self-Employed Schedule C & K-1 Cash-Flow Worksheet`
- **UI Archetype Slug:** `form_1084_tax_worksheet` (`layout_mode: light_executive_paper`)
- **Color Palette:** Primary Accent `#4F46E5` · Secondary Accent `#059669` · Surface `#F8FAFC`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: qualifying_monthly_income, yoy_trend_pct, worksheet_lines (list of {irs_line, description, yr_2024, yr_2025, addback_or_deduct, rule_explanation}), and underwriter_signoff_note.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
