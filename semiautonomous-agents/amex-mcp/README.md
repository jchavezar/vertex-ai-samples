# Amex MCP — Hybrid Search over Financial Transactions

Automated Amex statement ingestion + Gemini enrichment pipeline + hybrid search (semantic + structured + compute) exposed as MCP tools.

## Why This Architecture

LLMs are unreliable for math. Vector search alone can miss results. SQL alone can't understand "coffee shops." This system combines all three so each layer does what it's good at:

```
"how much did I spend on coffee shops in March?"

  1. SEMANTIC (vector search)     →  "coffee shops" → embed → find Blue Bottle, Starbucks, Peet's
  2. STRUCTURED (Firestore filter) →  date >= 2026-03-01 AND date <= 2026-03-31
  3. COMPUTE (Python math)         →  SUM(amount) = $127.43
```

| Layer | Good at | Bad at |
|-------|---------|--------|
| **Semantic** | "coffee shops", "trip expenses", "stuff for the kids" | exact math, date ranges |
| **Structured** | card_member = "X", date ranges, category = "Dining" | fuzzy concepts |
| **Compute** | SUM, AVG, COUNT, GROUP BY | understanding intent |

### Recall Guarantee

At this scale (~500 txns/month), Firestore uses **exact KNN** (brute-force), not approximate nearest neighbors. Combined with `limit=1000` on pre-filtered subsets that are always smaller than 1000, this gives **100% recall** — every relevant transaction is checked.

For purely structured queries (no semantic component), vector search is bypassed entirely and **all matching rows** are returned.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WRITE PATH                               │
│                                                                 │
│  Cloud Run Job (monthly)          Manual CSV Upload (fallback)  │
│  Playwright + Gmail OTP           ingest_amex_csv tool          │
│         │                                  │                    │
│         └──────────┬───────────────────────┘                    │
│                    ▼                                            │
│            CSV Parser (parser.py)                               │
│                    │                                            │
│                    ▼                                            │
│      ┌─── Enrichment Pipeline (5 stages) ───┐                  │
│      │                                       │                  │
│      │  1. Categorize (Gemini)               │                  │
│      │     → category, subcategory, tags,    │                  │
│      │       merchant_type, purpose, etc.    │                  │
│      │                                       │                  │
│      │  1.5 Embed (gemini-embedding-001)     │                  │
│      │     → 768d vector per transaction     │                  │
│      │                                       │                  │
│      │  2. Detect Subscriptions              │                  │
│      │     → deterministic frequency +       │                  │
│      │       Gemini verification             │                  │
│      │                                       │                  │
│      │  3. Match Receipts (Gmail + Gemini)   │                  │
│      │     → correlate ambiguous charges     │                  │
│      │                                       │                  │
│      │  4. Spending Insights                 │                  │
│      │     → deterministic stats +           │                  │
│      │       Gemini narrative                │                  │
│      │                                       │
│      │  5. Recommendations (Gemini)          │                  │
│      │     → savings tips, spending score    │                  │
│      └───────────────────────────────────────┘                  │
│                    │                                            │
│                    ▼                                            │
│  Firestore: amex_statements/{YYYY-MM}  (enriched statement)    │
│  Firestore: amex_transactions/{id}     (denormalized + vector) │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        READ PATH                                │
│                                                                 │
│  MCP Server (FastMCP "amex-statements")                         │
│         │                                                       │
│         ├── smart_query(query, filters, group_by, aggregate)    │
│         │     ├─ query="coffee" → embed → find_nearest (semantic)│
│         │     ├─ filters={date, category} → Firestore WHERE     │
│         │     └─ aggregate="sum" → Python SUM/AVG/COUNT         │
│         │                                                       │
│         ├── get_spending_by_category(year, month)               │
│         ├── get_category_trends(months)                         │
│         ├── get_top_merchants(year, month)                      │
│         ├── get_subscriptions()                                 │
│         ├── get_spending_insights(year, month)                  │
│         ├── get_recommendations()                               │
│         ├── get_latest_amex_statement()                         │
│         ├── get_amex_statement(year, month)                     │
│         ├── enrich_statement(year, month)                       │
│         └── ingest_amex_csv(csv_content)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Enriched Fields per Transaction

