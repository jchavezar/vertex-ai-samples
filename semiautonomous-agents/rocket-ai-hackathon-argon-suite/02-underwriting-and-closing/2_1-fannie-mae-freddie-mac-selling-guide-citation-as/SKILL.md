---
name: rocket-square-2_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [2.1] (Fannie Mae / Freddie Mac Selling Guide Citation Assistant) with bespoke UI archetype `notebooklm_gse_citation_desk`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[2.1]` — Fannie Mae / Freddie Mac Selling Guide Citation Assistant

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `NotebookLM Enterprise & StreamAssist // Fannie B3-3.1 & Freddie 5303 Citation Desk`
- **UI Archetype Slug:** `notebooklm_gse_citation_desk` (`layout_mode: light_executive_paper`)
- **Color Palette:** Primary Accent `#0284C7` · Secondary Accent `#4F46E5` · Surface `#F8FAFC`
- **Interactive Controls:** `[{"id": "base_annual", "label": "Base Salary ($/yr)", "type": "range", "min": 100000, "max": 300000, "step": 5000, "default": 165000}, {"id": "bonus_2025", "label": "2025 Bonus ($/yr)", "type": "range", "min": 5000, "max": 40000, "step": 1000, "default": 14000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash`
- **Routing Rationale:** Discovery Engine streamAssist (gemini-enterprise-17877637_1787763712023) + gemini-3.8-flash
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: total_qualifying_monthly, underwriting_ruling, income_components (list of {component, calculation, monthly_allowed, gse_citation, status_pill}), and red_flag_alerts (list of strings).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
