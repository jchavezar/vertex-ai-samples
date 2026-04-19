# Vibe Search — Vector Search Deployment Log

End-to-end record of provisioning the demo on Vertex AI Vector Search in the
`vtxdemos` project for the EBC session on **2026-04-29**.

---

## 0. Starting state

- 200 indexed assets (50 each across photo / video / graphic / audio).
- Originals in `gs://<your-ingest-bucket>` (private, uniform IAM).
- App (`app/main.py`) doing **local NumPy** brute-force search over a 200×3072
  matrix loaded from `archive/v1/asset_index.npz`.
- No Vector Search index or endpoint in the project.

This document records the steps to (a) widen the corpus, (b) provision a real
Vertex AI Vector Search index + endpoint, (c) cut the FastAPI app over to the
managed endpoint, and (d) prove the new wiring works.

---

## 1. Widen the corpus (50 → 75 per modality)

**Why**: the EBC briefing flags 14 content types. We can't ship all 14 in a
week, but adding more variety per modality makes both the strong-match and
rescue paths land on more interesting items, and gives the Vector Search story
a non-trivial number of vectors (300+ instead of 200).

**Files touched**:

- `pipeline/build.py` — `QUERY_PACKS` extended with **5 new theme queries per
  modality**, covering content gaps from the briefing:
  - **Photos** added: family/pets, fitness/yoga, winter villages, industrial
    workspaces, weddings.
  - **Videos** added: logo reveals, lower-third graphics, particle backgrounds,
    intro motion graphics, data-viz animations (proxy for the *Video Templates*
    content type).
  - **Graphics** added: typography quotes, social-media post templates,
    presentation slides, mobile UI screens, hero web banners (proxy for the
    *Graphic Templates* and *Web Templates* content types).
  - **Audio** added: rain/thunder SFX, footsteps, whoosh transitions, crowd
    applause, vintage radio static (proxy for the *Sound Effects* content type).

**Command**:

```bash
export PEXELS_API_KEY=...                    # already set in shell
export PIXABAY_API_KEY=...
.venv/bin/python -m pipeline.build --target-per-mod 75 --gcs
```

**Result** (verified after the run completed in 38.6 s of embed time):

| Modality | Before | After |
|----------|--------|-------|
| Photo    | 50     | 75    |
| Video    | 50     | 75    |
| Graphic  | 50     | 75    |
| Audio    | 50     | 75    |
| **Total**| **200**| **300** |

NPZ footprint after embed: `index/asset_index.npz` = 3,600 KB
(300 vectors × 3072 dims × float32). GCS bucket grew by ~125 new media
files (originals + video posters).

---

## 2. Patch `pipeline.py` for STREAM_UPDATE

**Why**: the SDK default for `MatchingEngineIndex.create_tree_ah_index` is
`BATCH_UPDATE`, which means every catalog change requires re-staging an NPZ to
GCS and waiting 20-40 minutes for the index to rebuild. For a creative-asset
catalog where contributors upload constantly, we want **streaming upserts**:
new vectors queryable in seconds.

**Change** (`pipeline.py:push_to_vector_search`):

```python
index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name=INDEX_DISPLAY_NAME,
    dimensions=int(vectors.shape[1]),
    approximate_neighbors_count=150,
    distance_measure_type="COSINE_DISTANCE",
    leaf_node_embedding_count=500,
    leaf_nodes_to_search_percent=10,
    index_update_method="STREAM_UPDATE",   # ← was the default BATCH_UPDATE
    description="Vibe Search — Gemini Embedding 2 multimodal demo index",
)
```

The companion change drops the JSONL-via-GCS staging path (only used by
`BATCH_UPDATE`) and switches to direct streaming upserts:

```python
from google.cloud.aiplatform_v1.types.index import IndexDatapoint

datapoints = [
    IndexDatapoint(
        datapoint_id=aid,
        feature_vector=vec.tolist(),
        restricts=[
            IndexDatapoint.Restriction(namespace="modality",
                                       allow_list=[m["category"]]),
            IndexDatapoint.Restriction(namespace="sub_category",
                                       allow_list=[m["sub_category"]]),
        ],
    )
    for aid, vec in zip(ids, vectors)
]
for chunk in batch(datapoints, 100):           # API limit: 100 per call
    index.upsert_datapoints(datapoints=chunk)
```

**Trade-off**: STREAM_UPDATE indexes have a slightly higher per-vector cost than
BATCH_UPDATE, but for a 300-item demo (or even a 60M-item production catalog)
the latency win is decisive. the prod catalog churn — new contributor
uploads every few seconds — *requires* streaming.

---

## 3. Provision the index + endpoint (the slow leg)

**Command** (foreground OK — pipeline is idempotent and will resume):

```bash
.venv/bin/python -m pipeline.build --target-per-mod 75 --gcs --vector-search
```

**Sequenced operations and timings**:

