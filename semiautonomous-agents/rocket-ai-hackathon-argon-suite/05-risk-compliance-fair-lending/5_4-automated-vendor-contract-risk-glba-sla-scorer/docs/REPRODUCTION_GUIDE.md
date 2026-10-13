# Square `[5.4]`: Automated Vendor Contract Risk & GLBA SLA Scorer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `5.4` |
| **Bespoke Application Title** | **Rocket Procurement & Legal // Third-Party Vendor MSA & GLBA Safeguards Redliner** (`vendor_glba_contract_redliner`) |
| **Business Domain** | 5. Risk, Compliance & Legal (CFPB, TRID, Model Armor PII Firewall & Fair Lending) (`rocket-demo-compliance`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.4](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Parse third-party vendor MSAs and SaaS agreements into a deterministic JSON risk matrix scored against Rocket's GLBA/FFIEC security policy.

**Description:**  
Ingest 80-page vendor Master Services Agreements (MSAs) and Information Security Addendums, returning a strict JSON risk matrix scoring Indemnification Caps, GLBA/NYDFS 24-Hour Breach Notification Windows, AI Training Opt-Outs, and Multi-Cloud Exit SLAs.

**Bespoke UI Archetype (`vendor_glba_contract_redliner`):**  
Rather than displaying a generic text response, Square `[5.4]` renders **Rocket Procurement & Legal // Third-Party Vendor MSA & GLBA Safeguards Redliner** with structured visual artifacts (`Return JSON with keys: vendor_risk_rating, clause_redlines (list of {section, vendor_original_text, policy_violation, rocket_replacement_clause}), and ciso_signoff_checklist.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Audits entire 150-page MSAs + SOC2 reports in one shot with strict JSON schema output and redline replacement clauses.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon (2M Context + response_schema)` · `Pydantic Risk Matrix` · `Cloud Run Legal API`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       5.4 AUTOMATED VENDOR CONTRACT RISK & SLA SCORER (L300 JSON)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Vendor MSA PDF + Rocket GLBA / FFIEC Security Policy Baseline]       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon Structured JSON Evaluator (response_schema)]          │
│  ├─► Sec 8.2: 3-Mo Cap ($45k) vs $5M GLBA Super-Cap -> CRITICAL        │
│  ├─► Sec 11.4: 72-Hr Notice vs 24-Hr NYDFS/GLBA Rule -> HIGH RISK      │
│  └─► Sec 14.1: AI Model Training Allowed -> CRITICAL BLOCKER           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Strict JSON Risk Matrix + Ready-to-Insert Legal Redline Clauses]     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Define a Pydantic schema `VendorContractRiskAudit` with typed fields for `overall_risk_score`, `blocking_violations`, and `redline_replacements`.
2. Pass the full vendor MSA PDF + Rocket TPRM Policy into `gemini-4-argon` with `response_schema=VendorContractRiskAudit`.
3. Route contracts with `overall_risk_score >= 75` to Senior Procurement Counsel with pre-drafted redlines.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-3.8-flash structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "vendor_glba_contract_redliner",
  "risk_score": "HIGH RISK (3 Critical GLBA / OCC Deficiencies Caught)",
  "redlines": [
    {
      "clause": "\u00a7 4.2 AI Model Training Rights",
      "vendor_text": "Vendor may use anonymized Customer mortgage documents to train foundation models.",
      "rocket_fix": "STRIKE & REPLACE: Strict Zero-Retention & Zero-Training Covenant under GLBA 16 CFR Part 314."
    },
    {
      "clause": "\u00a7 7.1 Breach Notification SLA",
      "vendor_text": "Vendor shall notify Rocket within 10 business days of a confirmed breach.",
      "rocket_fix": "STRIKE & REPLACE: Mandatory < 24-Hour Incident Notification per OCC/CFPB & NYDFS 23 NYCRR 500."
    },
    {
      "clause": "\u00a7 9.3 Sub-Processor Residency",
      "vendor_text": "Vendor may utilize global offshore sub-processors upon 30 days notice.",
      "rocket_fix": "STRIKE & REPLACE: Strict US-Only (`us-central1` / `us-east4`) Sovereign Data Residency & Prior Written CISO Consent."
    }
  ]
}
```
