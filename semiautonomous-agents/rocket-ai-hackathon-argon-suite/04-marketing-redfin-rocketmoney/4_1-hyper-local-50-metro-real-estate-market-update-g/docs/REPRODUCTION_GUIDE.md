# Square `[4.1]`: Hyper-Local 50-Metro Real Estate Market Update Generator — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `4.1` |
| **Bespoke Application Title** | **Redfin x Rocket // 50-Metro Real Estate Inventory, Price-Drop & Rate Pulse Grid** (`metro_50_market_pulse_heatmap`) |
| **Business Domain** | 4. Marketing, Growth & Client Acquisition (Redfin, Rocket Money & DTC Funnel) (`rocket-demo-marketing`) |
| **Complexity Level** | `L100–L200` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-marketing-254356041555.us-central1.run.app/?case=4.1](https://rocket-demo-marketing-254356041555.us-central1.run.app/?case=4.1) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.1](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.1) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Ingest live Redfin MLS metro data (median price, DOM, inventory, rate locks) to generate hyper-local newsletters, Redfin blog posts, and social hooks.

**Description:**  
Turn raw Redfin MLS market telemetry across 50 US metros into localized buyer/seller intelligence reports, neighborhood affordability breakdowns, and high-converting email campaigns in seconds.

**Bespoke UI Archetype (`metro_50_market_pulse_heatmap`):**  
Rather than displaying a generic text response, Square `[4.1]` renders **Redfin x Rocket // 50-Metro Real Estate Inventory, Price-Drop & Rate Pulse Grid** with structured visual artifacts (`Return JSON with keys: national_headline, metro_cards (list of 4 metros {metro_name, median_price, yoy_change, active_inventory_delta, seller_concession_pct, buying_power_headline, local_ad_hook}), and seo_newsletter_blurb.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Processes all 50 US metro MLS tables in a single 2M-token Gemini 4 Argon context window with Context Caching, cutting per-campaign generation costs by 78% vs OpenAI/Anthropic.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Google AI Studio` · `Gemini 4 Argon` · `BigQuery Redfin MLS Feed`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       4.1 HYPER-LOCAL 50-METRO MARKET UPDATE GENERATOR (L100-200)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Redfin MLS Metro Telemetry + Rocket Money Renter Cohort Data]        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon + Rent-vs-Buy Equity Accretion Calculator]            │
│  • Tailors strategy by metro (Detroit competitive vs Austin buydown)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Localized Email HTML + Redfin Blog Post + Paid Social Ad Copy]       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Prototype your multi-metro system prompt in Google AI Studio using system instructions and structured variables (`{{METRO}}`, `{{MEDIAN_PRICE}}`, `{{DOM}}`).
2. Click 'Get Code' in AI Studio to export the Python `google-genai` snippet running on `gemini-4-argon`.
3. Connect to BigQuery Redfin MLS tables to batch-generate all 50 metro campaigns automatically.

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
  "archetype": "metro_50_market_pulse_heatmap",
  "metros": [
    {
      "city": "Detroit-Warren-Dearborn, MI",
      "median": "$268,000",
      "inv": "+14.2% YoY",
      "concessions": "38% of Listings",
      "hook": "Lock 5.875% w/ Seller-Paid 2-1 Buydown on Royal Oak & Ferndale Craftsmans"
    },
    {
      "city": "Austin-Round Rock, TX",
      "median": "$445,000",
      "inv": "+22.8% YoY",
      "concessions": "54% of Listings",
      "hook": "Buyers Rule Austin: Average $12,400 Seller Credit Covers Full Rocket Rate Buydown"
    },
    {
      "city": "Charlotte-Concord, NC",
      "median": "$392,000",
      "inv": "+11.5% YoY",
      "concessions": "41% of Listings",
      "hook": "Move Up in South End with $0 Appraisal Waiver for Mr. Cooper Homeowners"
    },
    {
      "city": "Phoenix-Mesa-Chandler, AZ",
      "median": "$438,000",
      "inv": "+19.4% YoY",
      "concessions": "49% of Listings",
      "hook": "Beat Arizona Rent: $0 Down VA & 3% Down Rocket HomeReady Options"
    }
  ]
}
```
