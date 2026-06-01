# Path B · BigQuery backend

Cost-optimized nearest-neighbor lookup over **BigQuery `VECTOR_SEARCH`** (brute force, 3072-dim, COSINE) on a 2,103-row clustered table.

## When to choose this path

- < 10 k vectors (brute force scales linearly)
- Cost matters more than p50 — you can tolerate ~700–900 ms warm
- You're running a demo, internal tool, or low-QPS service
- You want SQL semantics for filters (`WHERE modality = ...`) and analytics on the same table

## Cost (this demo, 2,103 vectors)

| Resource | Spec | Monthly |
|---|---|---|
| BigQuery storage | ~50 MB (vectors + 5 string cols) | < $0.01 |
| BigQuery queries | brute-force scan ≤ 50 MB · ~free tier | **~$0** |
| Cloud Run app (`min=0`) | scale-to-zero, kept warm by Scheduler | **~$1** |
| Cloud Scheduler | 2 jobs × 8,640 invocations/mo | ~$0.20 |
| Embeddings (queries) | 1 per user query | usage-based |
| Firestore hydration | 2,103 docs, low QPS | < $1 |
| GCS source assets | ~5 GB Standard | ~$0.10 |
| **Total** | | **~$2 / mo** |

> BigQuery's first 1 TB of query data per month is free. A brute-force scan over a 50 MB clustered table is ~50 MB per query × ~30 k queries/mo = 1.5 GB → free.

## Files

| File | What it does |
|---|---|
| `backend.py` | `find_neighbors()` + `fanout_all()` + `warmup()` — same signature as the Vector Search functions |
| `backfill.py` | One-time copy of 2,103 vectors VS → BQ via `read_index_datapoints` (no re-embedding) |
| `sql/schema.sql` | Table DDL: 6 cols + `CLUSTER BY modality` for filter push-down |
| `deploy/deploy_app_bq.sh` | Cloud Run deploy with `SEARCH_BACKEND=bigquery`, `min=0` |

## Replicate from scratch

```bash
# 1. Create the dataset + table
bq --project_id=vtxdemos --location=us-central1 mk -d your_vibe
bq --project_id=vtxdemos query --nouse_legacy_sql < backends/bigquery/sql/schema.sql

# 2a. If you already have a Vector Search index (Path A), copy it over:
python backends/bigquery/backfill.py
# → reads 2,103 ids from Firestore, calls read_index_datapoints, bulk-loads JSONL

# 2b. If you're starting fresh, point pipeline/build.py at this table instead:
SEARCH_BACKEND=bigquery python pipeline/build.py

# 3. Grant the Cloud Run runner SA read access
gcloud projects add-iam-policy-binding vtxdemos \
  --member="serviceAccount:your-vibe-runner@vtxdemos.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer" --condition=None
gcloud projects add-iam-policy-binding vtxdemos \
  --member="serviceAccount:your-vibe-runner@vtxdemos.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser" --condition=None

# 4. Deploy the app (reuses the existing VS-built image)
bash backends/bigquery/deploy/deploy_app_bq.sh

# 5. Optional: scale-to-zero with warm cache (every 5 min, near-zero cost)
gcloud scheduler jobs create http your-vibe-bq-warmup \
  --project vtxdemos --location us-central1 \
  --schedule '*/5 * * * *' \
  --uri https://your-vibe-app-bq-oyntfgdwsq-uc.a.run.app/api/warmup \
  --http-method GET
```

## Configuration

```bash
SEARCH_BACKEND=bigquery
BQ_TABLE=<PROJECT>.your_vibe.segments    # PROJECT.DATASET.TABLE
GOOGLE_CLOUD_PROJECT=vtxdemos
```

## How the search works

```sql
SELECT base.datapoint_id AS id, distance
FROM VECTOR_SEARCH(
  (SELECT datapoint_id, embedding FROM `<PROJECT>.your_vibe.segments`
   WHERE modality = @modality),                  -- push-down on clustered col
  'embedding',
  (SELECT @q AS embedding),
  top_k => @k,
  distance_type => 'COSINE',
  options => '{"use_brute_force":true}'
)
ORDER BY distance ASC
```

The pre-filter subquery + `CLUSTER BY modality` means a single-modality query scans ~400 rows instead of 2,103. Cosine similarity is `1 - distance`.

## Latency

| Operation | Cold | Warm |
|---|---|---|
| `/api/warmup` | ~1.5 s | ~470 ms |
| Single-modality search | ~1.5 s | 700–900 ms |
| All-modality fan-out (5 modalities, parallel) | ~2.5 s | 1.4–1.9 s |

Cold = first request after Cloud Run scaled to zero. Scheduler keep-alive every 5 min keeps things in the warm column.

## Status in this repo

> **Live as of 2026-04-20.** Both `your-vibe-app` and `your-vibe-app-bq` Cloud Run services run this backend. The Vector Search index has been torn down. See [`docs/COST_ANALYSIS.md`](../../docs/COST_ANALYSIS.md) for the full delta.

## See also

- Cost comparison: [`docs/COST_ANALYSIS.md`](../../docs/COST_ANALYSIS.md)
- Sibling path: [`backends/vector-search/`](../vector-search/)
- Dispatcher: [`app/main.py`](../../app/main.py) → `vs_find_neighbors()`
