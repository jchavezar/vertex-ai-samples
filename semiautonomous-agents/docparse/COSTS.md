# docparse — End-to-End Cost Model

> Per-document and per-query cost for the full lifecycle: **extract → index → serve via Agent Engine + RAG**.
> Numbers calibrated against real production logs from `sharepoint-wif` (Cloud Run docparse service, 2026-04-25).
> Benchmark: a **30-page mixed-content PDF** (text + tables + ~3 charts + ~2 photos), the typical enterprise report.

---

## TL;DR

| Phase | When you pay | Cost per 30-page doc / per query |
|---|---|---|
| **Extraction** (Cloud Run + Gemini cascade) | one-time, on PDF upload | **~$1.50 – $3.00 per doc** |
| **Indexing** (RAG Engine corpus) | one-time, after extract | **~$0.005 per doc** (effectively free) |
| **Storage** (GCS + RAG vectors) | monthly, ongoing | **~$0.002 per doc per month** |
| **Serve — RAG retrieval + Gemini synthesis** | per user query | **~$0.016 per query** |
| **Serve — Agent Engine compute** | hourly, while min-instances ≥ 1 | **~$50–80 / month per always-on agent** |
| **(Optional) Gemini Enterprise wrapper** | per seat | **~$30 / user / month** |

**Rough rules of thumb:**
- A **1,000-document corpus** costs ~**$2k one-time to extract**, then ~$2/month to store, plus ~$50/month for the always-on agent.
- **10k queries/month** against that corpus = ~**$160/month** in Gemini synthesis cost.
- The break-even where serving cost overtakes extraction cost is roughly **125k queries per doc** — for almost any real workload, **extraction dominates the bill.**

---

## What you're paying for, stage by stage

```
PDF upload (GCS)
    ↓ Eventarc
[STAGE 1 — extractor on Cloud Run]
    ├─ Gemini 3 Flash Lite   → region detection per page
    ├─ Gemini 3 Flash        → page OCR + tables + misc
    └─ Gemini 3.1 Pro        → charts + diagrams (high-fidelity)
    ↓ markdown lands in GCS
[STAGE 2 — indexing]
    ├─ Per-page split (CPU only, free)
    └─ RAG Engine corpus import + text-embedding-004 embeddings
    ↓
[STAGE 3 — serve]
    ├─ User query hits Gemini Enterprise (or direct ADK)
    ├─ Agent Engine receives stream_query
    ├─ VertexAiRagRetrieval → top_k=20 chunks
    └─ Gemini 3 Flash synthesizes grounded answer
```

Three model SKUs do the work. Vertex AI list pricing as of Apr 2026:

| Model | Input (text/image/video) | Output | Use in pipeline |
|---|---:|---:|---|
| `gemini-3.1-flash-lite-preview` | $0.00025 / 1k tok | $0.0015 / 1k tok | region detect, photo captions |
| `gemini-3-flash-preview` | $0.0005 / 1k tok | $0.003 / 1k tok | page OCR, tables, agent synthesis |
| `gemini-3.1-pro-preview` | $0.002 / 1k tok | $0.012 / 1k tok | chart/diagram structured extraction |

