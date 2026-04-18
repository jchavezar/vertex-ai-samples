# Envato Vibe Engine — Operational Handoff

## What this is

A production-shaped reference implementation of a multimodal vibe-search engine for a stock-media catalog (photos, videos, music, sound effects, illustrations). The corpus mirrors Envato Elements' shape: ~300 source assets (75 each per modality) expanded to ~1,060 segment-level datapoints. Search uses **Gemini Embeddings 2 (preview, 3072-dim, multimodal, L2-normed)** in a shared text/image/audio/video space, indexed in **Vertex AI Vector Search 2.0** with stream upserts. New uploads land in GCS, fire **Eventarc**, run through the **Cloud Run ingest service**, and become queryable in seconds. Built for the Envato EBC on **2026-04-29**.

## Architecture

```
                  ┌────────────────────────────────────────────┐
  drag/drop  ───► │  POST /api/upload  →  gs://envato-vibe-    │
  in web UI       │                       demo/ingest/<file>   │
                  └────────────────────────────────────────────┘
                                       │
                                       ▼  (object.finalized)
                            ┌────────────────────┐
                            │ Eventarc trigger   │
                            └────────────────────┘
                                       │
                                       ▼
                  ┌────────────────────────────────────────────┐
                  │ Cloud Run: envato-vibe-ingest              │
                  │  ingest_handler.py → process_asset() in    │
                  │  pipeline_v2.py:                           │
                  │   1. ffprobe + plan_segments()             │
                  │   2. ffmpeg cut clip + thumb (per segment) │
                  │   3. upload thumb + clip + original to GCS │
                  │   4. caption (Gemini 3 Flash / 3.1 Lite)   │
                  │   5. embed (gemini-embedding-2-preview,    │
                  │      raw audio/video/image bytes + caption)│
                  │   6. Firestore segments/{datapoint_id}     │
                  │   7. Vector Search upsert_datapoints()     │
                  └────────────────────────────────────────────┘
                                       │
       ┌───────────────────────────────┼────────────────────────────────┐
       ▼                               ▼                                ▼
┌─────────────┐               ┌─────────────────┐              ┌────────────────┐
│ GCS bucket  │               │ Firestore       │              │ Vertex Vector  │
│ originals/  │               │ segments/{id}   │              │ Search 2.0     │
│ segments/   │               │ uploads/{id}    │              │ stream upsert  │
│ thumbnails/ │               │ rich JSON doc   │              │ deployed index │
│ ingest/     │               └─────────────────┘              └────────────────┘
│ (public-RO) │                                                         │
└─────────────┘                                                         │
       ▲                                                                ▼
       │                              ┌─────────────────────────────────────────┐
       │                              │ Cloud Run: envato-vibe-app (FastAPI)    │
       │                              │  app_v2.py                              │
       └──────────────────────────────│   /api/search  → embed → VS → FS getAll │
            (direct https URLs        │   /api/search/sounds-like (audio query) │
             for thumbs, clips,       │   /api/image-to-anything   (image qry)  │
             originals)               │   /api/upload   /api/stats              │
                                      │   /api/segment/{id}  /api/uploads/recent│
                                      └─────────────────────────────────────────┘
                                                       │
                                                       ▼
                                            Browser (templates/index_v2.html
                                            + static/app_v2.js + styles_v2.css)
```

| Layer | Component | File |
|---|---|---|
| Web/API | FastAPI app (search, upload, stats) | `envato/app_v2.py` |
| UI | Dark masonry grid, multi-modal cards | `envato/templates/index_v2.html`, `envato/static/app_v2.js`, `envato/static/styles_v2.css` |
| Ingest worker | Eventarc receiver, calls pipeline | `envato/ingest_handler.py` |
| Pipeline | Segment, caption, embed, upsert | `envato/pipeline_v2.py` |
| Container | Ingest image | `Dockerfile` (root), `envato/requirements.ingest.txt` |
| Deploy | Ingest service + trigger | `envato/deploy_ingest.sh` |

## Live URLs (FILL IN BEFORE DEMO)

