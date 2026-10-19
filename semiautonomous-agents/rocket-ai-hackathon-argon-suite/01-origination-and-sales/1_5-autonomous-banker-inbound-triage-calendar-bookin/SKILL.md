---
name: rocket-square-1_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [1.5] (Autonomous Banker Inbound Triage & Calendar Booking Suite) with bespoke UI archetype `mcp_webhook_router_board`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[1.5]` — Autonomous Banker Inbound Triage & Calendar Booking Suite

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Antigravity MCP // Redfin Tour Webhook & Banker Calendar Dispatch Board`
- **UI Archetype Slug:** `mcp_webhook_router_board` (`layout_mode: mcp_event_topology`)
- **Color Palette:** Primary Accent `#06B6D4` · Secondary Accent `#10B981` · Surface `#040D14`
- **Interactive Controls:** `[{"id": "list_price", "label": "Redfin Tour Property ($)", "type": "range", "min": 350000, "max": 950000, "step": 15000, "default": 585000}, {"id": "assets", "label": "Rocket Money Liquid Assets ($)", "type": "range", "min": 35000, "max": 200000, "step": 5000, "default": 94500}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: lead_urgency_score, redfin_tour_event ({property, tour_time, agent}), mcp_tool_trace (list of {step, mcp_server, latency_ms, payload_summary}), assigned_banker ({name, nmls, license_state, match_reason, booked_slot}), and instant_sms_draft.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
