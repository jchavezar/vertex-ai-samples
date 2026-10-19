---
name: rocket-square-3_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [3.3] (Hardship & Forbearance Live Servicing Assistant (CFPB Reg X)) with bespoke UI archetype `ccai_synopsis_agent_assist`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[3.3]` — Hardship & Forbearance Live Servicing Assistant (CFPB Reg X)

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Rocket Logic Synopsis Next-Gen // Real-Time CCAI Agent Assist & Reg X Loss-Mitigation HUD`
- **UI Archetype Slug:** `ccai_synopsis_agent_assist` (`layout_mode: contact_center_hud`)
- **Color Palette:** Primary Accent `#0EA5E9` · Secondary Accent `#F59E0B` · Surface `#05101A`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: caller_sentiment_score, reg_x_compliance_status, live_coaching_cards (list of {title, urgency, script_to_read, policy_citation}), workout_waterfall (list of {rank, program_name, eligibility, monthly_payment_effect}), and auto_crm_disposition.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