| Surface | URL |
|---|---|
| Web app (Cloud Run) | `https://envato-vibe-app-XXXXXX-uc.a.run.app`  ← _fill from `gcloud run services describe envato-vibe-app --region us-central1 --format 'value(status.url)'`_ |
| Ingest service (Cloud Run, internal) | `https://envato-vibe-ingest-XXXXXX-uc.a.run.app` |
| Local dev | `http://localhost:8091` |
| GCS console (bucket) | `https://console.cloud.google.com/storage/browser/envato-vibe-demo` |
| Vector Search index | `https://console.cloud.google.com/vertex-ai/matching-engine/indexes?project=vtxdemos` |
| Firestore segments | `https://console.cloud.google.com/firestore/databases/-default-/data/panel/segments?project=vtxdemos` |

## Service inventory

| Resource | Identifier | Notes |
|---|---|---|
| GCP project | `vtxdemos` (project number `254356041555`) | |
| Region | `us-central1` (captioners on `global`) | |
| GCS bucket | `gs://envato-vibe-demo` | Layout: `ingest/`, `originals/`, `segments/`, `thumbnails/` (public read) |
| Firestore collection | `segments` (~1,060 docs) | doc id = `<asset_id>__seg_NN__t<start>-<end>` |
| Firestore collection | `uploads` | per-upload audit/toast feed |
| Vector Search index | `envato-vibe-multimodal` | 3072-dim, COSINE, STREAM_UPDATE |
| VS endpoint | `envato-vibe-endpoint` (`546600215516282880`) | reused from v1 |
| VS deployed index id | `envato_vibe_multimodal` | |
| Cloud Run | `envato-vibe-app` | FastAPI surface, public |
| Cloud Run | `envato-vibe-ingest` | Eventarc target, internal |
| Eventarc trigger | `envato-vibe-ingest-trigger` | filter: `bucket=envato-vibe-demo`, type `object.v1.finalized` |
| Service account | `envato-vibe-runner@vtxdemos.iam.gserviceaccount.com` | needs: `roles/storage.objectAdmin`, `roles/datastore.user`, `roles/aiplatform.user`, `roles/run.invoker` (for trigger) |

### Embedding + captioning models

| Model | Region | Used for |
|---|---|---|
| `gemini-embedding-2-preview` | `us-central1` | All embeddings (text query, image, audio, video) — 3072 dim, multimodal, single shared space |
| `gemini-3-flash-preview` | `us-central1` | Video segment captions (structured JSON) |
| `gemini-3.1-flash-lite-preview` | `global` | Audio + photo + zero-result rescue captions / rewrites |

## Day-of-demo checklist (run T-30 minutes)

Browser tabs to pin (in order):
1. The web app URL — primary demo surface.
2. GCS console at `gs://envato-vibe-demo/ingest/` — used during the live-ingest act.
3. Cloud Run logs for `envato-vibe-ingest` (`gcloud run services logs tail envato-vibe-ingest --region us-central1`) — to point at while ingest runs.
4. Firestore console on the `segments` collection — for the "this is the document that just got written" beat.
5. Vector Search console — to show endpoint + datapoint count.

