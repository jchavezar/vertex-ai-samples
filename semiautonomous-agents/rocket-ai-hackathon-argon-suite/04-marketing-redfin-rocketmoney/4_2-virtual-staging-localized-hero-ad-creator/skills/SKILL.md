---
name: rocket-square-4_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [4.2] (Virtual Staging & Localized Hero Ad Creator) with bespoke UI archetype `imagen_virtual_staging_comparator`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[4.2]` — Virtual Staging & Localized Hero Ad Creator

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Nano Banana 2 / Gempix-2 // Interactive Corktown Loft Virtual Staging & TILA Ad Studio`
- **UI Archetype Slug:** `imagen_virtual_staging_comparator` (`layout_mode: virtual_staging_slider`)
- **Color Palette:** Primary Accent `#E11D48` · Secondary Accent `#F59E0B` · Surface `#120914`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: selected_design_theme, staging_elements_added (list of strings), hero_ad_overlay ({headline, payment_callout, grant_badge, tila_reg_z_disclaimer}), and social_ad_variants (list of {channel, copy_text, cta_button}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
