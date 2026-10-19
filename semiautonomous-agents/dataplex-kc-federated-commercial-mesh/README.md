# Dataplex Knowledge Catalog (KC) & Federated Commercial Intelligence Mesh

> **Executive Verdict**: Standalone Database MCP servers (`execute_sql`) only solve **~18%** of enterprise B2B commercial intelligence questions out-of-the-box. Adding **Dataplex Knowledge Catalog (KC) + BigQuery Gold Views + Python Counterfactual Simulation** raises the structured ceiling to **~48%**, while **Google ADK Multi-Tool Federation (`gemini-3.8-flash`)** unlocks the remaining **~52%** across Unstructured Contract/Delivery RAG, Licensed 3P Market APIs, and Executive QBR Automation.

---

## 1. Why Standalone Database MCP Fails on 82% of Commercial Queries

Connecting an LLM directly to raw enterprise tables using a single `execute_sql` tool triggers **6 Red-Flag Architectural Blockers**:

| Blocker Code | Architectural Blocker | Share | Root Cause in Raw SQL MCP | Federated Mesh Remediation (`vtxdemos.commercial_mesh_gold`) |
| :--- | :--- | :--- | :--- | :--- |
| **`LIC-GUARD`** | **License Compliance Blocker** | Critical | Unlicensed 3P analyst tables (`genai_usage_rights = FALSE`) forbid LLM prompt ingestion. | **Pre-Flight Dataplex License Guard** blocks restricted tables and substitutes 1P elasticity from `deal_pricing_scenarios`. |
| **`WHAT-IF`** | **Counterfactual Simulator** | ~21% | SQL is declarative over past rows; it cannot run price elasticity or rate-card stress tests. | **Python Counterfactual Simulator** pulls baseline cohorts from `v_gold_pricing_yield_dax` and models margin uplift. |
| **`ML-MODEL`** | **Missing Econometric Model** | ~13% | Raw CRM tables lack Hidden Markov regime states or 6-lever win-propensity weights. | **BigQuery Gold View** (`v_gold_markov_regime_analytics`) pre-computes Markov regimes and erosion risk. |
| **`UNSTRUCT-RAG`** | **Hidden Unstructured Notes** | ~33% | Deal slippage, MSA COLA caps, and termination clauses live in PDFs and review commentary. | **Federated RAG** joins structured Deal IDs with `clm_contract_vault_chunks` and `delivery_governance_hub`. |
| **`EXT-API`** | **External 3P Market API** | ~33% | Buyer intent surges, 10-K/8-K filings, and DIY AI hiring signals sit outside CRM/ERP tables. | **Licensed Market Signal Tool** correlates `external_market_signals` with active pipeline accounts. |
| **`SCHEMA-GAP`** | **Proprietary DAX Ratios** | ~17% | Multi-stage ratios (`CCI Excl. Billable Expenses`, `Adjusted Yield v1/v3/v4`) hallucinate in raw SQL. | **Dataplex KC Glossary + Gold Views** codify exact winsorized (`P05-P95`) and `1.5-sigma` capped DAX formulas. |

---

