# Personal Finance Multi-Bank MCP Server — Configuration & Architecture Design

**Owner:** Jesus Chavez (`jchavezar@gmail.com` / `jesusarguelles@google.com`)  
**Date:** October 12, 2026  
**Connected Institutions:** Bank of America (`bofa`), American Express (`amex`), SoFi (`sofi`)  
**MCP Server Name:** `personal-finance` (`~/vertex-ai-samples/semiautonomous-agents/amex-mcp`)  
**GCP Project:** `vtxdemos` (Firestore + Vertex AI `gemini-embedding-001` + Gemini 2.5 Flash)

---

## 1. Executive Summary & System Architecture

This document specifies the architecture, security controls, configuration, and operational runbook for the **Personal Finance Multi-Bank MCP Server** integrated into `jetski-cli`.

Rather than relying on brittle headless browser screen-scraping (Playwright + OTP) or corporate-gated Plaid KYB production contracts, the system uses **SimpleFIN Bridge (`beta-bridge.simplefin.org`)** backed by **MX Technologies' FDX OAuth 2.0 network** to ingest balances and transactions across **7 accounts** at **Bank of America**, **American Express**, and **SoFi**, feeding them into a 5-stage **Vertex AI Gemini + Firestore Hybrid Vector/Structured/Compute Engine**.

```text
┌──────────────────────────────────────────────────────────────────────┐
│            UNIFIED PERSONAL FINANCE MCP ARCHITECTURE                 │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 1: BANK OAUTH 2.0 (FDX Read-Only via MX Technologies)         │
│  • Bank of America (`mx.bank_of_america`):                           │
│    - Adv Relationship Banking - 4473                                 │
│    - Advantage Savings - 4499                                        │
│    - Premium Rewards Visa Signature - 8577                           │
│  • American Express (`mx.amex`):                                     │
│    - Delta SkyMiles Reserve Card - 4002                              │
│  • SoFi (`mx.78939`):                                                │
│    - Checking - 5857                                                 │
│    - Savings - 2752                                                  │
│    - Brokerage - 6725                                                │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 2: AGGREGATION BRIDGE (SimpleFIN Bridge v2 Protocol)          │
│  • Endpoint: `https://beta-bridge.simplefin.org/simplefin/accounts`  │
│  • Auth: Claimed HTTP Basic Auth URL stored at `0600` permissions    │
│    (`~/.gemini/jetski/.simplefin_access_url` & Firestore config)     │
│  • Account Security: Protected by TOTP 2FA + 7-day reset lock        │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 3: 5-STAGE GEMINI ENRICHMENT & FIRESTORE HYBRID STORAGE       │
│  • Stage 1: Gemini Categorization (16 categories, clean merchant,    │
│             tags, merchant_type, purchase_channel, purpose)          │
│  • Stage 2: Vertex AI `gemini-embedding-001` (768-dim vectors)       │
│  • Stage 3: Recurring Subscription Detection                         │
│  • Stage 4: Gmail Receipt Correlation (`gworkspace-mcp-tokens`)      │
│  • Stage 5: Firestore Storage (`vtxdemos`):                          │
│    - `bank_accounts/{account_id}` (live balances by institution)     │
│    - `amex_statements/{YYYY-MM}` (monthly rollups & AI insights)     │
│    - `amex_transactions/{YYYY-MM_NNNN}` (denormalized + KNN vectors) │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 4: JETSKI-CLI MCP SERVER (`~/.gemini/config/mcp_config.json`) │
│  • Transport: `stdio` via `uv run python mcp_server/server.py`       │
│  • Hybrid Query Engine: `smart_query` (Semantic + Filter + Math)     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Connected Accounts Inventory (Initial Sync Verified Oct 12, 2026)

| Institution Slug | Institution Name | Account Name | SimpleFIN Account ID | Type |
| :--- | :--- | :--- | :--- | :--- |
| **`bofa`** | Bank of America | `Adv Relationship Banking- 4473 (4473)` | `ACT-b359bd9b-8e5d-408c-a768-17419ce7de0c` | Checking / Debit |
| **`bofa`** | Bank of America | `Advantage Savings- 4499 (4499)` | `ACT-996ac109-c216-44f0-b1db-7b5255264135` | Savings |
| **`bofa`** | Bank of America | `Premium Rewards Visa Signature- 8577 (8577)` | `ACT-e2af2b57-efa2-4304-8ea1-1efbb4dca71c` | Credit Card |
| **`amex`** | American Express | `Delta SkyMiles® Reserve Card (4002)` | `ACT-3544d76a-073e-4d84-a13a-0b0e4109f425` | Credit Card |
| **`sofi`** | SoFi | `Checking - 5857 (5857)` | `ACT-149abb6f-d108-4a26-b275-e094723d2a8a` | Checking / Debit |
| **`sofi`** | SoFi | `Savings - 2752 (2752)` | `ACT-a984874d-ba0d-4ce1-8660-a8d5fd0d81de` | Savings |
| **`sofi`** | SoFi | `Brokerage (6725)` | `ACT-4a3aea68-925c-474a-b527-79fb3d609edf` | Investment / Brokerage |

---

## 3. Configuration Files & File Paths

### 3.1 Global `jetski-cli` MCP Config
**File:** `~/.gemini/config/mcp_config.json`

```json
{
  "mcpServers": {
    "personal-finance": {
      "command": "/usr/local/google/home/jesusarguelles/.local/bin/uv",
      "args": [
        "run",
        "--directory",
        "/usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/amex-mcp",
        "python",
        "mcp_server/server.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GCP_PROJECT_ID": "vtxdemos"
      }
    }
  }
}
```

