# Dataplex Knowledge Catalog (KC) & Federated Commercial Intelligence Mesh

> **Reference Architecture & Diagnostic Workbench**: Why standalone Database MCP (`execute_sql`) servers only solve **~18%** of real-world Enterprise B2B Commercial Intelligence questions out-of-the-box, how **Dataplex Knowledge Catalog (KC) + BigQuery Gold Views + Python What-If Simulation** raise the structured ceiling to **~48%**, and how **Google ADK Multi-Tool Federation** unlocks the remaining **~52%** across Unstructured Contract/Visit RAG, Licensed 3P Market APIs, and Executive Workspace Automation.

---

## 1. The Enterprise Text-to-SQL & Database MCP Sufficiency Problem

Enterprise commercial leaders (Global Pipeline Directors, Deal Pricing Architects, Regional Revenue Leads, and Delivery Risk Officers) routinely ask questions that appear deceptively simple in natural language:

- *"Why is our contracted gross margin eroding relative to initial Deal Pricing Engine bids across EMEA renewals, and what happens if we uplift rate cards by +6%?"*
- *"Which >$5M Stage 3/4 opportunities slipped out of Q3, what termination-for-convenience or COLA clauses are holding up legal redlines, and what did the client CFO raise in recent executive visit debriefs?"*
- *"Compare our Financial Services win rate and discount depth against syndicated peer benchmarks and correlate with live external buyer intent surges."*

When engineering teams connect an LLM directly to a raw enterprise data warehouse (`CRM_Opportunity_Spine`, `Revenue_ODS_15TB`, `Deal_Pricing_Engine`, `ERP_Financials_Ledger`) using a single `execute_sql` MCP server, **~82% of production benchmark queries fail or hallucinate** due to **6 Red-Flag Architectural Blockers**:

| Blocker Code | Architectural Blocker | Benchmark Share | Root Cause in Raw Database MCP | Federated Mesh Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **`LIC-GUARD`** | **License Compliance Blocker** | Critical Trap | 3P syndicated tables (`Analyst_Benchmark_Feed_Unlicensed`) carry `GenAI_Usage_Rights = 0`, prohibiting LLM prompt ingestion. | **Pre-Flight Dataplex Governance Guard** intercepts restricted sources and substitutes governed 1P telemetry. |
| **`WHAT-IF`** | **Counterfactual What-If Simulator** | ~21% | SQL is declarative over historical rows; it cannot run Monte Carlo elasticity, Nash bargaining, or pyramid shifts. | **ADK Python Counterfactual Sandbox** consumes baseline cohorts from `genai-toolbox` and runs stress-tests. |
| **`ML-MODEL`** | **Missing ML / Econometric Model** | ~13% | Raw transaction tables do not store Hidden Markov pricing regimes or fitted logistic win-propensity weights. | Materialize **BigQuery ML (BQML)** inference scores into **Gold Views** or call a Vertex AI Endpoint tool. |
| **`UNSTRUCT-RAG`** | **Hidden Unstructured Notes** | ~33% | Deal slippage root causes, MSA redlines, and CFO sentiment live in PDFs (`CLM_Contract_Vault`) and call notes (`Customer_Visit_Logs`). | Federate structured BigQuery Deal IDs with **Vertex AI Search RAG** over indexed contracts and visit logs. |
| **`EXT-API`** | **External 3P Market API** | ~33% | Live B2B buyer intent surges (`Buyer_Intent_Signal_Stream`), 10-K/8-K filings (`SEC_Regulatory_Filings`), and tech telemetry sit outside BigQuery. | Orchestrate parallel tool calls to licensed **External Market Intelligence MCPs** alongside BigQuery. |
| **`SCHEMA-GAP`** | **Incomplete Schema / DAX Spec** | ~17% | Proprietary BI ratios (`Adjusted Yield v1/v3/v4`, `Book-to-Bill`) span 420+ wide tables in `Revenue_ODS_15TB`. | Govern canonical DAX definitions in **Dataplex Knowledge Catalog (KC)** backed by **Materialized Gold Views**. |