Pre-warm queries (run each once so the first user-facing query isn't a cold start):
- `calm cinematic underscore`
- `drone shot of ocean at golden hour`
- `cozy coffee shop morning`
- `upbeat corporate background`

Hit `/api/health` once: confirms Firestore reachability and returns segment count.

Have on local disk for the demo (`~/demo-assets/`):
- `ocean-waves.mp3` (or any 20–30s clip) — for "sounds-like".
- A photo (`coffee-cup.jpg`) — for "image-to-anything".
- A brand-new `.jpg` and a brand-new `.mp3` that are NOT in the corpus — for the live-ingest act.

Fallback if the live ingest stalls (>90s for a video):
- Pivot to "while that's processing, here's what already happened end-to-end on the last upload" — open `/api/uploads/recent?limit=5` in another tab and walk through the elapsed_s field.

## How to add new content (the "production loop")

1. Drop the file directly into the bucket:
   ```bash
   gsutil cp my-photo.jpg gs://envato-vibe-demo/ingest/
   gsutil cp my-track.mp3 gs://envato-vibe-demo/ingest/
   gsutil cp my-clip.mp4  gs://envato-vibe-demo/ingest/
   ```
   Or use `POST /api/upload` from the web UI — it does the same `gs://.../ingest/` write.
2. Eventarc fires within ~1s of object finalization.
3. Watch:
   ```bash
   gcloud run services logs tail envato-vibe-ingest --region us-central1
   ```
4. The handler moves the source from `ingest/` to `originals/` once complete (so the same file isn't reprocessed on retry).
5. Query for it in the web UI — it should appear within seconds of the log line `[ingest] done`.

End-to-end timings observed in production:
| Modality | Wall-clock to queryable |
|---|---|
| Photo (single segment) | ~3.7 s |
| 30 s music track (~2 segments) | ~30 s |
| 30 s video clip (~3 segments) | ~60–150 s |

## How to redeploy

Ingest service (also wires the Eventarc trigger; idempotent):
```bash
cd /home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/semiautonomous-agents/shutter-vibe-engine
./envato/deploy_ingest.sh
```

Web app (deployed by the parallel agent — confirm with them; expected pattern):
```bash
gcloud run deploy envato-vibe-app \
  --source . \
  --region us-central1 \
  --service-account envato-vibe-runner@vtxdemos.iam.gserviceaccount.com \
  --memory 2Gi --cpu 2 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=vtxdemos,GOOGLE_CLOUD_LOCATION=us-central1,ENVATO_GCS_BUCKET=envato-vibe-demo,GOOGLE_GENAI_USE_VERTEXAI=True"
```

To re-process the entire corpus from scratch (one-time, ~30–45 min):
```bash
uv run --python .venv/bin/python envato/pipeline_v2.py            # all 300 assets
uv run --python .venv/bin/python envato/pipeline_v2.py --modality video --limit 5
uv run --python .venv/bin/python envato/pipeline_v2.py --asset-id px-video-9620654 --force
```

## Known limitations (be honest with the audience)

- **Embedding model is `gemini-embedding-2-preview`** — Preview SLA, not GA. Rate limits are tight. If a query 429s during the demo, the FastAPI layer doesn't yet retry — it surfaces the error. Mitigation: pre-warm.
- **Captioner split between regions.** Video uses `gemini-3-flash-preview` in `us-central1`; audio + photo use `gemini-3.1-flash-lite-preview` in `global`. Two clients, two rate-limit pools.
- **Thumbnails for audio are static waveform PNGs.** Not yet "album art with overlay" as discussed in the original plan.
- **No audio hover-preview clip yet** — the UI plays the full segment on click.
- **Eval harness (`/api/eval`) and per-card "why this match" explainer are NOT in `app_v2.py`.** They were in the 12-feature plan but cut for scope. The features that ARE live: cross-modal fan-out (`grouped[]`), sounds-like, image-to-anything, palette filter, tempo/length restricts, zero-result rescue (catalog detour + visual paraphrase), per-search latency telemetry, recent-queries feed.
- **Corpus is ~1,060 datapoints, not 30M.** Latency numbers shown will be wildly better than at production scale. Don't over-claim.
- **SFX coverage is thin** (8 datapoints) — the corpus is mostly music + photos + video, light on stingers.
- **Captions for music are dominated by "uplifting corporate" theme** — Internet Archive seeded it. Some queries will look repetitive in the audio rail; this is corpus-side, not model-side.

## Costs (back-of-envelope, per the locked plan)

| Item | One-time | Recurring |
|---|---|---|
| Captioning the 1,060-segment corpus | ~$5–6 | — |
| Embedding the 1,060-segment corpus | ~$1 | — |
| GCS storage (~2 GB) | — | ~$0.05/mo |
| Vector Search managed endpoint (always-on, stream-update) | — | ~$14/mo |
| Firestore (1K docs, demo traffic) | — | ~free tier |
| Cloud Run (idle) | — | ~$0 |
| **Per query** (1× embed + 1× VS find_neighbors + 1× FS getAll batch) | — | **~$0.0003** |

Demo-day total cost: rounding error.
