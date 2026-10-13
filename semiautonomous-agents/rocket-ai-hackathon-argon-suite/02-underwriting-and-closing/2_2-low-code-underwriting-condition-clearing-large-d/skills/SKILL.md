---
name: rocket-square-2_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [2.2] (Low-Code Underwriting Condition Clearing & Large-Deposit Agent) with bespoke UI archetype `adk_hitl_condition_clearing_DAG`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[2.2]` — Low-Code Underwriting Condition Clearing & Large-Deposit Agent

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `GEAP Visual Agent Studio + ADK // Bank Statement Large-Deposit Clearing Gate`
- **UI Archetype Slug:** `adk_hitl_condition_clearing_DAG` (`layout_mode: light_executive_paper`)
- **Color Palette:** Primary Accent `#059669` · Secondary Accent `#D97706` · Surface `#F8FAFC`
- **Interactive Controls:** `[{"id": "qualifying_monthly_income", "label": "Qualifying Income ($/mo)", "type": "range", "min": 6000, "max": 22000, "step": 500, "default": 11400}, {"id": "ending_balance", "label": "Chase Ending Balance ($)", "type": "range", "min": 30000, "max": 95000, "step": 1000, "default": 51200}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: fannie_50pct_threshold, deposits_ledger (list of {date, description, amount, exceeds_threshold, disposition}), asset_backout_math ({ending_balance, unverified_deducted, verified_remaining, required_to_close, pass_fail}), and cel_blocking_gate_payload ({stage, policy_rule, condition_text}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
