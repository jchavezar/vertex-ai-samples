---
name: rocket-square-4_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [4.5] (Redfin-to-Rocket Cross-Funnel Campaign Bot) with bespoke UI archetype `redfin_rocketmoney_flywheel_journey`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[4.5]` — Redfin-to-Rocket Cross-Funnel Campaign Bot

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Antigravity Cross-Brand Flywheel // Rocket Money Vault -> Redfin Tour -> Mortgage Close`
- **UI Archetype Slug:** `redfin_rocketmoney_flywheel_journey` (`layout_mode: cross_brand_flywheel`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#E11D48` · Surface `#070E14`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: household_readiness_score, flywheel_stages (list of 4 stages {brand, event_detected, financial_metric, next_automated_trigger}), and bundled_incentive_offer ({rocket_money_perk, redfin_rebate, mortgage_credit, total_household_savings}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
