# Square `[1.2]`: Outlook Hyper-Personalized Rate-Lock & Pre-Approval Agent — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `1.2` |
| **Bespoke Application Title** | **Microsoft Outlook 365 // Rocket Verified Approval & Rate-Lock Add-In** (`outlook_addin_composer`) |
| **Business Domain** | 1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO) (`rocket-demo-origination`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/1.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/1.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Compile personalized Rocket Verified Approval letters & Excel closing-cost tables directly inside an O365 Outlook compose workflow.

**Description:**  
Generate a tailored Rocket Mortgage Verified Approval Letter and 3-option Rate-Lock comparison table inside an Outlook-style compose window referencing the exact Redfin property address, seller agent, and local Oakland County millage taxes.

**Bespoke UI Archetype (`outlook_addin_composer`):**  
Rather than displaying a generic text response, Square `[1.2]` renders **Microsoft Outlook 365 // Rocket Verified Approval & Rate-Lock Add-In** with structured visual artifacts (`Return JSON with keys: email_headers ({to, cc, subject}), rate_options_table (list of 3 options with {option_name, rate, monthly_pi, upfront_cost, breakeven_months, badge}), verified_approval_certificate ({cert_id, max_price, property_address, expiration}), and email_body_paragraphs (list of strings).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Outperforms Microsoft 365 Copilot in Outlook by pulling live Rocket pricing engine tiers and computing exact county transfer taxes without hallucinating fee buckets.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini 4 Argon` · `Gemini Code Assist` · `Microsoft Graph / Outlook MCP`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      1.2 OUTLOOK RATE-LOCK & PRE-APPROVAL AGENT (L100-L200)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [O365 Outlook Add-In / Compose Pane]                                  │
│  • Property Address, Listing Agent, Loan Amount, 3 Rate Options        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Sandboxed Breakeven & PITI Engine + Gemini 4 Argon]                  │
│  • Computes exact P&I, Buydown Cost, Monthly Savings, Breakeven Month  │
│  • Generates Seller-Facing Verified Approval + Buyer Comparison Grid   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Outlook Rich HTML Email + Copy-Paste Excel Table]                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Use Gemini Code Assist in VS Code or Antigravity IDE to scaffold the O365 Outlook Web Add-in manifest (`manifest.xml`) and FastAPI backend.
2. Connect the backend to `gemini-4-argon` on Vertex AI to synthesize both the Listing Agent Verified Approval certificate and the Borrower 3-Scenario Comparison Table.
3. Run the sandboxed amortization calculator so breakeven months (Upfront Points Cost / Monthly P&I Savings) are exact.

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
  "archetype": "outlook_addin_composer",
  "email_to": "Marcus & Elena Vance <mvance@ford.com>; Sarah Jenkins (Redfin Premier Agent) <sjenkins@redfin.com>",
  "email_subject": "\u2705 Rocket Mortgage Verified Approval ($460,000) + 3 Custom Rate-Lock Options \u2014 1420 Vinsetta Blvd",
  "certificate_id": "RKT-VA-994021-MI",
  "rate_matrix": [
    {
      "tier": "Option A \u00b7 30Y Par Lock",
      "rate": "6.125%",
      "pi": "$3,038.05/mo @ 6.125% ($0 Points)",
      "upfront": "$0 Points",
      "breakeven": "Immediate (0 Mos)",
      "badge": "Zero Points"
    },
    {
      "tier": "Option B \u00b7 Permanent Buydown",
      "rate": "5.875%",
      "pi": "$2,957.69/mo @ 5.875% (Cost: $3,750.00 | Saves $80.36/mo)",
      "upfront": "$3,750 (0.75 Pts)",
      "breakeven": "46.7 Months (3.9 Years)",
      "badge": "Best Long-Term"
    },
    {
      "tier": "Option C \u00b7 Seller-Paid 2-1 Buydown",
      "rate": "4.125% Yr1 / 5.125% Yr2",
      "pi": "Yr 1: $2,423.25/mo (4.125%) | Yr 2: $2,722.43/mo (5.125%) | Seller Subsidy: $11,165.04",
      "upfront": "$11,245 Seller Credit",
      "breakeven": "$0 Buyer Cost",
      "badge": "\u2b50 Recommended Offer Strategy"
    }
  ]
}
```
