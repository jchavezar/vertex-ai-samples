---
name: rocket-square-6_3
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [6.3] (Legacy .NET Framework / WCF to Cloud Run Microservice Modernizer) with bespoke UI archetype `legacy_dotnet_wcf_transpiler`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[6.3]` — Legacy .NET Framework / WCF to Cloud Run Microservice Modernizer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Antigravity Legacy Modernizer // C# .NET 4.8 WCF SOAP -> .NET 9 Cloud Run Transpiler`
- **UI Archetype Slug:** `legacy_dotnet_wcf_transpiler` (`layout_mode: side_by_side_transpiler`)
- **Color Palette:** Primary Accent `#38BDF8` · Secondary Accent `#22C55E` · Surface `#050912`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: modernization_metrics ({cold_start_ms, memory_reduction_pct, sql_injection_fixed}), legacy_issues_removed (list of {anti_pattern, legacy_snippet, modern_fix}), modern_csharp_code (str), and michigan_millage_parity_table (list of {scenario, taxable_value, mills, annual_tax, monthly_escrow}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