| Op | Typical time | Notes |
|---|---|---|
| `MatchingEngineIndex.create_tree_ah_index(STREAM_UPDATE)` | ~5-10 min | One-time per index. Returns a long-running operation. |
| `MatchingEngineIndexEndpoint.create(public_endpoint_enabled=True)` | seconds | Public endpoint = simplest demo path. Lock down with VPC SC + private endpoint for prod. |
| `endpoint.deploy_index(index, deployed_index_id="envato_vibe_multimodal")` | ~30-60 min | Provisions ANN-serving VMs in `us-central1`. Idle cost ~$0.50/hr — tear down after the EBC. |
| `index.upsert_datapoints(...)` × ceil(N/100) | seconds total | Streaming. New vectors queryable within ~5 s. |

**Resource names produced** (captured live during this run):

```
index    = projects/254356041555/locations/us-central1/indexes/9202325185275887616
endpoint = projects/254356041555/locations/us-central1/indexEndpoints/546600215516282880
deployed_index_id = envato_vibe_multimodal
```

Long-running operation (LRO) for the deploy:

```
projects/254356041555/locations/us-central1/indexEndpoints/546600215516282880/operations/4320826890362290176
```

Poll status with:

```bash
.venv/bin/python -c "
from google.cloud import aiplatform
aiplatform.init(project='vtxdemos', location='us-central1')
ep = aiplatform.MatchingEngineIndexEndpoint('projects/254356041555/locations/us-central1/indexEndpoints/546600215516282880')
for d in ep.deployed_indexes:
    print(d.id, '→', d.index)
"
```

**Verify in console**:
- https://console.cloud.google.com/vertex-ai/matching-engine/indexes?project=vtxdemos
- https://console.cloud.google.com/vertex-ai/matching-engine/index-endpoints?project=vtxdemos

---

## 4. Cut `app.py` over to the managed endpoint

**Files touched**: `app/main.py`

The new `vector_search()` first attempts the managed endpoint and falls back
to local NumPy if the endpoint is not yet deployed (so the demo works the
moment the index finishes provisioning, with no code change).

**Endpoint resolver — cached, with negative-result TTL** (`app.py:_resolve_endpoint`):

```python
ENDPOINT = None
_ENDPOINT_RECHECK_AT = 0.0
_ENDPOINT_RECHECK_INTERVAL = 60.0   # don't re-probe Vertex on every search

def _resolve_endpoint():
    global ENDPOINT, _ENDPOINT_RECHECK_AT
    if ENDPOINT is not None:
        return ENDPOINT
    if time.time() < _ENDPOINT_RECHECK_AT:
        return None
    _ENDPOINT_RECHECK_AT = time.time() + _ENDPOINT_RECHECK_INTERVAL
    from google.cloud import aiplatform
    aiplatform.init(project=PROJECT, location=LOCATION)
    eps = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"')
    if not eps or not any(d.id == DEPLOYED_INDEX_ID for d in eps[0].deployed_indexes):
        return None
    ENDPOINT = eps[0]
    return ENDPOINT
```

**Search call** (`app.py:_vector_search_remote`):

```python
def _vector_search_remote(q_vec, k, modality):
    ep = _resolve_endpoint()
    if ep is None:
        return None
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
        Namespace,
    )
    over_k = k * 4 if modality is None else k
    kwargs = dict(
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[q_vec.tolist()],
        num_neighbors=over_k,
    )
    if modality:
        kwargs["filter"] = [Namespace(name="modality", allow_tokens=[modality])]
    response = ep.find_neighbors(**kwargs)
    hits = [(n.id, 1.0 - float(n.distance)) for n in response[0]]   # cos = 1 - dist
    if modality is None and MODALITY_BIAS:
        hits = [(aid, score + MODALITY_BIAS.get(MANIFEST[aid]["category"], 0.0))
                for aid, score in hits]
        hits.sort(key=lambda x: -x[1])
    return hits[:k]
```

The `MANIFEST` dict stays loaded locally for hydration (asset metadata,
thumbnail paths). Only the *similarity search* moves to Vector Search.

**Also dropped** the `expand_query_concepts` Gemini-Flash hop in `build_rescue`
— vector search itself is the semantic-neighborhood expansion. The rescue panel
now has just two strategies (catalog detour + visual paraphrase), both of which
are pure vector lookups. The redundant re-embed of the original query inside
`build_rescue` is also gone (the query vector is now passed in from
`/api/search`). Net effect: rescue-path latency **5,500 ms → 250 ms**.

---

## 5. Smoke tests

After deploy + cutover, prove the demo still works end-to-end.

```bash
# Server up?
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8090/

# Strong-match path — should be STRONG MATCH, total ~280 ms
curl -s "http://127.0.0.1:8090/api/search?q=cozy+coffee+shop+morning" \
  | jq '.summary // .timings_ms, .best_score, .results[:2] | .[]?.asset_id'

# Rescue path — should be LOW CONFIDENCE + 3 strategies + Generate-it CTA
curl -s "http://127.0.0.1:8090/api/search?q=viking+longship+invading+medieval+castle" \
  | jq '.timings_ms, .best_score, .rescue.strategies[].headline'

# Modality filter — should only return audio
curl -s "http://127.0.0.1:8090/api/search?q=lofi+chill&modality=audio" \
  | jq '.results[].category' | sort -u
```

