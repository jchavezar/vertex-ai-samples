# Cost analysis · Vector Search vs. BigQuery backend

> Snapshot: **2026-04-20**, after migrating the live demo from Vertex AI Vector Search to BigQuery `VECTOR_SEARCH`. All prices are `us-central1` list, demo workload is **2,103 segments** in a 3072-dim embedding space.

## TL;DR

| Path | Engine | Monthly | p50 latency | Use when |
|---|---|---:|---|---|
| **A · Vector Search** | TREE_AH ANN, `e2-standard-2` 24×7 | **~$137** | 40–80 ms | Production, > 100 k vectors |
| **B · BigQuery** ✅ live | brute force `VECTOR_SEARCH` | **~$2** | 700–900 ms warm | Demos, ≤ 10 k vectors |
| **Delta** | | **−$135 / mo (−98 %)** | +700 ms | |

The BigQuery path costs ~1.5 % of the Vector Search path while keeping every UI feature (filters, fan-out, hydration, snippets, 3D viz, voiceover) identical. The latency penalty is a single round-trip — invisible during a live demo.

---

## Path A · Vector Search — line items

| Resource | Spec | Hours / mo | Unit price | Monthly |
|---|---|---:|---|---:|
| Vector Search index node | `automaticResources` default `e2-standard-2` (2 vCPU / 8 GiB) | 730 | $0.0938 / hr | **$68.47** |
| Vector Search storage | ~50 MB index shard | — | $0.0001 / MB-hr | $0.01 |
| Cloud Run app | 2 vCPU / 2 GiB, `min-instances=1` (always warm) | 730 | $0.0686 / hr (CPU+mem) | **~$50** |
| Cloud Run ingest | scale-to-zero, ~5 invocations / day | — | usage | < $1 |
| Embeddings (ingest) | 2,103 × `gemini-embedding-2-preview` (one-shot) | — | tokens | < $1 |
| Embeddings (queries) | 1 per user query | — | tokens | usage |
| Firestore hydration reads | 2,103 docs total, low QPS | — | $0.06 / 100 k reads | < $0.50 |
| GCS source assets | ~5 GB Standard | — | $0.020 / GB-mo | $0.10 |
| Cloud Build (occasional) | image rebuilds | — | first 120 min/day free | $0 |
| **Total** | | | | **~$137** |

> **Why so high?** The Vector Search node cannot scale to zero — it backs an SLA-bound endpoint. And the Cloud Run app keeps `min=1` to match the always-warm posture.

---

## Path B · BigQuery — line items

| Resource | Spec | Monthly |
|---|---|---:|
| BigQuery storage | ~50 MB (vectors as `ARRAY<FLOAT64>` + 5 string cols + `ingest_ts`) | < **$0.01** |
| BigQuery queries | brute-force scan ≤ 50 MB · ~30 k queries/mo = ~1.5 GB · first 1 TB free | **~$0** |
| Cloud Run app `your-vibe-app` | 2 vCPU / 2 GiB, `min=0`, kept warm by Scheduler | **~$1** |
| Cloud Run app `your-vibe-app-bq` | identical, kept as a sibling for comparison | **~$1** |
| Cloud Scheduler | 2 jobs × `*/5 * * * *` = 8,640 invocations/mo each | $0.20 |
| Cloud Run ingest | unchanged | < $1 |
| Embeddings (ingest) | unchanged (2,103 one-shot) | < $1 |
| Embeddings (queries) | unchanged | usage |
| Firestore hydration | unchanged | < $0.50 |
| GCS source assets | unchanged (~5 GB) | $0.10 |
| **Total** | | **~$2** |

> **Why so low?** BQ vector storage is just bytes-in-table (cheap), and the brute-force scan runs entirely inside the free monthly query tier at this volume. Cloud Run scaled to zero between requests; the `*/5 min` keep-alive is enough to keep first-search latency under 1 s.

---

## What changed in the architecture

```
                BEFORE                                      AFTER
  ┌─────────────────────────┐                ┌─────────────────────────┐
  │  Cloud Run (min=1)      │                │  Cloud Run (min=0)      │
  │  ▼                      │                │  ▼   warmup every 5 min │
  │  Vector Search endpoint │                │  BigQuery VECTOR_SEARCH │
  │  ▼ (e2-standard-2 24×7) │                │  ▼ (serverless)         │
  │  Index 9202325185...    │                │  your_vibe.segments   │
  │  Endpoint 5466002155... │                │  CLUSTER BY modality    │
  └─────────────────────────┘                └─────────────────────────┘
   $137 / mo                                  $2 / mo
```

Identical pieces (unchanged in either path):

- `gemini-embedding-2-preview` for the 3072-d query and document vectors
- Firestore for rich hydration metadata (caption, GCS URIs, license, contributor)
- GCS for source assets
- `pipeline/build.py` for ingest enrichment (Gemini captions per modality)
- The entire FastAPI UI, snippet overlay, 3D viz, voiceover

Only the nearest-neighbor lookup differs.

---

## Latency comparison

Measured 2026-04-20 against the live demo, warm path, single user.

| Operation | Path A (VS) | Path B (BQ) |
|---|---:|---:|
| Embed query (`gemini-embedding-2-preview`) | ~600 ms | ~700 ms |
| Single-modality nearest neighbors (k=20) | 40–80 ms | 700–900 ms |
| All-modality fan-out (5 modalities, parallel) | 100–200 ms | 1.4–1.9 s |
| Firestore hydration of top 60 | ~60 ms | ~60 ms |
| **End-to-end `/api/search?modality=all`** | **~1.0 s** | **~1.9 s** |

The added latency is one extra round-trip to a serverless slot. Imperceptible in a demo, noticeable in a real UX — that's the whole tradeoff.

---

## When this conclusion would flip

Move back to Path A when **any** of these is true:

- Vector count > 50 k (brute force becomes painfully slow on cold slots)
- Query QPS > a few per second sustained (BQ slot contention starts to bite)
- p95 < 500 ms is a contractual / UX requirement
- You need ANN semantics that brute force can't provide (e.g., huge k)

Until then, **stay on Path B**. The reverse migration is `bash deploy/deploy_app.sh` + `python pipeline/build.py --create-index --deploy` — the embeddings are already in BigQuery, so re-population of the VS index is a single read query.

---

## Reproducing these numbers

- **Vector Search node price**: [Vertex AI Vector Search pricing](https://cloud.google.com/vertex-ai/pricing#matchingengine) → `automaticResources` defaults to `e2-standard-2`, billed per node-hour.
- **Cloud Run pricing**: [Cloud Run pricing](https://cloud.google.com/run/pricing) — vCPU + memory only billed during request handling at `min=0`.
- **BigQuery pricing**: [BigQuery on-demand pricing](https://cloud.google.com/bigquery/pricing#on_demand_pricing) — first 1 TB queries / mo free; storage at $0.02/GB-mo.
- **Live state**: `gcloud run services describe your-vibe-app --region=us-central1 --project=vtxdemos` confirms `SEARCH_BACKEND=bigquery`, `min-instances=0`.
