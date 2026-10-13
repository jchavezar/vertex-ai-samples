---
name: rocket-square-3_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [3.2] (Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot) with bespoke UI archetype `payoff_1098_document_generator`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[3.2]` — Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator`
- **UI Archetype Slug:** `payoff_1098_document_generator` (`layout_mode: official_certificate`)
- **Color Palette:** Primary Accent `#06B6D4` · Secondary Accent `#10B981` · Surface `#04131A`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`
- **Routing Rationale:** Routed to gemini-3.8-flash (Official ADK & Agent Engine Runtime production model)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: payoff_letter ({loan_number, good_through_date, unpaid_principal, accrued_interest, per_diem_rate, recording_release_fee, total_payoff_due, wire_aba, wire_account}), and irs_form_1098 ({tax_year, box1_mortgage_interest, box5_mip, box6_points, property_address}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
