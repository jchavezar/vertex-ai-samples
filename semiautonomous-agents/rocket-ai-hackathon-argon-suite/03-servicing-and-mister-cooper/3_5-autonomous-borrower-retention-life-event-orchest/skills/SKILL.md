---
name: rocket-square-3_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [3.5] (Autonomous Borrower Retention & Life-Event Orchestrator) with bespoke UI archetype `life_event_equity_moveup_planner`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[3.5]` — Autonomous Borrower Retention & Life-Event Orchestrator

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Mr. Cooper + Redfin + Rocket // Autonomous Move-Up & Home Equity Bridge Planner`
- **UI Archetype Slug:** `life_event_equity_moveup_planner` (`layout_mode: equity_bridge_split`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#8B5CF6` · Surface `#041214`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: current_home_equity_summary ({avm_value, current_loan_balance, current_rate, net_usable_equity}), option_a_keep_and_second_lien ({program, blended_rate, combined_payment}), option_b_sell_and_redfin_buy ({target_redfin_home, down_payment_from_equity, new_loan_amount, new_monthly_pi, rocket_closing_credit}), and recommended_path.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
