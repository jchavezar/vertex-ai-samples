---
name: rocket-square-5_5
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [5.5] (Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)) with bespoke UI archetype `ecoa_fair_lending_twin_certifier`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[5.5]` — Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `ECOA Regulation B // 500-Counterfactual Twin Fair Lending & Adverse Action Certifier`
- **UI Archetype Slug:** `ecoa_fair_lending_twin_certifier` (`layout_mode: fair_lending_gauges`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#6366F1` · Surface `#070B14`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: certification_badge, disparate_impact_metrics ({approval_parity_ratio, eeoc_four_fifths_threshold, fee_waiver_variance_bps, prohibited_factors_detected}), counterfactual_cohort_table (list of {cohort_pair, identical_financials, approval_rate_a, approval_rate_b, parity_ratio}), and reg_b_compliance_attestation.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
