---
name: rocket-square-5_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [5.3] (Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)) with bespoke UI archetype `trid_le_cd_tolerance_grid`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[5.3]` — Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor`
- **UI Archetype Slug:** `trid_le_cd_tolerance_grid` (`layout_mode: trid_audit_table`)
- **Color Palette:** Primary Accent `#F59E0B` · Secondary Accent `#10B981` · Surface `#0A0D14`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: total_lender_cure_credit, closing_timer_status, fee_comparison_rows (list of {fee_name, trid_bucket, le_disclosed, cd_actual, variance, cure_required, citation}), and section_j_journal_entry.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
