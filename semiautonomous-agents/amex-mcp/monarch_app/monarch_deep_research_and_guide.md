# Monarch Money Deep Research & Sovereign Finance OS Architecture Guide

**Owner:** Jesus Chavez (`jesusarguelles@google.com` / `jchavezar@gmail.com`)  
**Application Artifact:** [monarch_finance_app.html](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/e16782b8-3b7e-4494-9cdf-d8aad8636e0f/monarch_finance_app.html)  
**Backend & Data Engine:** [monarch_app/](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/amex-mcp/monarch_app) (`FastAPI` + `SimpleFIN Bridge` + `Firestore vtxdemos`)  
**Design System:** Vercel Monochrome Architecture (`Light Mode` default + Dynamic `☀️/🌙` Toggle + Claude-Code Shrinking & Shining Ink Loader)

---

## 1. Exhaustive Research: Monarch Money + Copilot + Lunch Money Feature Matrix

We investigated every core module across **Monarch Money**, **Copilot Money**, and **Lunch Money**, and engineered a super-set implementation tailored to your 7 connected accounts (**Bank of America**, **American Express**, **SoFi**) and **978 live transactions** (`Jul – Oct 2026`).

```text
┌──────────────────────────────────────────────────────────────────────┐
│           SOVEREIGN // MONARCH FINANCE OS ARCHITECTURE               │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 1: MULTI-BANK SIMPLEFIN FDX INGESTION & FIRESTORE (`vtxdemos`)│
│  • 7 Live Accounts ($66,705.52 Assets / -$33,451.41 Card Float)      │
│  • 978 Full-History Transactions (Jul, Aug, Sep, Oct 2026)           │
│  • Live `POST /api/sync` endpoint for on-demand 90-day refresh       │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 2: REFUND PAIRING & CLASSIFICATION ENGINE (`data_engine.py`)  │
│  • Pairs 54 Merchant Returns (-$8,238.73 in 90D / -$4,575.69 in 60D) │
│  • Strips 100% refunded charges ($1,075.84 Vividstorm, $230 Nike)    │
│  • Deducts partial returns (Alo Yoga, Skims, Aritzia, Booking.com)   │
│  • Separates True Expenses vs. Payroll/GSU Inflows vs. Transfers     │
└──────────────────────────────────┬───────────────────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 3: 9 INTERACTIVE MONARCH MODULES (`monarch_finance_app.html`) │
│  01 // Modular Dashboard Overview   06 // Recurring & Oct Calendar   │
│  02 // Accounts & Net Worth Engine  07 // Goals & 311 Lease Vault    │
│  03 // Power-User Ledger & Splits   08 // Merchant Reports & Rules   │
│  04 // Sankey Cash Flow & Waterfall 09 // Solvency Stress-Tester     │
│  05 // Flex & Rollover Budgeting                                     │
└──────────────────────────────────────────────────────────────────────┘
```

### Feature-by-Feature Comparison & Implementation

