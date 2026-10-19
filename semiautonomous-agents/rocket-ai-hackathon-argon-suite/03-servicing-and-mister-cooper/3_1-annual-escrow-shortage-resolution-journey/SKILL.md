---
name: rocket-square-3_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [3.1] (Annual Escrow Shortage Resolution Journey) with bespoke UI archetype `escrow_waterfall_interactive`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[3.1]` — Annual Escrow Shortage Resolution Journey

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Mr. Cooper x GECX // Interactive Annual Escrow Shortage Waterfall & Payment Slider`
- **UI Archetype Slug:** `escrow_waterfall_interactive` (`layout_mode: servicing_waterfall`)
- **Color Palette:** Primary Accent `#14B8A6` · Secondary Accent `#06B6D4` · Surface `#031217`
- **Interactive Controls:** `[{"id": "new_tax_yr", "label": "New Annual Property Tax ($)", "type": "range", "min": 4800, "max": 8400, "step": 120, "default": 6000}, {"id": "shortage_total", "label": "Escrow Shortage Balance ($)", "type": "range", "min": 600, "max": 3600, "step": 120, "default": 1740}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash`
- **Routing Rationale:** Discovery Engine streamAssist (gemini-enterprise-17877637_1787763712023) + gemini-3.8-flash
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: empathetic_headline, payment_comparison ({old_total, new_lump_sum_total, new_12mo_spread_total}), waterfall_bars (list of {component, old_mo, new_mo, delta_mo, explanation}), and repayment_options (list of {option_title, upfront_due, monthly_payment, pros}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
