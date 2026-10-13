---
name: rocket-square-m_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [M.4] (Project Mirror: Interactive Virtual Mortgage Advisor ('Astra Pro')) with bespoke UI archetype `project_mirror_live_whiteboard_advisor`, deterministic gVisor sandbox math, and `gemini-3.8-flash` routing.
---

# Skill: Reproduce Square `[M.4]` — Project Mirror: Interactive Virtual Mortgage Advisor ('Astra Pro')

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Project Mirror ('Astra Pro') // Interactive Live Voice & Dynamic Closing-Table Whiteboard`
- **UI Archetype Slug:** `project_mirror_live_whiteboard_advisor` (`layout_mode: live_whiteboard_advisor`)
- **Color Palette:** Primary Accent `#38BDF8` · Secondary Accent `#A855F7` · Surface `#040814`
- **Interactive Controls:** `[{"id": "price", "label": "First Home Price ($)", "type": "range", "min": 220000, "max": 550000, "step": 10000, "default": 350000}, {"id": "savings", "label": "Rocket Money Savings ($)", "type": "range", "min": 15000, "max": 60000, "step": 1000, "default": 25000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-3.8-flash`
- **Runtime Badge:** `Vertex AI Live API WebSocket (gemini-live-2.5-flash-native-audio) + gemini-3.8-flash`
- **Routing Rationale:** Real-time 16kHz->24kHz PCM Bidi Audio via gemini-live-2.5-flash-native-audio (us-central1)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: advisor_reassurance_headline, cash_to_close_buckets (list of {bucket_name, amount, color_tag, plain_english_note}), pmi_drop_schedule ({monthly_pmi, auto_drop_month, hpa_78_ltv_balance, early_redfin_avm_option}), and borrower_faq_cards (list of {question, simple_answer}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-3.8-flash` with `response_mime_type="application/json"` and validate the structured decision cards.