**Measured timings** (on the local-fallback path with caching fix, while the
managed endpoint is provisioning):

| Path | Embed (Gemini) | Vector search | Rescue extras | Total |
|------|---------------:|--------------:|--------------:|------:|
| Strong match (cold)         | 1,275 ms | 8 ms  | – | 1,283 ms |
| Strong match (warm)         |   258 ms | 11 ms | – |   270 ms |
| Low-confidence (with rescue)|   216 ms | 4 ms  | 30 ms | **250 ms** |

The rescue path went from **5,500 ms → 250 ms** by removing the LLM-based
"concept neighbours" expansion (vector search itself is the semantic
neighborhood) and dropping the redundant re-embed of the original query.

Once the managed endpoint is reachable, `vector_search` automatically routes
to `endpoint.find_neighbors()`. Expected timings on the managed endpoint:

| Path | Embed (Gemini) | VS find_neighbors | Total |
|------|---------------:|------------------:|------:|
| Strong match | ~250 ms | ~10-20 ms | ~270 ms |
| Low confidence (with rescue) | ~250 ms | ~30-50 ms (5 calls in rescue) | ~310 ms |

---

## 6. Continuous catalog updates (the streaming story)

After the index is deployed, adding a new asset is one call:

```python
from google.cloud.aiplatform_v1.types.index import IndexDatapoint

new_vec = embed_visual(new_item)              # ~250 ms (Gemini)
INDEX.upsert_datapoints(datapoints=[
    IndexDatapoint(
        datapoint_id=new_item["asset_id"],
        feature_vector=new_vec.tolist(),
        restricts=[
            IndexDatapoint.Restriction(namespace="modality",
                                       allow_list=[new_item["category"]]),
        ],
    ),
])
# new_item is queryable in ~5 s — no rebuild, no redeploy
```

Deletes are equally cheap:

```python
INDEX.remove_datapoints(datapoint_ids=[asset_id])
```

This is the EBC's "no batch reindex window" story.

---

## 7. Tear-down (post-EBC)

The endpoint accrues hourly cost while up. After the session:

```bash
.venv/bin/python << 'PY'
from google.cloud import aiplatform
aiplatform.init(project="vtxdemos", location="us-central1")

for ep in aiplatform.MatchingEngineIndexEndpoint.list(
        filter='display_name="envato-vibe-endpoint"'):
    for d in ep.deployed_indexes:
        ep.undeploy_index(deployed_index_id=d.id)
    ep.delete()

for ix in aiplatform.MatchingEngineIndex.list(
        filter='display_name="envato-vibe-multimodal"'):
    ix.delete()
PY
```

The `gs://<your-ingest-bucket>` bucket and the local NPZ stay around — those are
free at this size and rebuilding the index from them is one `--vector-search`
re-run.

---

## 8. Current status (live snapshot)

| Step | Status |
|------|--------|
| QUERY_PACKS expanded with 5 new themes per modality | ✅ done |
| `pipeline.py` patched for `STREAM_UPDATE` + `index.upsert_datapoints` | ✅ done |
| Harvest + embed → 300 assets in `manifest.json`, vectors in NPZ | ✅ done |
| 125 new originals uploaded to `gs://<your-ingest-bucket>` | ✅ done |
| `MatchingEngineIndex` created (STREAM_UPDATE) | ✅ done |
| `MatchingEngineIndexEndpoint` created (public) | ✅ done |
| `endpoint.deploy_index(...)` LRO | ⏳ in progress (~30-60 min) |
| Stream-upsert 300 vectors via `index.upsert_datapoints(...)` | ⏳ blocks on deploy |
| `app.py` cut over to `endpoint.find_neighbors()` (with auto-fallback) | ✅ done — auto-promotes on next 60s poll once deploy completes |

The FastAPI app is **already running** and currently using the local-NumPy
fallback. As soon as `endpoint.deploy_index` finishes, the next `/api/search`
call within 60 s will detect the deployed index and switch to remote mode
silently — no restart required.

**Verify post-deploy:**
```bash
curl -s http://127.0.0.1:8090/api/stats | jq '.backend, .endpoint, .deployed_index_id'
# expected:
#   "vertex_vector_search"
#   "projects/254356041555/locations/us-central1/indexEndpoints/546600215516282880"
#   "envato_vibe_multimodal"
```

## 9. Files of record

| File | Role |
|------|------|
| `pipeline/build.py` | Single source of truth: harvest → download → GCS → embed → NPZ → Vector Search |
| `app/main.py` | FastAPI app with rescue logic. Queries Vector Search endpoint. |
| `app/templates/index_v2.html` | UI (search box, modality filter, audio cards, Generate-it CTA) |
| `assets/manifest.json` | Per-asset metadata (id, caption, tags, license, GCS URI) |
| `archive/v1/asset_index.npz` | Local fallback (not used in prod path) |
| `docs/DEPLOYMENT.md` | This document |
