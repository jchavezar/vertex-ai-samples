# Square `[1.1]`: The ABCDQ Post-Call Structured Debriefer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `1.1` |
| **Bespoke Application Title** | **Rocket Logic // Form 1003 Pre-Qual & CRM Intake Cockpit** (`1003_intake_cockpit`) |
| **Business Domain** | 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`) |
| **Complexity Level** | `L100` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Persona-Task-Context-Format prompting to turn messy banker intake notes into DTI/LTV calculations, CRM JSON, and Outlook follow-ups.

**Description:**  
Paste messy intake call shorthand from a first-time Detroit/Oakland County homebuyer into Gemini 4 Argon. Instantly outputs a structured 1003 pre-qualification summary (DTI, LTV, qualifying income, reserve check), a Salesforce CRM payload, and an empathetic borrower action checklist.

**Bespoke UI Archetype (`1003_intake_cockpit`):**  
Rather than displaying a generic text response, Square `[1.1]` renders **Rocket Logic // Form 1003 Pre-Qual & CRM Intake Cockpit** with structured visual artifacts (`Return JSON with keys: executive_verdict, borrower_profile (name, fico, target_property), income_breakdown ( list of {source, monthly_amount, rule_note} ), dti_gauges ({front_dti, back_dti, max_allowed, status}), salesforce_payload (dict), and outlook_email_html (str).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Beats ChatGPT Enterprise & Bedrock Claude by combining deterministic mortgage math verification with zero-retention GCP data governance.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon (gemini-4-argon)` · `Gemini Enterprise Prompt Canvas` · `Cloud Run`

```text
┌────────────────────────────────────────────────────────────────────────┐
│           1.1 ABCDQ POST-CALL STRUCTURED DEBRIEFER (L100)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Banker Intake Notes / Rocket Logic Synopsis Transcript]              │
│  • Raw shorthand: Income, FICO, Redfin Address, Rocket Money Vault     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Enterprise / Vertex AI: gemini-4-argon (Global Endpoint)]     │
│  • Persona-Task-Context-Format System Guardrail                        │
│  • Sandboxed DTI / LTV / PITI + PMI Verification Engine                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [3 Standardized Deliverables]                                         │
│  ├─► 1. 1003 Pre-Qual Summary (Front/Back DTI, Reserve Sufficiency)    │
│  ├─► 2. Salesforce / Encompass LOS Structured JSON Payload             │
│  └─► 3. O365 Outlook Ready-to-Send Borrower Follow-Up & Checklist      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Enable Vertex AI API in your GCP project: `gcloud services enable aiplatform.googleapis.com run.googleapis.com --project=vtxdemos`
2. Call the global `gemini-4-argon` endpoint using `google-genai` SDK with the Persona-Task-Context-Format system instruction.
3. Attach the Python DTI/LTV calculation verifier tool so all dollar figures (P&I, PMI, Taxes, Front/Back DTI) are 100% mathematically verified before rendering the Outlook draft.
4. Deploy the banker frontend to Cloud Run with `--no-allow-unauthenticated` or basic auth middleware.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-4-argon structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "1003_intake_cockpit",
  "borrower": "Marcus & Elena Vance (Royal Oak, MI 48067)",
  "fico_pair": "748 / 762 (Middle FICO: 748)",
  "target_property": "1420 Vinsetta Blvd, Royal Oak, MI \u2014 $460,000 (Redfin MLS #20261892)",
  "front_dti": 19.65,
  "back_dti": 23.79,
  "max_dti": 45.0,
  "income_rows": [
    {
      "source": "Marcus Base Salary (Ford Motor Co \u2014 Sr. Mech Eng)",
      "monthly": "$9,833.33",
      "rule": "100% Base Allowed (VOE Confirmed)"
    },
    {
      "source": "Elena Base Salary (Corewell Health \u2014 RN)",
      "monthly": "$7,166.67",
      "rule": "100% Base Allowed (VOE Confirmed)"
    },
    {
      "source": "Marcus 24-Mo Avg Annual Bonus ($14k/yr)",
      "monthly": "$1,166.67",
      "rule": "Fannie Mae B3-3.1-01 2-Yr Average"
    },
    {
      "source": "Elena 24-Mo Avg RN Overtime ($9.5k/yr)",
      "monthly": "$791.67",
      "rule": "Fannie Mae B3-3.1-01 2-Yr Average"
    }
  ],
  "total_qualifying_income": "$18,958.33/mo (Base $17,000 + 24m Avg Bonus/OT $1,958)",
  "monthly_piti_breakdown": "$3,347.44/mo (P&I $2,515.51 + Tax $555.83 + Ins $145.00 + PMI $131.10)",
  "crm_json": {
    "lead_id": "RKT-1003-2026-88412",
    "aus_recommendation": "DU APPROVE / ELIGIBLE",
    "loan_program": "30-Yr Fixed Conventional 90% LTV",
    "rocket_money_vault_verified": "$52,000.00 (Chase + Ally Linked)",
    "post_close_reserves_months": "6.4 Months PITI"
  }
}
```
