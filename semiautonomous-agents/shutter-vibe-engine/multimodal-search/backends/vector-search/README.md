# Path A · Vector Search backend

Production-grade nearest-neighbor lookup over **Vertex AI Vector Search** (TREE_AH ANN, 3072-dim, COSINE).

> This folder is intentionally a marker + docs. The actual code lives at the top level (`app/`, `pipeline/`, `deploy/`) because Vector Search was the *original* path — the BigQuery path was extracted later as a sibling.

## When to choose this path

- > 100 k vectors, or you expect to grow there
- p50 < 100 ms is a hard requirement (live UX, agent loops)
- You need always-warm responses (no cold-start tolerance)
- Filtering is simple equality (modality, tempo bucket, length bucket)

## Cost (this demo, 2,103 vectors)

| Resource | Spec | Monthly |
|---|---|---|
| Vector Search index node | `automaticResources` default = `e2-standard-2` 24 × 7 | **~$68** |
| Index build storage | ~50 MB shard | ~$0.01 |
| Embeddings (ingest) | 2,103 × `gemini-embedding-2-preview` (one-shot) | < $1 |
| Embeddings (queries) | 1 per user query | usage-based |
| Cloud Run app (`min=1`) | 2 vCPU / 2 GiB always warm | **~$50** |
| Cloud Run ingest (Eventarc) | scale-to-zero, ~rare | < $1 |
| Firestore hydration | 2,103 docs, low QPS | < $1 |
| GCS source assets | ~5 GB Standard | ~$0.10 |
| **Total** | | **~$137 / mo** |

The Vector Search node dominates. Going to scale-to-zero is *not* an option — the endpoint must stay deployed for the SLA to hold.

## Replicate

```bash
# 1. Build the index (creates index + endpoint, deploys)
python pipeline/build.py --create-index --deploy

# 2. Wait for deploy (~20 min for 3072-d, TREE_AH)
gcloud ai index-endpoints describe ENDPOINT_ID --region=us-central1

# 3. Ingest assets (writes to VS + Firestore + GCS)
python pipeline/build.py

# 4. Deploy the FastAPI app (default SEARCH_BACKEND=vector-search)
bash deploy/deploy_app.sh
bash deploy/deploy_ingest.sh   # Eventarc-triggered ingest service
```

## Configuration

The app dispatches to this backend when `SEARCH_BACKEND=vector-search` (default). The endpoint id and deployed-index id are read from env in [`app/main.py`](../../app/main.py):

```bash
VS_ENDPOINT_ID=546600215516282880
VS_DEPLOYED_ID=envato_vibe_multimodal
```

Search code: `app/main.py` → `_vs_find_neighbors_native()`

## Status in this repo

> The Vector Search index for this demo (`9202325185275887616`) and its endpoint (`546600215516282880`) were **torn down on 2026-04-20** to save the $137/mo while the BigQuery path serves the live demo. To re-deploy, run the steps above — `pipeline/build.py` is idempotent and re-uses the same Firestore + GCS state.

## See also

- Cost comparison: [`docs/COST_ANALYSIS.md`](../../docs/COST_ANALYSIS.md)
- Sibling path: [`backends/bigquery/`](../bigquery/)