| Module | How Monarch Money Works | Enhancements From Copilot / Lunch Money | How It Works in Your `Sovereign // Monarch Finance OS` |
| :--- | :--- | :--- | :--- |
| **01 // Dashboard** | Modular widgets showing Net Worth, Cash Flow, Top Categories, Budget Progress, Recurring, and Needs Review. | Real-time refund-adjusted net spend telemetry + true unencumbered liquidity KPI. | **5 Executive KPIs** + **6 Interactive Widgets** including instant one-click `"✓ Approve All"` in the Needs Review queue. |
| **02 // Accounts & Net Worth** | Groups Assets vs. Liabilities by institution with balance history. | Custom commitment encumbrance overlay for fixed-term leases. | Tracks all **7 accounts** (`$66,705.52` Assets vs `-$33,451.41` Cards = `+$33,254.11` Net Worth) + toggleable **311 Lease Encumbrance (`-$13,744.71`)** showing **`+$19,509.40` True Unencumbered Net Worth**. |
| **03 // Transactions & Refunds** | Multi-column search/filter, category reassignment, tags, splits, and review flags. | **Automatic Refund Pairing Engine**: links merchant credits directly to original purchases so returns don't inflate gross spend. | **Sortable 7-column table** across all 978 rows, **Global Net Spend vs. Raw Ledger toggle**, **Interactive Split Calculator modal**, CSV export, and dedicated **54-row Refund Pairing Audit Table**. |
| **04 // Cash Flow & Sankey** | Dynamic **Sankey diagram** mapping Income Sources $\rightarrow$ Expense Groups $\rightarrow$ Categories + Savings Rate %. | Excludes internal bank-to-bank and card autopay transfers so cash flow is never double-counted. | **Proportional SVG Sankey Diagram** mapping Google Payroll + Morgan Stanley GSU vests $\rightarrow$ Fixed Bills, Flexible Living, Non-Monthly & Retained Surplus + **Jul–Oct Monthly Waterfall Table**. |
| **05 // Flex & Category Budget** | **Monarch Flex Budgeting** simplifies budgeting into 3 buckets (*Fixed*, *Flexible "Flex Number"*, *Non-Monthly*). | **Copilot / Lunch Money Rollover Toggles** for discretionary and sinking categories. | Instant toggle between **3-Column Flex Budget View** and **12-Category Rollover Table** with automatic timeframe scaling (`1M`, `60D`, `90D`). |
| **06 // Recurring & Calendar** | Monthly calendar grid + list of upcoming paychecks, rent, credit card bills, and subscriptions. | Account-level routing labels (`SoFi 2752 → 5857`, `BofA 4473 → Amex 4002`) to prevent overdrafts. | **Full October 2026 Calendar Grid** + **10-Stream Recurring Directory** tracking Wed SoFi & Fri BofA paydays, dual rents, and Oct 17 / Oct 27 card autopays. |
| **07 // Goals & Sinking Vaults** | Links specific bank accounts to savings or debt-paydown goals. | True unencumbered buffer math inside dedicated sinking accounts. | Tracks **Vault #01: 311 Lease Reserve (`SoFi 2752`: `$26,003.87` balance vs `$13,744.71` remaining = `+$12,259.16` surplus)** and **Goal #02: 100% Card Float Elimination**. |
| **08 // Reports & Rules** | Top merchants by spend and visit count + `Settings > Rules` automation engine. | Multi-condition rules showing historical match counts across the ledger. | **Top 20 Merchant Matrix** (Gross vs. Refunded vs. Net Kept + Visit Frequency) + **7 Active Automation Rules**. |
| **09 // AI Advisor & Stress Test** | Static insights notifications. | Interactive cash-flow and account-routing simulator. | **Interactive 3-Slider Solvency Simulator** testing statement vs. 100% card payoff and `SoFi → BofA 4473` pre-autopay transfer routing. |

---

## 2. Key Financial Discoveries From the Full 90-Day Multi-Bank Ledger

1. **September Inflows Included `+$31,155.50` in Morgan Stanley Equity Releases**:
   - Alongside your regular Google LLC bi-weekly paychecks (`~$10,432.60` in Sep), `BofA Checking (4473)` received three Morgan Stanley ACH equity releases in September (`+$15,285.71` on Sep 16, `+$879.76` on Sep 29, and `+$14,990.03` on Sep 30), bringing total September true inflows to **`+$41,975.95`**.
2. **54 Merchant Refunds Totaling `-$8,238.73` Paired & Removed (`Jul – Oct 2026`)**:
   - Within the 60-day `Aug 18 – Oct 12` window, **26 merchant returns (`-$4,575.69` total: `-$4,261.54` across 24 Amex `4002` returns, `-$300.00` Otter Moving on SoFi `5857`, and `-$14.15` Google Store on BofA `8577`)** were matched and stripped from gross spending.
   - Across the full 90-day `Jul – Oct 2026` window, **54 merchant returns (`-$8,238.73`)** were paired with their original purchases.
3. **311 2nd Apartment Vault (`SoFi 2752`) Is 189.2% Funded**:
   - Current balance: **`$26,003.87`**.
   - Remaining 3 monthly transfers (`Nov`, `Dec`, `Jan` $\times \$4,581.57$ before lease ends **Feb 1, 2027**): **`$13,744.71`**.
   - **True Unencumbered Surplus inside SoFi 2752**: **`+$12,259.16`**.
4. **100% Credit Card Payoff + Routing Action Plan**:
   - Because both `BofA Visa 8577` (`$8,754.52` statement due Oct 17) and `Amex Reserve 4002` (`~$18,748.24` statement due Oct 27–28) draft from `BofA Checking 4473` (`$23,905.80` current balance), initiate a **`$12,000–$15,000` ACH transfer** from `SoFi Checking 5857` (or your unencumbered `SoFi 2752` buffer) to `BofA Checking 4473` before **Oct 25**.
   - Even if you pay off **100% of the current balance on both cards (`-$33,451.41`)** AND keep the entire **`$13,744.71` 311 lease reserve locked**, you still retain **`+$15,402.04` in unencumbered liquid cash** plus **`$4,107.36` in SoFi Brokerage (`+$19,509.40` unencumbered net worth)**.