## 2. Diagram 1: The 4-Tier Enterprise Sufficiency Funnel (`18% -> 48% -> 97% -> 100%`)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│        ENTERPRISE B2B COMMERCIAL INTELLIGENCE BENCHMARK (100% CORPUS)      │
│         24 Representative Golden Questions // 203 Production Queries       │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 1 (18% Share -> 18% Cumulative | 91% Avg Readiness Confidence)        │
│ DETERMINISTIC PARAMETERIZED SQL                                            │
│  ├─ Engine : Google MCP Toolbox for Databases (`genai-toolbox` tools.yaml) │
│  ├─ Target : `vtxdemos.commercial_mesh_gold.v_gold_stage2b_stalled_deals`  │
│  └─ Solves : Stage 2B velocity bottlenecks, regional win rates, top N TCV  │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 2 (+30% Share -> 48% Structured Ceiling | 68% Avg Confidence)         │
│ DATAPLEX KC DAX GLOSSARY + BIGQUERY GOLD VIEWS + PYTHON WHAT-IF SIMULATOR  │
│  ├─ Engine : Dataplex Knowledge Catalog + BigQuery Gold Views + Python Sim │
│  ├─ Target : `v_gold_pricing_yield_dax`, `v_gold_markov_regime_analytics`  │
│  └─ Solves : CCI Excl. BE, Adjusted Yield v1/v3/v4, +300 bps Repricing Sim │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 3 (+49% Share -> 97% Cumulative | 45% Avg Readiness Confidence)       │
│ FEDERATED MULTI-TOOL AGENT (SQL + UNSTRUCTURED RAG + LICENSED 3P SIGNALS)  │
│  ├─ Guard  : Pre-Flight Dataplex GenAI License Guard (`genai_usage_rights`)│
│  ├─ Target : `clm_contract_vault_chunks`, `delivery_governance_hub`,       │
│  │           `external_market_signals`, `v_gold_account_360_health`        │
│  └─ Solves : MSA COLA/MFN clauses, delivery SLA slippage, DIY AI signals   │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 4 (+3% Share -> 100% Total Coverage | 44% Avg Readiness Confidence)   │
│ EXECUTIVE BRIEFING & WORKFLOW AUTOMATION                                   │
│  ├─ Engine : Google ADK (`gemini-3.8-flash`) + Workspace QBR Action Tool   │
│  └─ Solves : Account 360 Executive QBR Packet synthesis & squad dispatch   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Diagram 2: End-to-End Federated Architecture (`vtxdemos.commercial_mesh_gold`)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                   EXECUTIVE & COMMERCIAL ARCHITECT SURFACE                 │
│     3-Mode React Workbench (`:8766`) // VS Code & Antigravity IDE Cells    │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│        GOOGLE ADK ORCHESTRATOR (`gemini-3.8-flash`, location="global")     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ STEP 0: PRE-FLIGHT DATAPLEX GENAI LICENSE & RBAC GOVERNANCE GUARD    │  │
│  │ Queries `vtxdemos.commercial_mesh_gold.dataplex_source_governance`   │  │
│  │ Blocks `genai_usage_rights = FALSE` before any LLM prompt ingestion  │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ 4-TIER MULTI-AGENT ROUTER (Parallel Structured + RAG + Sim Dispatch) │  │
│  └──────┬───────────────────────────┬────────────────────────────┬──────┘  │
└─────────┼───────────────────────────┼────────────────────────────┼─────────┘
          ▼                           ▼                            ▼
┌───────────────────┐     ┌───────────────────────┐    ┌─────────────────────┐
│     PILLAR 1      │     │       PILLAR 2        │    │      PILLAR 3       │
│  TIER 1 (18.0%)   │     │    TIER 2 (30.0%)     │    │ TIERS 3 & 4 (52.0%) │
│   MCP TOOLBOX     │     │  DATAPLEX KC & SIM    │    │  RAG & 3P SIGNALS   │
├───────────────────┤     ├───────────────────────┤    ├─────────────────────┤
│ • `genai-toolbox` │     │ • Dataplex KC DAX     │    │ • Unstructured RAG: │
│   parameterized   │     │   Glossary Aspects    │    │   `clm_contract_    │
│   `tools.yaml`    │     │ • Gold Views:         │    │   vault_chunks` &   │
│ • `v_gold_stage2b`│     │   `v_gold_pricing_    │    │   `delivery_gov`    │
│   `_stalled_deals`│     │   yield_dax` &        │    │ • Licensed 3P Feed: │
│ • Zero ad-hoc SQL │     │   `v_gold_markov_*`   │    │   `external_market_ │
│   hallucinations  │     │ • Python Counter-     │    │   signals`          │
│ • Sub-500ms SLA   │     │   factual Simulator   │    │ • Account 360 QBR   │
└───────────────────┘     └───────────────────────┘    └─────────────────────┘
```

---

## 4. Diagram 3: Pre-Flight Dataplex GenAI License Guard (`genai_usage_rights` Intercept)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Commercial Query Requesting 3P Rate-Card Benchmarks (e.g., Q-016)          │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STEP 0: Pre-Flight Governance Guard queries BigQuery Governance Registry   │
│ `SELECT genai_usage_rights, pii_classification`                            │
│ `FROM vtxdemos.commercial_mesh_gold.dataplex_source_governance`            │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
              ┌───────────────────────────────────────────────┐
              │ Does Target Source Have genai_usage_rights?   │
              └───────┬───────────────────────────────┬───────┘
                      │ TRUE (13 Governed Sources)    │ FALSE (SRC-014)
                      ▼                               ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────────┐
│ CLEARED FOR GEMINI 3.8 FLASH          │ │ HARD COMPLIANCE INTERCEPT        │
│ • `crm_opportunities` (500 rows)      │ │ • Blocked: `Analyst_Benchmark_   │
│ • `deal_pricing_scenarios` (500 rows) │ │   Feed_Unlicensed` (SRC-014)     │
│ • `clm_contract_vault_chunks` (150)   │ │ • Zero rows enter LLM context    │
│ • `external_market_signals` (120)     │ │ • Auto-substitutes clean-room 1P │
│ • Executes Federated ADK Tool Plan    │ │   elasticity from `v_gold_*`     │
└───────────────────────────────────────┘ └──────────────────────────────────┘
```

