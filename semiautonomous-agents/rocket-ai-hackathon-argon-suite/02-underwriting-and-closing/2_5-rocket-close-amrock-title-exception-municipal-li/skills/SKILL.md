---
name: rocket-square-2_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [2.5] (Rocket Close (Amrock) Title Exception & Municipal Lien Matcher) with bespoke UI archetype `amrock_title_curative_map`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[2.5]` — Rocket Close (Amrock) Title Exception & Municipal Lien Matcher

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Rocket Close (Amrock) // Schedule B-II Title Exception & ALTA Endorsement Clearer`
- **UI Archetype Slug:** `amrock_title_curative_map` (`layout_mode: light_executive_paper`)
- **Color Palette:** Primary Accent `#0D9488` · Secondary Accent `#2563EB` · Surface `#F8FAFC`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Gemini Enterprise streamAssist API (v1alpha) + Vertex AI`
- **Routing Rationale:** Executed against live Discovery Engine v1alpha streamAssist endpoint (gemini-enterprise-17877637_1787763712023)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: clear_to_close_status, schedule_b_exceptions (list of {item_no, defect_type, description, curative_resolution, treaty_or_alta_ref, auto_cleared}), and dispatched_vendor_packets (list of strings).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