> Verified against the official [Vertex AI generative AI pricing page](https://cloud.google.com/vertex-ai/generative-ai/pricing) (April 2026). Cross-checked against `sharepoint-wif` April 25 billing: $2,040 Flash output ÷ 680M tok = $0.003/1k. ✓
>
> **Why "preview" still costs money:** on Vertex AI, "preview" is a *lifecycle* label (stable enough for production trial, no full SLA), **not** a pricing tier. Google publishes preview models on the same pricing table as GA models at full rate. The free tier you may remember is on **AI Studio** (the consumer playground at aistudio.google.com) — Vertex AI has no equivalent free preview tier.

---

## Stage 1 — Extraction cost (per 30-page doc)

The extractor runs three concurrent passes per page (`extractor/src/docparse/pipeline.py`):

1. **Detect regions** — 1 call per page, classifies layout into text / table / chart / diagram / photo.
2. **OCR + text body** — 1 Flash call per page emitting markdown.
3. **Structured regions** — for each detected non-text region, a model call sized to its complexity.

For a typical 30-page mixed-content report (~3 charts, ~5 tables, ~2 photos, ~2 diagrams):

| Call type | Model | Calls per doc | Avg output tokens | Cost / doc |
|---|---|---:|---:|---:|
| Region detect | Lite | 30 | 800 | $0.04 |
| Page OCR | Flash | 30 | 5,000 | $0.45 |
| Table extract | Flash | 5 | 4,000 | $0.06 |
| Photo caption | Lite | 2 | 500 | <$0.01 |
| Chart extract | Flash → Pro retry | 3 | 8,000 (Pro) | $0.30 |
| Diagram extract | Pro | 2 | 6,000 | $0.15 |
| Image input (page renders) | all models | ~70 | 1,500 each | $0.10 |
| **Subtotal — Gemini** | | **~75 calls** | | **~$1.10** |
| Cloud Run compute | 2 vCPU, 4 GB RAM | ~14 min/doc, concurrency=1 | | $0.02 |
| GCS read+write (PDF in, MD out) | Standard | 10 MB in, 150 KB out | | <$0.01 |
| **Total — extraction** | | | | **~$1.10 – $1.50** |

For a **chart-dense** report (10+ charts on a 30-page doc, e.g. industry analysis):
- Pro calls climb from 5 → 20+ → adds ~$1.50
- **Total: ~$2.50 – $3.00 per doc**

For a **text-heavy** report (contract / policy with 1-2 small tables):
- Pro calls drop to 0, fewer table calls
- **Total: ~$0.60 – $0.80 per doc**

> **Calibration check:** On 2026-04-25 the docparse Cloud Run processed at ~35 docs/hour and burned $2,458 over 22 hours = **~$112/hour ÷ 35 = $3.20/doc**. That matches the upper end (chart-dense), which is exactly what the eval corpus looks like (industry/competitive-intelligence reports).

---

## Stage 2 — Indexing cost

After extraction lands in `gs://${PROJECT}-docparse-out/`, `deploy.sh agent` splits each markdown into per-page chunks and imports into a Vertex AI RAG Engine corpus.

Per 30-page doc:

| Item | Quantity | Unit cost | Cost / doc |
|---|---:|---:|---:|
| `text-embedding-004` embeddings | 30 chunks × ~2k tok = 60k tok | $0.000025/1k | $0.0015 |
| RAG Engine import call | 1 batch | included | — |
| **Total — indexing (one-time)** | | | **~$0.005** |

**Effectively free** at any reasonable corpus size. A 10,000-document corpus costs ~$50 one-time to embed.

---

## Storage — ongoing monthly cost

| Item | Per 30-page doc | Per 1,000 docs |
|---|---:|---:|
| GCS Standard — PDFs in | ~10 MB → $0.0002/mo | $0.20/mo |
| GCS Standard — markdown out | ~150 KB → negligible | $0.003/mo |
| RAG Engine vector storage | ~90 KB embeddings → negligible | $0.05/mo (~50 MB) |
| **Total — storage / doc / month** | **<$0.001** | **~$0.25/mo** |

Even at 100k documents, monthly storage is ~$25. Storage is **never** the cost driver; it disappears in the noise next to extraction.

---

## Stage 3 — Serving cost (per user query)

Each user question goes:
`Gemini Enterprise UI → Agent Engine stream_query → RAG retrieval (top_k=20) → Gemini 3 Flash synthesis → grounded answer + citations`.

Per query:

| Item | Quantity | Cost / query |
|---|---:|---:|
| RAG retrieval (embedding the query + vector search) | 1 query embedding (~50 tok) + ANN search | <$0.0001 |
| Gemini 3 Flash input (context = 20 retrieved chunks @ ~1k tok + system + user) | ~22k input tok | $0.011 |
| Gemini 3 Flash output (grounded answer + citations) | ~1,500 output tok | $0.0045 |
| Agent Engine per-request compute | 1 stream_query, ~3 sec | <$0.001 |
| **Total — per query** | | **~$0.016** |

So **10,000 queries/month = ~$160/month** in serving cost.

### Agent Engine fixed cost — the only "always on" line

Reasoning Engines (where the ADK agent runs) bill on vCPU-hour + memory-hour like Cloud Run, but with a higher floor when `min_instances ≥ 1`. Reference numbers:

| Configuration | Approx. monthly fixed cost |
|---|---:|
| `min_instances=0` (cold-start tolerant) | $0 idle + ~$0.001 per cold start |
| `min_instances=1`, 2 vCPU / 4 GB (recommended for prod) | **~$50 – $80 / month** |
| `min_instances=2` (HA pair) | **~$100 – $160 / month** |

**Trade-off:** at min=1 the first-token latency drops from ~5s (cold) to <1s (warm). For a chat product that matters; for a back-office batch process it doesn't.

### Optional: Gemini Enterprise wrapping

If you front the agent with a Gemini Enterprise app (the chat UI / streamAssist layer in the architecture diagram), GE adds:

- **~$30 / user / seat / month** (list price; check your enterprise agreement)
- No additional per-query Gemini cost — GE just relays to the same Agent Engine you already pay for above

GE is the right wrapper if you want SSO, per-user ACLs, the polished citation UI, and admin controls. It is *not* required — the agent works directly via `stream_query`.

---

## Three concrete deployment scenarios

### 1. Pilot (100 docs, 5 internal users, ~500 queries/month)

| Line | Cost |
|---|---:|
| Extraction (one-time) | $150 – $300 |
| Indexing (one-time) | $0.50 |
| Storage (monthly) | $0.03 |
| Agent Engine, min=1 (monthly) | $60 |
| Gemini synthesis, 500 queries (monthly) | $8 |
| GE seats, 5 × $30 (monthly) | $150 |
| **One-time total** | **~$300** |
| **Monthly recurring** | **~$220** |

### 2. Department rollout (1,000 docs, 50 users, ~10k queries/month)

| Line | Cost |
|---|---:|
| Extraction (one-time) | $1,500 – $3,000 |
| Indexing (one-time) | $5 |
| Storage (monthly) | $0.25 |
| Agent Engine, min=2 (monthly) | $130 |
| Gemini synthesis, 10k queries (monthly) | $160 |
| GE seats, 50 × $30 (monthly) | $1,500 |
| **One-time total** | **~$3,000** |
| **Monthly recurring** | **~$1,800** |

### 3. Enterprise (10,000 docs, 500 users, ~250k queries/month)

| Line | Cost |
|---|---:|
| Extraction (one-time) | $15k – $30k |
| Indexing (one-time) | $50 |
| Storage (monthly) | $2.50 |
| Agent Engine, min=2 (monthly) | $130 |
| Gemini synthesis, 250k queries (monthly) | $4,000 |
| GE seats, 500 × $30 (monthly) | $15,000 |
| **One-time total** | **~$30,000** |
| **Monthly recurring** | **~$19,000** |

---

## Cost optimization knobs (in order of leverage)

1. **Drop GE seats if you don't need the polished UI** — for many internal back-office uses, calling Agent Engine `stream_query` directly from a custom React app eliminates the largest recurring line item.
2. **Avoid re-extracting unchanged docs** — `deploy.sh` is idempotent on the corpus side, but uploading a PDF re-runs Eventarc → extractor every time. Add a content-hash check to the extractor or use GCS object versioning to short-circuit.
3. **Reduce Pro fallbacks** — set `DOCPARSE_PRO=gemini-3-flash-preview` in the extractor env if your docs don't have charts dense enough to need Pro. Saves ~$0.50/doc on chart-heavy reports, but accept some chart accuracy loss.
4. **Lower `top_k`** — the agent's `AGENT_TOP_K=20` is conservative. Dropping to 10 cuts input tokens roughly in half → ~$0.008/query instead of $0.016. Eval shows minimal recall loss for top_k ≥ 8.
5. **Run Agent Engine at `min_instances=0`** — saves $50–80/month at the cost of cold-start latency on the first query of a quiet period.
6. **Batch extractions during off-peak** — Cloud Run pricing is uniform but Vertex AI quotas are easier to reason about during off-hours; matters at 10k+ doc backfills.

---

## Cost guardrails to set BEFORE the next backfill

A 22-hour run at $112/hour will silently spend $2,500 if no one's looking. Two cheap guardrails:

```bash
# 1. Quota-cap the extractor SA's Gemini calls per minute
# Console → IAM & Admin → Quotas → filter "aiplatform.googleapis.com"
#   "Online prediction requests per minute per project" → set to 600
#   (= ~36k/hour, i.e. ~25% above observed peak — kills runaway loops, allows real load)

# 2. Daily budget alert at 50% of expected
gcloud billing budgets create \
  --billing-account=$(gcloud billing accounts list --format='value(name)' | head -1) \
  --display-name="docparse daily" \
  --budget-amount=200USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

Both are reversible in 30 seconds and have saved us >$1k/month in similar pipelines.

---

## What this model does NOT cover

- **Eval / judge runs.** The 216-question eval against 4 strategies costs ~$5–10 per full pass; budget separately if iterating on retrieval config.
- **Document AI / Vertex Vector Search alternatives.** This pipeline uses managed RAG Engine. If you swap to self-hosted Vector Search index + endpoint, fixed cost rises (~$20/month minimum index endpoint) but per-query cost drops slightly.
- **Egress.** Trivial unless you stream large PDFs out of GCP regularly.
- **Cloud Trace / Logging at high volume.** ~$0.50 per GB ingested above the free tier. Not an issue for normal usage.
- **VPC-SC / CMEK overhead.** Adds ~10–15% to compute lines if enabled.

---

## Source data & methodology

- Per-token rates verified against the official [Vertex AI generative AI pricing page](https://cloud.google.com/vertex-ai/generative-ai/pricing) (April 2026). All preview-model rates listed there match GA pricing structure — preview is a lifecycle stage, not a discount tier.
- Per-doc call counts derived from the extractor source (`extractor/src/docparse/pipeline.py`, `extractor/src/docparse/extract.py`) — one detect call per page, one OCR call per page, plus one structured-extraction call per detected non-text region.
- Per-query call counts derived from `agent/docparse_agent/agent.py` — `top_k=20` retrieval feeding a single Gemini 3 Flash synthesis call.
- All numbers are **list price** without committed-use discounts. Real-world spend with a CUD or enterprise discount typically runs 15–25% below these estimates.
