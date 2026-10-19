---
name: rocket-square-1_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [1.2] (Outlook Hyper-Personalized Rate-Lock & Pre-Approval Agent) with bespoke UI archetype `outlook_addin_composer`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[1.2]` — Outlook Hyper-Personalized Rate-Lock & Pre-Approval Agent

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Microsoft Outlook 365 // Rocket Verified Approval & Rate-Lock Add-In`
- **UI Archetype Slug:** `outlook_addin_composer` (`layout_mode: o365_desktop_ribbon`)
- **Color Palette:** Primary Accent `#0078D4` · Secondary Accent `#10B981` · Surface `#0A111F`
- **Interactive Controls:** `[{"id": "loan_amount", "label": "Loan Amount ($)", "type": "range", "min": 250000, "max": 900000, "step": 10000, "default": 500000}, {"id": "base_rate", "label": "Par Rate (%)", "type": "range", "min": 5.25, "max": 7.25, "step": 0.125, "default": 6.125}, {"id": "buydown_pts", "label": "Discount Points", "type": "range", "min": 0.25, "max": 2.0, "step": 0.25, "default": 0.75}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: email_headers ({to, cc, subject}), rate_options_table (list of 3 options with {option_name, rate, monthly_pi, upfront_cost, breakeven_months, badge}), verified_approval_certificate ({cert_id, max_price, property_address, expiration}), and email_body_paragraphs (list of strings).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
