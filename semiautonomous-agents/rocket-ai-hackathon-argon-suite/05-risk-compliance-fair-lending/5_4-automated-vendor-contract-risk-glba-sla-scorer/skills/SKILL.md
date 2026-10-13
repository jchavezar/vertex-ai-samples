---
name: rocket-square-5_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [5.4] (Automated Vendor Contract Risk & GLBA SLA Scorer) with bespoke UI archetype `vendor_glba_contract_redliner`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[5.4]` — Automated Vendor Contract Risk & GLBA SLA Scorer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Rocket Procurement & Legal // Third-Party Vendor MSA & GLBA Safeguards Redliner`
- **UI Archetype Slug:** `vendor_glba_contract_redliner` (`layout_mode: contract_clause_redliner`)
- **Color Palette:** Primary Accent `#3B82F6` · Secondary Accent `#EF4444` · Surface `#080C16`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: vendor_risk_rating, clause_redlines (list of {section, vendor_original_text, policy_violation, rocket_replacement_clause}), and ciso_signoff_checklist.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
