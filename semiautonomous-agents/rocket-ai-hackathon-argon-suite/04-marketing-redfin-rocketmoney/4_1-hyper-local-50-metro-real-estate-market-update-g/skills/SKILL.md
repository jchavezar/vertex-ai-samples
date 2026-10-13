---
name: rocket-square-4_1
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [4.1] (Hyper-Local 50-Metro Real Estate Market Update Generator) with bespoke UI archetype `metro_50_market_pulse_heatmap`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[4.1]` — Hyper-Local 50-Metro Real Estate Market Update Generator

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Redfin x Rocket // 50-Metro Real Estate Inventory, Price-Drop & Rate Pulse Grid`
- **UI Archetype Slug:** `metro_50_market_pulse_heatmap` (`layout_mode: market_pulse_dashboard`)
- **Color Palette:** Primary Accent `#F43F5E` · Secondary Accent `#8B5CF6` · Surface `#110B18`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: national_headline, metro_cards (list of 4 metros {metro_name, median_price, yoy_change, active_inventory_delta, seller_concession_pct, buying_power_headline, local_ad_hook}), and seo_newsletter_blurb.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
