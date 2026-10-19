---
name: rocket-square-m_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [M.5] (Project Air-Tight: Self-Healing Autonomous Compliance Swarm) with bespoke UI archetype `project_airtight_self_healing_pipeline`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[M.5]` — Project Air-Tight: Self-Healing Autonomous Compliance Swarm

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Project Air-Tight // Autonomous 4-Stage Self-Healing Closing Disclosure Pipeline`
- **UI Archetype Slug:** `project_airtight_self_healing_pipeline` (`layout_mode: self_healing_4stage_pipeline`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#F59E0B` · Surface `#040B0E`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Active Model: gemini-3.8-flash on Global Endpoint (ADK default: gemini-3.8-flash)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: final_clearance_status, total_cure_applied, pipeline_stages (list of 4 stages {stage_num, agent_name, status, defect_detected, autonomous_patch_applied, verification_hash}), and patched_closing_disclosure_diff (list of {line_item, before_value, after_value, compliance_rule}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