---

## 2. Diagram 1: The 4-Tier Enterprise Question Sufficiency Funnel

```text
┌────────────────────────────────────────────────────────────────────────────┐
│        ENTERPRISE B2B COMMERCIAL INTELLIGENCE BENCHMARK (100% CORPUS)      │
│         24 Representative Benchmark Questions // 203 Production Queries    │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 1 (~18% Share | 91% Avg Readiness Confidence)                         │
│ DETERMINISTIC PARAMETERIZED SQL                                            │
│  ├─ Engine : Google MCP Toolbox for Databases (`genai-toolbox`)            │
│  ├─ Sources: `CRM_Opportunity_Spine`, `Revenue_ODS_15TB` (Gold Projection) │
│  └─ Verdict: SUFFICIENT FOR STANDALONE DB MCP (Zero SQL Hallucination)     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 2 (+30% Share -> 48% Structured Ceiling | 68% Avg Confidence)         │
│ SEMANTIC BI LAYER (DATAPLEX KC DAX) + GOLD VIEWS + PYTHON SIMULATOR        │
│  ├─ Engine : Dataplex Knowledge Catalog + BQ Conversational Analytics      │
│  ├─ Compute: Materialized BigQuery Gold Views + ADK Python What-If Sandbox │
│  ├─ Sources: `Deal_Pricing_Engine`, `ERP_Financials_Ledger`, `Workforce`   │
│  └─ Solves : Adjusted Yield v1/v3/v4, Hidden Markov Regimes, Margin Stress │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 3 (+49% Share -> 97% Cumulative | 45% Avg Readiness Confidence)       │
│ FEDERATED MULTI-TOOL AGENT (SQL + UNSTRUCTURED RAG + LICENSED 3P APIS)     │
│  ├─ Guard  : Pre-Flight Dataplex GenAI License & RBAC Policy Interceptor   │
│  ├─ RAG    : Vertex AI Search (`CLM_Contract_Vault`, `Customer_Visit_Logs`)│
│  ├─ 3P API : `Buyer_Intent_Signal_Stream`, `Tech_Stack_Telemetry_Feed`     │
│  └─ Solves : Cross-corpus deal slippage, MSA COLA caps, compliant 3P intel │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ TIER 4 (+3% Share -> 100% Total Coverage | 44% Avg Readiness Confidence)   │
│ MULTI-SYSTEM ACTION & EXECUTIVE BRIEFING AUTOMATION                        │
│  ├─ Engine : Google Workspace Action MCP + Pursuit Mobilization Webhook    │
│  └─ Solves : Account 360 Executive QBR Packet synthesis & squad dispatch   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Diagram 2: End-to-End 3-Pillar Federated Architecture

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                   EXECUTIVE & COMMERCIAL ARCHITECT SURFACE                 │
│     Gemini Enterprise / Antigravity IDE / React Topology Workbench UI      │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│              CLOUD RUN: GOOGLE ADK FEDERATED MESH ORCHESTRATOR             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ STEP 0: PRE-FLIGHT DATAPLEX GENAI LICENSE & RBAC GOVERNANCE GUARD    │  │
│  │ Inspects `data_source_governance` (`genai_usage_rights == 1`)        │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │MULTI-AGENT ROUTER (Tier 1..4 Classifier + Parallel Tool Dispatcher) │  │
│  └──────┬───────────────────────────┬────────────────────────────┬──────┘  │
└─────────┼───────────────────────────┼────────────────────────────┼─────────┘
          ▼                           ▼                            ▼
┌───────────────────┐     ┌───────────────────────┐    ┌─────────────────────┐
│     PILLAR 1      │     │       PILLAR 2        │    │      PILLAR 3       │
│  DETERMINISTIC    │     │  SEMANTIC BI & SIM    │    │ UNSTRUCTURED & 3P   │
│   SQL TOOLBOX     │     │   DATAPLEX KC + BQ    │    │  FEDERATED MESH     │
├───────────────────┤     ├───────────────────────┤    ├─────────────────────┤
│ • `genai-toolbox` │     │ • Dataplex Knowledge  │    │ • Vertex AI Search  │
│ • Parameterized   │     │   Catalog Glossary    │    │   `CLM_Contract` &  │
│   `tools.yaml`    │     │ • BigQuery Gold Views │    │   `Visit_Logs` RAG  │
│ • Zero ad-hoc     │     │   (`v_gold_*`)        │    │ • Licensed 3P APIs: │
│   join guessing   │     │ • BQ Conversational   │    │   `Buyer_Intent`,   │
│ • Sub-500ms SLA   │     │   Analytics (BQCA)    │    │   `SEC_Filings`     │
│                   │     │ • Python Counter-     │    │ • Workspace QBR     │
│                   │     │   factual Sandbox     │    │   Action Generator  │
└───────────────────┘     └───────────────────────┘    └─────────────────────┘
```