The categorizer extracts these fields in a **single Gemini call** (batches of 25):

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `enriched_category` | enum (16) | "Dining" | Structured filter |
| `subcategory` | string | "Coffee" | Structured filter |
| `merchant_clean` | string | "Blue Bottle Coffee" | Display + search |
| `tags` | string[] | ["coffee", "cafe", "beverage"] | Semantic keywords |
| `merchant_type` | enum | "local", "chain", "online" | Structured filter |
| `purchase_channel` | enum | "in_store", "app", "subscription" | Structured filter |
| `purpose` | enum | "personal", "business", "travel" | Structured filter |
| `confidence` | float | 0.95 | Quality indicator |
| `embedding` | float[768] | [...] | Vector search |

More structured fields = less work for vector search = higher recall.

## Prerequisites

- GCP project with Firestore, Secret Manager, Vertex AI APIs enabled
- `gcloud` CLI authenticated
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Amex credentials in Secret Manager (secret `amx`)
- Gmail OAuth tokens in Secret Manager (secret `gworkspace-mcp-tokens`)

## Setup & Reproduce

### 1. Install dependencies

```bash
cd semiautonomous-agents/amex-mcp
uv sync
```

### 2. Create Firestore vector index

The first `smart_query` with semantic search will prompt you to create a composite index. Alternatively, create it manually:

```bash
gcloud firestore indexes composite create \
  --project=vtxdemos \
  --collection-group=amex_transactions \
  --field-config field-path=date,order=ASCENDING \
  --field-config field-path=embedding,vector-config='{"dimension":"768","flat":{}}' \
  --database="(default)"
```

### 3. Ingest statements

**Option A: Automated (Cloud Run Job)**
```bash
./deploy.sh
gcloud run jobs execute amex-statement-sync --region=us-east1 --project=vtxdemos
```

**Option B: Manual CSV upload via MCP**
```
Use the ingest_amex_csv tool with raw CSV content from Amex
```

### 4. Run enrichment

Enrichment runs automatically after ingestion. To re-enrich:
```
Use the enrich_statement(year, month, force=True) tool
```

### 5. Start MCP server

```bash
cd amex-mcp
uv run python mcp_server/server.py
```

Add to Claude Code config (`~/.claude/.mcp.json`):
```json
{
  "mcpServers": {
    "amex": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/amex-mcp", "python", "mcp_server/server.py"]
    }
  }
}
```

### 6. Query examples

```
smart_query(query="coffee shops", filters='{"date_after":"2026-03-01"}')
smart_query(filters='{"category":"Dining"}', group_by="merchant_clean", aggregate="sum")
smart_query(query="business meals", aggregate="sum")
smart_query(filters='{"period":"2026-04"}', group_by="enriched_category", aggregate="sum")
```

## File Structure

```
amex-mcp/
├── amex_job/                    # Cloud Run Job — statement ingestion
│   ├── main.py                  # Entry point
│   ├── browser.py               # Playwright login + Gmail OTP + CSV download
│   ├── parser.py                # Amex CSV parser
│   ├── credentials.py           # Secret Manager + Gmail OAuth
│   └── storage.py               # Firestore CRUD + vector search + structured query
├── enrichment/                  # Gemini enrichment pipeline
│   ├── pipeline.py              # Orchestrator (5 stages)
│   ├── gemini_client.py         # Vertex AI Gemini wrapper (retry + rate limit)
│   ├── embedder.py              # gemini-embedding-001 (768d) batch embeddings
│   ├── categorizer.py           # Stage 1: categorize + tags + merchant_type + purpose
│   ├── subscription_detector.py # Stage 2: recurring charge detection
│   ├── receipt_matcher.py       # Stage 3: Gmail receipt correlation
│   ├── insights.py              # Stage 4: spending analytics
│   ├── recommender.py           # Stage 5: financial recommendations
│   └── prompts.py               # All prompt templates
├── mcp_server/
│   ├── server.py                # FastMCP server (registers all tool modules)
│   └── tools/
│       ├── search.py            # smart_query — hybrid search (semantic + structured + compute)
│       ├── statements.py        # get/list statements
│       ├── ingestion.py         # CSV upload + enrich trigger
│       ├── categories.py        # spending by category, trends, top merchants
│       ├── subscriptions.py     # recurring charges
│       └── insights.py          # AI insights + recommendations
├── pyproject.toml               # uv project config
├── deploy.sh                    # Cloud Run Job deployment
└── README.md
```

## Security

- Credentials only in Secret Manager — never logged, never in MCP responses
- MCP tools are read-only from Firestore — no browser, no Amex access
- Gmail access uses existing OAuth tokens (same as gworkspace MCP)
- Embeddings are stored in Firestore — no external vector DB
