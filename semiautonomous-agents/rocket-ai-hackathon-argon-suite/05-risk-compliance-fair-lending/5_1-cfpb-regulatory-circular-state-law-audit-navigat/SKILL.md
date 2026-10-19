---
name: rocket-square-5_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [5.1] (CFPB Regulatory Circular & State Law Audit Navigator) with bespoke UI archetype `cfpb_respa_regulatory_diff_vault`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[5.1]` — CFPB Regulatory Circular & State Law Audit Navigator

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Rocket Legal & NotebookLM // CFPB RESPA Section 8 & State Law Redline Vault`
- **UI Archetype Slug:** `cfpb_respa_regulatory_diff_vault` (`layout_mode: legal_redline_vault`)
- **Color Palette:** Primary Accent `#F59E0B` · Secondary Accent `#EF4444` · Surface `#0B0D13`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash`
- **Routing Rationale:** Discovery Engine streamAssist (gemini-enterprise-17877637_1787763712023) + gemini-3.8-flash
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: compliance_verdict, statutory_citations (list of {statute, section, rule_summary, violation_status}), feature_audit_rows (list of {feature_name, respa_risk_level, defect_found, mandatory_remediation}), and patched_ui_disclosure_text.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