---

## 5. `vtxdemos.commercial_mesh_gold` BigQuery Dataset (6 Tables & 4 Gold Views)

All **1,404 synthetic enterprise rows** are provisioned in GCP project **`vtxdemos`**, dataset **`commercial_mesh_gold`** (`location="US"`):

| BigQuery Table / Gold View | Rows | Grain & Primary Key | Purpose in the Federated Commercial Mesh |
| :--- | :--- | :--- | :--- |
| **`crm_opportunities`** | `500` | `opp_id` (`OPP-10001..`) | Core pipeline spine across NA, EMEA, APAC, LATAM with `stage_code`, `days_at_current_stage`, `tcv_usd`, `win_probability`, `markov_regime`, and 3 PWin lever scores (`pwin_lever_pricing_score`, `pwin_lever_exec_sponsor_score`, `pwin_lever_tech_diff_score`). |
| **`deal_pricing_scenarios`** | `500` | `opp_id` (`OPP-10001..`) | Commercial pricing constructs (`Fixed Price`, `Time & Materials`, `Outcome / Gain-Share`, `Managed Capacity`), `cci_excluding_be_pct`, `adjusted_yield_v3_trimmed`, `adjusted_yield_v4_sigma_capped`, and `ams_ai_task_substitutable_pct`. |
| **`delivery_governance_hub`** | `120` | `account_id` (`ACC-1001..`) | Post-sales delivery health (`rag_status`, `csat_score`, `nps_score`, `sla_slippage_days`, `eac_margin_variance_bps`, `open_staffing_roles`) plus `unstructured_director_review_notes`. |
| **`clm_contract_vault_chunks`** | `150` | `chunk_id` (`CLM-001..`) | Unstructured MSA/SOW legal clauses and review notes (`Stage_2B_Blocker_Reason`, `AI_Rate_Compression_Clause`, `COLA_Inflation_Cap`, `Termination_For_Convenience`) in `clause_or_risk_tag` and `verbatim_text_chunk`. |
| **`external_market_signals`** | `120` | `signal_id` (`SIG-001..`) | Licensed 3P market intelligence (`buyer_intent_surge_score`, `ai_self_sufficiency_index`, `client_rd_intensity_pct`, `c_suite_change_detected`, `competitor_concession_alert`, `signal_summary`). |
| **`dataplex_source_governance`** | `14` | `source_id` (`SRC-001..014`) | Dataplex Knowledge Catalog governance registry enforcing `genai_usage_rights` (`TRUE` for 13 governed sources; `FALSE` for quarantined `Analyst_Benchmark_Feed_Unlicensed`). |
| **`v_gold_stage2b_stalled_deals`** | View | `opp_id` | **Tier 1 Gold View**: Pre-joins `crm_opportunities` + `deal_pricing_scenarios` for Stage 2B bottlenecks. |
| **`v_gold_pricing_yield_dax`** | View | `opp_id` | **Tier 2 Gold View**: Materializes `CCI Excl. BE`, `Adjusted Yield v1/v3/v4`, and `be_passthrough_distortion_pct`. |
| **`v_gold_markov_regime_analytics`** | View | `opp_id` | **Tier 2 Gold View**: Computes Hidden Markov regime transition risk and 6-lever win probability drivers. |
| **`v_gold_account_360_health`** | View | `account_id` | **Tier 3/4 Gold View**: Unifies pre-sales Sold Yield v4 with post-sales EAC margin variance and 3P intent surges. |

---

## 6. Diagram 4: Separated `backend/` (5 Modular IDE Parts) & `frontend/` Directory Map

