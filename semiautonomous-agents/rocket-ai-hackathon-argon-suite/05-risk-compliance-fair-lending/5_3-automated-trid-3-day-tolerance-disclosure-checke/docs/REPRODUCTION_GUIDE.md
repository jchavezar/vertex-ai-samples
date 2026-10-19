# Square `[5.3]`: Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD) — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `5.3` |
| **Bespoke Application Title** | **CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor** (`trid_le_cd_tolerance_grid`) |
| **Business Domain** | 5. Risk, Compliance & Legal (CFPB, TRID, Model Armor PII Firewall & Fair Lending) (`rocket-demo-compliance`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/5.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/5.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Compare initial Loan Estimates (LE) against final Closing Disclosures (CD) across 0% and 10% CFPB TRID fee buckets and calculate exact Principal Reduction / Lender Cure credits.

**Description:**  
Eliminate manual pre-closing TRID audits: extract fee tables from the initial Loan Estimate and final Closing Disclosure, audit Zero-Tolerance (0%) and Cumulative 10% Tolerance buckets under 12 CFR § 1026.19(e)(3), and compute the exact dollar cure required prior to closing.

**Bespoke UI Archetype (`trid_le_cd_tolerance_grid`):**  
Rather than displaying a generic text response, Square `[5.3]` renders **CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor** with structured visual artifacts (`Return JSON with keys: total_lender_cure_credit, closing_timer_status, fee_comparison_rows (list of {fee_name, trid_bucket, le_disclosed, cd_actual, variance, cure_required, citation}), and section_j_journal_entry.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Catches 100% of 0%-bucket and 10%-cumulative-bucket TRID violations before closing package dispatch, eliminating post-close investors buybacks and CFPB examination findings.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Document AI Loan Estimate & Closing Disclosure Parsers` · `Gemini 4 Argon` · `Deterministic TRID Tolerance Sandbox`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      5.3 AUTOMATED TRID 3-DAY TOLERANCE & LE-VS-CD CHECKER (L200-300)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Document AI Parsers: Initial Loan Estimate (LE) + Final CD]          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [12 CFR § 1026.19(e)(3) TRID Tolerance Sandbox + Gemini 4 Argon]      │
│  ├─► 0% Bucket:  LE $1,985 vs CD $2,185 -> $200.00 Breach!             │
│  ├─► 10% Bucket: LE $1,800 (Cap $1,980) vs CD $2,110 -> $130.00 Breach!│
│  └─► Total Required Lender Tolerance Cure (Section J): $330.00         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Auto-Generated CD Cure Addendum + 3-Day Re-Disclosure Check]         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Extract fee tables from the initial Loan Estimate and final Closing Disclosure using Google Cloud Document AI (`MORTGAGE_LOAN_ESTIMATE_PROCESSOR` and `MORTGAGE_CLOSING_DISCLOSURE_PROCESSOR`).
2. Run the deterministic Python TRID bucket auditor comparing 0% individual fees and 10% cumulative aggregate fees.
3. Have `gemini-4-argon` generate the Section J Tolerance Cure adjustment and audit memo.

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
  "archetype": "trid_le_cd_tolerance_grid",
  "total_cure": "$330.00 Lender Tolerance Credit Required on CD Page 2 Section J Prior to Closing",
  "rows": [
    {
      "fee": "Origination / Underwriting Fee",
      "bucket": "0% Zero Tolerance",
      "le": "$1,295.00",
      "cd": "$1,295.00",
      "diff": "$0.00",
      "cure": "$0.00 (PASS)"
    },
    {
      "fee": "Appraisal Rush Fee (Unapproved)",
      "bucket": "0% Zero Tolerance",
      "le": "$550.00",
      "cd": "$800.00",
      "diff": "+$250.00",
      "cure": "\ud83d\udea9 $250.00 CURE (No Valid COC)"
    },
    {
      "fee": "County Recording + Transfer Fees",
      "bucket": "10% Cumulative Bucket",
      "le": "$650.00",
      "cd": "$950.00",
      "diff": "+$300.00 (+46.1%)",
      "cure": "\ud83d\udea9 $235.00 CURE (Exceeds $65 Cap)"
    },
    {
      "fee": "Borrower-Shopped Pest Inspection",
      "bucket": "Unlimited (Borrower Shopped)",
      "le": "$125.00",
      "cd": "$160.00",
      "diff": "+$35.00",
      "cure": "$0.00 (Exempt Bucket)"
    }
  ]
}
```
