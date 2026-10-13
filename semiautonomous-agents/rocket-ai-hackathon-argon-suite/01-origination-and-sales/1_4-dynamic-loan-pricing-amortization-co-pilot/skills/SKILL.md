---
name: rocket-square-1_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [1.4] (Dynamic Loan Pricing & Amortization Co-Pilot) with bespoke UI archetype `monark_wealth_vault_simulator`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[1.4]` — Dynamic Loan Pricing & Amortization Co-Pilot

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Monark™ x Rocket Money // Down-Payment Vault & LTV Pricing Simulator`
- **UI Archetype Slug:** `monark_wealth_vault_simulator` (`layout_mode: monark_financial_os`)
- **Color Palette:** Primary Accent `#10B981` · Secondary Accent `#F59E0B` · Surface `#06100E`
- **Interactive Controls:** `[{"id": "price", "label": "Home Price ($)", "type": "range", "min": 300000, "max": 850000, "step": 10000, "default": 540000}]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: net_worth_impact, rocket_money_accounts (list of {account_name,institution,balance,allocation_action}), ltv_comparison (list of {tier, loan_amount, rate, monthly_pi, monthly_pmi, total_piti}), and five_year_wealth_projection ({interest_saved, pmi_saved, net_equity_yr5}).
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
