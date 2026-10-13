---
name: rocket-square-6_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [6.2] (AI Software Factory: Autonomous PRD-to-Pull-Request Architect) with bespoke UI archetype `antigravity_swarm_software_factory`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[6.2]` — AI Software Factory: Autonomous PRD-to-Pull-Request Architect

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Google Antigravity 2.0 Swarm // Autonomous PRD-to-Pull-Request Software Factory`
- **UI Archetype Slug:** `antigravity_swarm_software_factory` (`layout_mode: swarm_pr_pipeline`)
- **Color Palette:** Primary Accent `#A855F7` · Secondary Accent `#22C55E` · Surface `#06050B`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: pr_number_and_title, biweekly_math_verification ({standard_months, accelerated_months, years_shaved, lifetime_interest_saved}), subagent_lanes (list of 4 lanes {agent_role, workspace_branch, files_authored, test_status}), and generated_fastapi_endpoint_code.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