### 3.2 Repository Structure (`~/vertex-ai-samples/semiautonomous-agents/amex-mcp`)
* `amex_job/simplefin.py`: SimpleFIN Bridge v2 client (`claim_setup_token`, `fetch_simplefin_data`, `sync_simplefin_to_firestore`, `get_cached_balances`). Maps `conn_id` from `connections` to tag every transaction and account with `institution` (`bofa`, `amex`, `sofi`).
* `mcp_server/tools/simplefin_tools.py`: Exposes `simplefin_claim_token`, `simplefin_sync`, and `get_bank_balances`.
* `mcp_server/tools/search.py`: Exposes `smart_query` with support for filtering and grouping by `institution` (`bofa`, `amex`, `sofi`), `account_name`, `card_member`, `enriched_category`, `subcategory`, `merchant_clean`, `purpose`, `purchase_channel`, and `date`.
* `amex_job/storage.py`: Manages Firestore collections `bank_accounts`, `amex_statements`, `amex_transactions` (with 768-dim `gemini-embedding-001` vectors), and `finance_config/simplefin`.

### 3.3 Credential & Token Storage Locations
1. **Local Restricted File (`0600` permissions):** `~/.gemini/jetski/.simplefin_access_url`
2. **Firestore Backup Document:** `projects/vtxdemos/databases/(default)/documents/finance_config/simplefin`
3. **Gmail Receipt Matcher OAuth Token:** GCP Secret Manager secret `gworkspace-mcp-tokens` in project `vtxdemos` (`jchavezar@gmail.com`).

---

## 4. Available MCP Tools & Example Prompts in `jetski-cli`

| Tool Name | Purpose | Key Parameters |
| :--- | :--- | :--- |
| **`get_bank_balances`** | View live or cached balances across all 7 BofA, Amex, and SoFi accounts | `refresh: bool = False` |
| **`simplefin_sync`** | Pull latest transactions & balances from SimpleFIN and run Gemini enrichment | `days: int = 30, enrich: bool = True` |
| **`smart_query`** | Hybrid semantic vector + structured Firestore filter + deterministic Python math | `query, filters, group_by, aggregate, limit` |
| **`get_spending_by_category`** | Category breakdown for a given `year` and `month` | `year: int, month: int` |
| **`get_category_trends`** | Multi-month spending trend across categories | `months: int = 6` |
| **`get_top_merchants`** | Top merchants by total spend or visit count | `year: int, month: int` |
| **`get_subscriptions`** | Recurring monthly charges detected across accounts | *(none)* |
| **`get_spending_insights`** | AI narrative + anomalies + spending score | `year: int, month: int` |
| **`get_recommendations`** | Personalized savings tips from Gemini | *(none)* |
| **`ingest_amex_csv`** | Manual CSV fallback ingestion | `csv_content: str, period: str` |
| **`simplefin_claim_token`** | One-time exchange of a SimpleFIN Base64 Setup Token | `setup_token: str, sync_days: int = 60` |

### Example `smart_query` Calls
```python
# 1. Total spend grouped by bank (bofa, amex, sofi) in September 2026
smart_query(filters='{"period":"2026-09"}', group_by="institution", aggregate="sum")

# 2. Semantic search for coffee shops across all 3 banks
smart_query(query="coffee shops", filters='{"date_after":"2026-08-01"}', aggregate="sum")

# 3. Filter specifically to Bank of America or Amex transactions
smart_query(filters='{"institution":"bofa","period":"2026-10"}', group_by="enriched_category", aggregate="sum")
```

---

## 5. Security Controls & Emergency Kill-Switch Runbook

### 5.1 Active Security Protections
* **Read-Only API Architecture:** SimpleFIN only exposes `/accounts` (`GET`) for balances and transactions; it has no money-movement, wire, Zelle, or ACH initiation endpoints.
* **2FA Step-Up Lock:** `jchavezar@gmail.com` on `beta-bridge.simplefin.org` has TOTP Two-Factor Authentication enabled with a mandatory **7-day hardware reset waiting period** before 2FA can be disabled. Minting any new App Setup Token requires a live 6-digit TOTP code.
* **IP Subnet Audit Log:** SimpleFIN logs every IPv4/IPv6 subnet that accesses the token under **My Account $\rightarrow$ Access Log**.

### 5.2 Three-Layer Emergency Kill Switches (How to Cut Access Instantly)
1. **Kill Switch 1 — Bank-Side OAuth Revocation (Immediate `401 Unauthorized` at the Bank):**
   * **Bank of America:** Log in $\rightarrow$ **Security Center** $\rightarrow$ **Third-Party Access / Data Sharing** $\rightarrow$ click **Revoke** next to **SimpleFIN (via MX Technologies)**.
   * **American Express:** Log in $\rightarrow$ **Account Services** $\rightarrow$ **Security & Privacy** $\rightarrow$ **Manage Third-Party Access / Connected Apps** $\rightarrow$ Remove **MX**.
   * **SoFi:** Log in $\rightarrow$ **Profile** $\rightarrow$ **Settings** $\rightarrow$ **Security & Privacy / Connected Apps** $\rightarrow$ Revoke access.
2. **Kill Switch 2 — SimpleFIN Dashboard (`https://beta-bridge.simplefin.org/my-account`):**
   * Under **Apps**, click **Revoke** next to `jetski-mcp` to kill the local token instantly.
   * Under **Financial Institutions**, click **Delete** next to `Bank of America`, `American Express`, or `SoFi` to sever the MX connection.
3. **Kill Switch 3 — Local Machine / GCP:**
   * Delete `~/.gemini/jetski/.simplefin_access_url` and Firestore document `finance_config/simplefin`.