---

## 4. Diagram 3: Pre-Flight GenAI Data Licensing & RBAC Governance Guard Flow

A critical failure mode of naive Database MCP deployments is exposing **all** warehouse tables to LLM tool calls—including syndicated third-party analyst tables (`Analyst_Benchmark_Feed_Unlicensed`) whose procurement contracts strictly forbid passing rows into generative AI prompts or vector stores.

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Incoming Commercial Query (e.g., Q-016: Competitor Rate-Card Benchmarking) │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ ADK Pre-Flight Governance Guard queries Dataplex Aspect Registry           │
│ `SELECT genai_usage_rights, pii_classification FROM data_source_governance`│
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
              ┌───────────────────────────────────────────────┐
              │ Does Target Source Allow GenAI LLM Ingestion? │
              └───────┬───────────────────────────────┬───────┘
                      │ YES (genai_usage_rights=1)    │ NO (rights=0)
                      ▼                               ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────────┐
│ CLEARED FOR EXECUTION                 │ │ HARD COMPLIANCE INTERCEPT        │
│ • `CRM_Opportunity_Spine`             │ │ • Target: `Analyst_Benchmark_    │
│ • `Revenue_ODS_15TB` (via Gold Views) │ │   Feed_Unlicensed` (SRC-014)     │
│ • `Deal_Pricing_Engine`               │ │ • Blocks raw SQL & LLM egress    │
│ • `CLM_Contract_Vault` (ACL Scoped)   │ │ • Substitutes 1P Governed Win/   │
│ • `Buyer_Intent_Signal_Stream`        │ │   Loss + Licensed Market API     │
│ • Executes Federated Tool Plan        │ │ • Logs Audit Trail Event         │
└───────────────────────────────────────┘ └──────────────────────────────────┘
```

---

## 5. Architectural Assessment Confidence % & Missing Artifacts Methodology

Every benchmark question (`Q-001` through `Q-024`) in `data/taxonomy_questions_catalog.json` and the TypeScript Workbench includes two explicit production-readiness telemetry fields:

1. **`confidence_pct` (Color-Coded Readiness Score)**:
   - **Green (`>= 80%` — High Readiness)**: Deterministic SQL over known primary keys (`Tier 1`). Only minor physical DDL verification (e.g., currency normalization or stage audit timestamp behavior) is needed.
   - **Amber (`50% - 79%` — Semantic / Simulator Gap)**: Requires codifying proprietary DAX definitions (`Adjusted Yield v1/v3/v4`), cross-system WBS entity bridges, or elasticity parameters (`Tier 2`).
   - **Red (`< 50%` — Multi-Tool Federation / Legal Blocker)**: Requires unstructured Document AI chunking (`CLM_Contract_Vault`), external 3P API entity resolution, or legal remediation for unlicensed feeds (`Tier 3` & `Tier 4`).
2. **`missing_artifacts` (Missing Schema / Customer Artifacts Needed for 100% Precision)**:
   - Explicitly lists the exact physical BigQuery DDLs, DAX formula sheets, join keys, or legal addenda required from customer data stewards to move each question from architectural prototype to 100% production precision.

---

## 6. Repository Structure

```text
dataplex-kc-federated-commercial-mesh/
├── README.md                              # Architecture guide & quickstart
├── data/
│   ├── synthetic_topology_seed.py         # Seed generator (SQLite + JSON)
│   ├── commercial_spine_mock.db           # Seeded SQLite mock (8 systems)
│   └── taxonomy_questions_catalog.json    # 24 questions + confidence_pct
├── config/
│   ├── tools.yaml                         # genai-toolbox SQL definitions
│   └── bigquery_gold_views.sql            # Materialized Gold View DDLs
├── agent/
│   ├── mesh_orchestrator.py               # 4-Tier ADK + License Guard
│   └── server.py                          # FastAPI + static UI server
└── frontend/
    ├── package.json                       # TypeScript + React 18 + Vite
    ├── tsconfig.json                      # Strict TypeScript config
    ├── vite.config.ts                     # Vite dev proxy & build config
    ├── index.html                         # Workbench HTML entry point
    ├── dist/                              # Self-contained UI bundle
    └── src/
        ├── types.ts                       # TypeScript interfaces
        ├── data.ts                        # 24 hydrated benchmark questions
        ├── styles.css                     # Light/Dark + Ink loader CSS
        ├── App.tsx                        # Workbench + 3-Tab Drawer UI
        └── main.tsx                       # React DOM root mount
