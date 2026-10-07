# 05 — FinOps & Cloud Spanner Hybrid GraphRAG Cost Model

## 1. Enterprise Legal Data & User Baseline

| Dimension | Stated Volume | Architectural Handling |
| :--- | :--- | :--- |
| **Users / Licenses** | **1,300 active lawyers** (1,500–3,000 total GE seats) | Gemini Enterprise Standard ($25.50/user/mo w/ 15% discount) |
| **iManage DMS** | **20,000,000 docs (10 TB)** | Active 3–5 yr working set (`4M–5M docs / 2.5 TB`) hot in Spanner |
| **SharePoint + OneDrive** | **2,000,000 docs (2.5 TB matter sites)** | Indexed into Spanner Graph & BigQuery Lakehouse |
| **Exchange / O365 Email** | **700,000,000 active emails (150 TB)** | External/attachment deal emails (`15M` in 3–5 yr window) embedded; headers in Graph |
| **Intapp Ethical Walls** | **≈ 50,000 Client Matter Numbers (CMNs)** | Real-time SQL `INCLUDE` / `EXCLUDE` ACL changes enforced at 0ms in Spanner GQL |

---

## 2. Cost-Bearing Architecture Layers

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  1. PREPROCESSING & INGESTION PIPELINE                                   │
│     • GCS Staging (12.5 TB iManage/SP + 150 TB Email Archive w/ CMEK)    │
│     • Datastream CDC (Intapp SQL Walls) + Pub/Sub + Cloud Run Parsers    │
│     • Bounding-Box Parser (PyMuPDF/OpenXML + Gemini 3.8 Flash on scans)  │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  2. GEMINI EMBEDDING LAYER (Vertex AI gemini-embedding-2)                │
│     • One-Time Backfill (Batch API 50% discount) + Monthly Delta         │
│     • 3,072-dim vectors across Clauses, Chunks & Deal Emails             │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  3. UNIFIED RAG & GRAPH CONTEXT ENGINE                                   │
│     • Cloud Spanner Enterprise: LexGraphLegalGraph (GQL) + Vector + FTS      │
│     • Vertex AI Vector Search (ScaNN) w/ Intapp Token Restricts          │
│     • BigQuery Lakehouse: 5,000-Row x 100-Col Queryable Analysis Grids   │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  4. AGENT RUNTIME & GEMINI LLM CALLS                                     │
│     • Cloud Run (MCP App SEP-1865 + A2UI v0.9 Agents) + Agent Engine     │
│     • Gemini 3.8 Flash (80% Interactive + Dynamic Grid Column Extraction)│
│     • Gemini 4 Pro (20% Complex Legal Synthesis + Citation Verifier)     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Monthly Recurring Run-Rate Comparison

| Architecture Layer & Component | Option A: Smart Tiered (55M Hot Chunks + BQ Archive) | Option B: Full All-Hot (250M Hot Chunks) | Sizing & Pricing Breakdown (3-Yr CUD / Enterprise Rates) |
| :--- | :--- | :--- | :--- |
| **1. Preprocessing & Ingestion Pipeline (Ongoing Delta)** | **$3,550 / mo** | **$5,650 / mo** | GCS staging + Datastream CDC (Intapp SQL) + delta parsing |
| **2. Cloud Spanner + Hybrid RAG & Graph Engine** | **$6,530 / mo** | **$17,050 / mo** | Spanner Enterprise (5 nodes Opt A / 14 nodes Opt B) + Storage + BigQuery |
| **3. Monthly Embeddings (`gemini-embedding-2`)** | **$220 / mo** | **$350 / mo** | ≈ 2M new chunks/mo + ≈ 715K live query embeddings/mo (3,072-dim) |
| **4. Agent Runtime & Gemini Model Calls (1,300 Lawyers)** | **$8,200 / mo** | **$9,200 / mo** | Cloud Run MCP App + Gemini 3.8 Flash ($2.6K) + Gemini 4 Pro ($4.5K) |
| **TOTAL MONTHLY GCP + AGENT + RAG COST** | **$18,500 / month** | **$32,250 / month** | **$222,000 / yr (Option A)** vs. **$387,000 / yr (Option B)** |
| **Incremental Per-User Cost (3,000 Seats)** | **$6.16 / user / mo** | **$10.75 / user / mo** | Zero "Double Storage" overage in Gemini Enterprise |
