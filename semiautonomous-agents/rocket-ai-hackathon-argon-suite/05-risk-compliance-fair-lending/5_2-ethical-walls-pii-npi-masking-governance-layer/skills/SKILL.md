---
name: rocket-square-5_2
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [5.2] (Ethical Walls & PII/NPI Masking Governance Layer) with bespoke UI archetype `model_armor_pii_firewall_inspector`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[5.2]` — Ethical Walls & PII/NPI Masking Governance Layer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Google Cloud Model Armor + SDP // GLBA Ethical Wall & Live PII/SSN Redaction Firewall`
- **UI Archetype Slug:** `model_armor_pii_firewall_inspector` (`layout_mode: pii_firewall_split`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#F59E0B` · Surface `#070C12`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: firewall_status, prompt_injection_blocked, redacted_entities (list of {entity_type, raw_pattern_masked, replacement_token, glba_rule}), sanitized_cross_brand_payload (str), and security_audit_log.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
