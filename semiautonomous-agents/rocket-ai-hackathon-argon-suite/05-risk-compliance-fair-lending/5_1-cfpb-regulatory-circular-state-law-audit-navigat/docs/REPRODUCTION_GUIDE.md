# Square `[5.1]`: CFPB Regulatory Circular & State Law Audit Navigator — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `5.1` |
| **Bespoke Application Title** | **Rocket Legal & NotebookLM // CFPB RESPA Section 8 & State Law Redline Vault** (`cfpb_respa_regulatory_diff_vault`) |
| **Business Domain** | 5. Risk, Compliance & Legal (CFPB, TRID, Model Armor PII Firewall & Fair Lending) (`rocket-demo-compliance`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.1](https://rocket-demo-compliance-254356041555.us-central1.run.app/?case=5.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/5.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Audit promotional campaigns, seller concessions, and Redfin/Rocket referral arrangements against CFPB RESPA Section 8, TILA Reg Z, and state lending statutes.

**Description:**  
Verify multi-state mortgage marketing promotions, Redfin Affiliated Business Arrangement (AfBA) disclosures, and state seller-concession caps with exact paragraph-level citations to CFPB circulars and state statutes.

**Bespoke UI Archetype (`cfpb_respa_regulatory_diff_vault`):**  
Rather than displaying a generic text response, Square `[5.1]` renders **Rocket Legal & NotebookLM // CFPB RESPA Section 8 & State Law Redline Vault** with structured visual artifacts (`Return JSON with keys: compliance_verdict, statutory_citations (list of {statute, section, rule_summary, violation_status}), feature_audit_rows (list of {feature_name, respa_risk_level, defect_found, mandatory_remediation}), and patched_ui_disclosure_text.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Provides auditable paragraph citations to 12 CFR Part 1024 (RESPA) and Part 1026 (TILA) so Rocket Legal can sign off on hackathon prototypes in minutes.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `NotebookLM Enterprise` · `Vertex AI Grounding` · `Gemini 4 Argon`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       5.1 CFPB REGULATORY CIRCULAR & STATE LAW NAVIGATOR (L100-200)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Marketing Promo Proposal: Redfin + Rocket $2,500 Co-Branded Credit]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [NotebookLM Enterprise / Vertex Grounding: CFPB & GSE Corpus]         │
│  ├─► 12 CFR § 1024.14 & § 1024.15 (RESPA Section 8 & AfBA Rules)       │
│  ├─► CFPB Digital Mortgage Comparison-Shopping Advisory Opinion        │
│  └─► Fannie Mae B3-4.1-02 Interested Party Contribution (IPC) Caps     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Cited Legal Sign-Off Memo + Mandatory AfBA Disclosure Language]      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Load CFPB Regulation X (12 CFR 1024), Regulation Z (12 CFR 1026), and state lending statutes into NotebookLM Enterprise / Vertex AI Search.
2. Query with `gemini-4-argon` enforcing strict statutory citation formatting.
3. Export the signed compliance checklist directly to Rocket's legal approval workflow.

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
  "archetype": "cfpb_respa_regulatory_diff_vault",
  "verdict": "CONDITIONAL PASS \u2014 Must display written AfBA Disclosure at/prior to referral + 'No Required Use' statement",
  "remediation": "Render Neutral Objective Rate-Sorted Lender Grid + Prominent Affiliates Disclosure",
  "clauses": [
    {
      "statute": "12 U.S.C. \u00a7 2607(a) (RESPA Sec 8)",
      "defect": "Default pre-checking Rocket Mortgage when sorting by 'Lowest Payment' while hiding lower APR competitor",
      "fix": "Sort strictly by objective APR/Monthly Payment math; never steer via paid placement"
    },
    {
      "statute": "12 U.S.C. \u00a7 2607(c)(4) (ABA Safe Harbor)",
      "defect": "Affiliate relationship disclosure buried in 8pt footer text",
      "fix": "Display prominent 12 CFR \u00a7 1024 Appendix D Affiliated Business Arrangement Disclosure modal prior to lead transfer"
    }
  ]
}
```
