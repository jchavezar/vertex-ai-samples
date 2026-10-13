# Square `[1.3]`: No-Code Mortgage Guideline & Competitor Battlecard Agent — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `1.3` |
| **Bespoke Application Title** | **Gemini Enterprise (Sobi / Spark) // GSE Guideline & Competitor Battlecard Hub** (`gemini_enterprise_streamassist_hub`) |
| **Business Domain** | 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-demo-origination-254356041555.us-central1.run.app/?case=1.3](https://rocket-demo-origination-254356041555.us-central1.run.app/?case=1.3) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.3](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.3) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Grounded Gemini Enterprise workplace agent integrated with Microsoft Teams to answer FHA/VA/Conventional guidelines & UWM/Pennymac battlecards.

**Description:**  
Answer complex banker eligibility scenarios (e.g., 640 FICO with 5% down, non-occupant co-borrower, recent student loan IBR) in seconds with exact credit matrix overlays, reserve rules, and live competitive counter-points.

**Bespoke UI Archetype (`gemini_enterprise_streamassist_hub`):**  
Rather than displaying a generic text response, Square `[1.3]` renders **Gemini Enterprise (Sobi / Spark) // GSE Guideline & Competitor Battlecard Hub** with structured visual artifacts (`Return JSON with keys: winning_recommendation, monthly_savings_vs_broker, program_matrix (list of 3 programs {program, min_fico, down_pct, monthly_pi, monthly_mi, total_payment, llpa_impact}), and banker_objection_script (list of {broker_claim, rocket_counter}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Queries Rocket's SharePoint & Fannie/Freddie PDFs in-place via Sobi 3-object MCP Registry (`McpServer`, `AuthProvider`, `AuthBinding`) with full ACL inheritance—zero AWS S3 data duplication.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Enterprise (global-gemini-enterprise)` · `SharePoint / OneDrive 3LO Connector` · `Gemini 4 Argon`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       1.3 GEMINI ENTERPRISE GUIDELINE & BATTLECARD AGENT (L100-200)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Microsoft Teams / Gemini Enterprise Web (/work/cid/<CID>)]           │
│  • Banker asks eligibility + competitor battlecard question            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Enterprise Sobi Runtime + Agent Registry]                     │
│  ├─► McpServer: SharePoint Product Matrix & Selling Guides             │
│  ├─► AuthProvider & AuthBinding: 3LO Entra ID / O365 ACL Enforcement   │
│  └─► Model: gemini-4-argon with Paragraph-Level Grounding Citations    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Grounded Matrix Comparison + FHA vs Conv Math + Winning Battlecard]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. In Google Cloud Console -> Gemini Enterprise (`collections/default_collection/engines/global-gemini-enterprise`), connect your SharePoint Online or Cloud Storage datastore containing Rocket Product Matrices & Fannie/Freddie Guides.
2. Create a No-Code Custom Agent in Gemini Enterprise Agent Studio with system instructions enforcing citation tags and FHA vs. Conventional payment comparisons.
3. Publish the agent to Microsoft Teams via the Gemini Enterprise M365 extension binding.

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
  "archetype": "gemini_enterprise_streamassist_hub",
  "winner_banner": "FHA 3.5% Down (or HomeReady if Census Tract <= 80% AMI)",
  "battlecard_rows": [
    {
      "metric": "Guideline Citation",
      "broker_conv": "Fannie Mae B3-5.1-01 (Std Conv)",
      "homeready": "Fannie Mae B5-6-01 (HomeReady)",
      "fha": "HUD Handbook 4000.1 II.A.4"
    },
    {
      "metric": "Credit Score Impact (642 FICO)",
      "broker_conv": "-1.75% LLPA Penalty Hit",
      "homeready": "100% LLPA Waived (<=80% AMI)",
      "fha": "No Credit-Tiered LLPA"
    },
    {
      "metric": "Monthly Mortgage Insurance",
      "broker_conv": "$406.12/mo (1.35% Charter MI)",
      "homeready": "$234.65/mo (Reduced 25% Cov)",
      "fha": "$168.07/mo (0.55% Annual MIP)"
    },
    {
      "metric": "Total P&I + MI Payment",
      "broker_conv": "P&I $2,311.52 + Private MI $406.12 = $2,717.64/mo (Heavy 642 FICO LLPA)",
      "homeready": "P&I $2,193.47 + Reduced MI $234.65 = $2,428.12/mo (LLPA Waived if <=80% AMI)",
      "fha": "P&I $2,207.13 + FHA MIP $168.07 = $2,375.20/mo (Lowest Monthly Payment by $286/mo!)"
    },
    {
      "metric": "Aunt's $8,000 Gift Funds",
      "broker_conv": "Allowed (B3-4.3-04)",
      "homeready": "Allowed (100% Gift OK)",
      "fha": "Allowed w/ Donor Bank Stmt"
    }
  ]
}
```