```

---

## 7. Quickstart Instructions

### Step 1: Seed the Synthetic Commercial Spine Database & 24-Question Catalog

```bash
python3 data/synthetic_topology_seed.py
```

This generates:
- `data/commercial_spine_mock.db` (populated with `opportunities`, `pricing_scenarios`, `delivery_health`, `unstructured_deal_notes`, `external_market_signals`, and `data_source_governance`)
- `data/taxonomy_questions_catalog.json` (all 24 benchmark questions enriched with `confidence_pct` and `missing_artifacts`)

### Step 2: Launch the FastAPI + ADK Federated Mesh Backend

```bash
# Optional: set GOOGLE_CLOUD_PROJECT to enable live Vertex AI Gemini Copilot synthesis
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

python3 -m uvicorn agent.server:app --host 0.0.0.0 --port 8080 --reload
```

Key REST Endpoints exposed by `agent/server.py`:
- `GET  /api/topology` — Returns the 4-Tier architecture summary, 6 blocker counts, and 14 governed data sources.
- `GET  /api/questions` — Returns the 24 benchmark questions with `confidence_pct` and `missing_artifacts`.
- `POST /api/simulate-question` — Runs the Pre-Flight License Guard, parameterized SQL, Python What-If Simulator, and Unstructured RAG trace.
- `POST /api/copilot/chat` — Live Vertex AI Gemini Architect Copilot grounded on the selected question's DAX formula, Gold View DDL, and missing artifacts.
- `POST /api/antigravity/send` — Dispatches the selected question blueprint directly to the active Antigravity IDE agent session.

### Step 3: Launch or Rebuild the TypeScript + React Workbench UI

The pre-built bundle in `frontend/dist/` is served automatically at `http://localhost:8080`. To run the Vite hot-reload development server:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (or `http://localhost:8080`) to explore the **Sufficiency Spectrum Meter**, filter by **4 Architectural Tiers** and **6 Red-Flag Blockers**, inspect **Architectural Assessment Confidence %** and **Missing Artifacts**, and open the **Live 3-Tab AI Architect Drawer**.
