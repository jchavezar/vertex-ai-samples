---
name: rocket-square-m_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [M.3] (Project HiveMind: Autonomous Treasury & Asset Swarm) with bespoke UI archetype `project_hivemind_treasury_swarm`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[M.3]` — Project HiveMind: Autonomous Treasury & Asset Swarm

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Project HiveMind // 4-Agent Treasury Yield Drop & Mr. Cooper Portfolio Lock Swarm`
- **UI Archetype Slug:** `project_hivemind_treasury_swarm` (`layout_mode: multi_agent_swarm_canvas`)
- **Color Palette:** Primary Accent `#C084FC` · Secondary Accent `#10B981` · Surface `#050212`
- **Interactive Controls:** `[{"id": "cohort_size", "label": "Pre-Cleared Mr. Cooper Cohort", "type": "range", "min": 500, "max": 5000, "step": 100, "default": 1240}, {"id": "conversion_pct", "label": "4-Hr 1-Tap Lock Conversion (%)", "type": "range", "min": 5, "max": 35, "step": 1, "default": 18.5}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: treasury_trigger_event, recaptured_volume_usd, swarm_agents (list of 4 agents {agent_id, role, model, latency_ms, input_signal, output_artifact}), and sample_borrower_1tap_offer ({borrower_name, old_rate, new_rate, monthly_savings, appraisal_waiver_code}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