```text
dataplex-kc-federated-commercial-mesh/
├── README.md                              # Concise architecture & quickstart
├── backend/                               # LIVE BIGQUERY + ADK BACKEND
│   ├── seed_bigquery_vtxdemos.py          # Provisions 6 tables + 4 Gold Views
│   ├── live_demo_walkthrough.py           # 5 runnable `# %%` IDE demo cells
│   ├── customer_live_demo.ipynb           # Jupyter Notebook (Parts 1 to 5)
│   ├── server.py                          # FastAPI (:8766) + BQ Explorer API
│   ├── parts/                             # 5 Modular ~45-Line Demo Scripts
│   │   ├── part1_bigquery_gold_spine.py   # Part 1: 6 BQ tables + Gold Views
│   │   ├── part2_dataplex_license_guard.py# Part 2: GenAI_Usage_Rights Guard
│   │   ├── part3_tier1_mcp_toolbox_sql.py # Part 3: Tier 1 Parameterized SQL
│   │   ├── part4_tier2_kc_and_simulator.py# Part 4: Tier 2 DAX + Python Sim
│   │   └── part5_tier3_federated_agent.py # Part 5: Tier 3 gemini-3.8-flash
│   ├── config/
│   │   ├── bigquery_gold_views.sql        # 4 Gold View DDLs on vtxdemos
│   │   └── tools.yaml                     # genai-toolbox SQL tool definitions
│   └── agent/
│       └── mesh_orchestrator.py           # 4-Tier ADK + gemini-3.8-flash
└── frontend/                              # 3-MODE EXECUTIVE REACT WORKBENCH
    ├── package.json                       # React 18 + TypeScript + Vite
    ├── dist/                              # Self-contained production bundle
    └── src/
        ├── App.tsx                        # Mode 1 Audit, Mode 2 Diagrams,
        │                                  # Mode 3 Live BQ & Part 1-5 Runner
        ├── data.ts                        # 24 Golden Questions + telemetry
        ├── types.ts                       # Strict TypeScript interfaces
        └── styles.css                     # Executive Slate UI (#F8FAFC)
```

---

## 7. Quickstart: Run Part-by-Part in IDE or Launch the 3-Mode Executive Workbench

### Option A: Run Part-by-Part in VS Code / Antigravity IDE (`# %%` Cells or Notebook)

Open [`backend/live_demo_walkthrough.py`](backend/live_demo_walkthrough.py) (click **"Run Cell"** above each `# %%` block) or open [`backend/customer_live_demo.ipynb`](backend/customer_live_demo.ipynb):

- **Part 1 (`# %% [Part 1]`) — Verify BigQuery Gold Spine (`vtxdemos.commercial_mesh_gold`)**: Lists all 6 tables (`1,404` rows) and 4 Gold Views in `vtxdemos`.
- **Part 2 (`# %% [Part 2]`) — Pre-Flight Dataplex GenAI License Guard**: Queries `dataplex_source_governance`, blocks `Analyst_Benchmark_Feed_Unlicensed` (`genai_usage_rights = FALSE`), and substitutes clean-room 1P elasticity.
- **Part 3 (`# %% [Part 3]`) — Tier 1 (18%) MCP Toolbox Parameterized SQL**: Runs parameterized Stage 2B stalled deal queries against `v_gold_stage2b_stalled_deals`.
- **Part 4 (`# %% [Part 4]`) — Tier 2 (30%) Dataplex KC DAX Views & What-If Simulator**: Queries `v_gold_pricing_yield_dax` and runs a Python `+300 bps` repricing elasticity stress-test.
- **Part 5 (`# %% [Part 5]`) — Tier 3 (52%) Federated ADK + `gemini-3.8-flash` Agent**: Combines BigQuery `v_gold_account_360_health`, unstructured `clm_contract_vault_chunks` RAG, and `external_market_signals` via `gemini-3.8-flash` (`location="global"`).

```bash
# Provision/verify the live BigQuery dataset (idempotent)
python3 backend/seed_bigquery_vtxdemos.py

# Run all 5 parts non-interactively or pass --part 1..5
python3 backend/live_demo_walkthrough.py
```

### Option B: Launch the 3-Mode Executive Presentation Workbench (`:8766`)

```bash
python3 backend/server.py
```

Open `http://localhost:8766` to switch seamlessly across the **3 Presentation Modes** in the top navigation bar:
1. **`📊 Golden Questions & Tier Audit`**: Interactive 4-Tier Sufficiency Spectrum (`18% / 30% / 49% / 3%`), 6 Red-Flag Blocker pills, 24 Golden Questions table, and full-height `gemini-3.8-flash` AI Architect Drawer.
2. **`🏗 Interactive Solution Architecture Diagrams`**: Clickable end-to-end 4-Tier Federated Mesh & Pre-Flight License Guard visual blueprints with live SQL/Python code inspection.
3. **`💻 Live vtxdemos BigQuery & Inline Python Runner (Parts 1–5)`**: Browse all 6 live BigQuery tables (`1,404 rows`) & 4 Gold Views in `vtxdemos.commercial_mesh_gold`, and execute **Parts 1–5** inline with live output.
