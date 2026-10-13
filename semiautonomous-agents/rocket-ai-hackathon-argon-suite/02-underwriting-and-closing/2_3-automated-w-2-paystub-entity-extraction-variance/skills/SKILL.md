---
name: rocket-square-2_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [2.3] (Automated W-2 & Paystub Entity Extraction & Variance Pipeline) with bespoke UI archetype `docai_paystub_w2_ocr_inspector`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[2.3]` — Automated W-2 & Paystub Entity Extraction & Variance Pipeline

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector`
- **UI Archetype Slug:** `docai_paystub_w2_ocr_inspector` (`layout_mode: light_executive_paper`)
- **Color Palette:** Primary Accent `#2563EB` · Secondary Accent `#DC2626` · Surface `#F8FAFC`
- **Interactive Controls:** `[{"id": "stated_monthly", "label": "1003 Stated Income ($/mo)", "type": "range", "min": 8500, "max": 13500, "step": 250, "default": 10500}, {"id": "ytd_base_9m", "label": "9-Mo YTD Base ($)", "type": "range", "min": 65000, "max": 105000, "step": 1500, "default": 82500}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: dba_entity_resolution ({paystub_name, w2_name, fein, match_confidence}), extracted_fields (list of {field_name, box_ref, extracted_value, ocr_confidence}), variance_analysis ({stated_monthly, documented_monthly, variance_pct, tolerance_limit, status}), and los_remediation_action.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
