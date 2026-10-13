---
name: rocket-square-m_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [M.2] (Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub) with bespoke UI archetype `project_spatial_close_3d_homestyle`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[M.2]` — Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Project Spatial Close // 3D Royal Oak Neighborhood Solar & Fannie HomeStyle Renovation Hub`
- **UI Archetype Slug:** `project_spatial_close_3d_homestyle` (`layout_mode: spatial_3d_renovation`)
- **Color Palette:** Primary Accent `#F43F5E` · Secondary Accent `#06B6D4` · Surface `#080514`
- **Interactive Controls:** `[{"id": "purchase_price", "label": "As-Is Purchase Price ($)", "type": "range", "min": 280000, "max": 600000, "step": 5000, "default": 385000}, {"id": "renovation_cost", "label": "Escrowed Renovation Budget ($)", "type": "range", "min": 25000, "max": 120000, "step": 5000, "default": 55000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: instant_equity_created, homestyle_vs_heloc ({homestyle_single_pi, separate_heloc_combined_pi, monthly_savings}), renovation_line_items (list of {scope_item, contractor_budget, appraised_value_add, roi_multiple}), and neighborhood_3d_telemetry ({solar_exposure, commute_to_detroit_mins, school_district}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
