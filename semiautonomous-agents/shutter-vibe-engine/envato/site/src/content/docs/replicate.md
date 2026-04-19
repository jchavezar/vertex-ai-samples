---
title: Replicate this in 5 minutes
description: From clone to first search, end-to-end.
---

The point of this repo is that you can clone it, point it at your GCP project, and have multimodal vibe search running in under five minutes.

## 0. Prerequisites

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=<your-project>
export GOOGLE_CLOUD_LOCATION=us-central1
export ENVATO_GCS_BUCKET=<your-bucket>
```

You'll need:

- A GCP project with **Vertex AI**, **Cloud Run**, **Firestore (Native)**, **Eventarc**, and **GCS** APIs enabled.
- A service account `envato-vibe-runner@<project>.iam.gserviceaccount.com` with `roles/aiplatform.user`, `roles/datastore.user`, `roles/storage.admin`.

## 1. Clone

```bash
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/shutter-vibe-engine/envato
```

## 2. Build the index from the bundled sample assets

```bash
pip install -r app/requirements.txt -r deploy/requirements.ingest.txt
python pipeline/build.py
```

This will:

- Walk `assets/` (~50 sample files across 5 modalities)
- Cut segments, generate rescue captions, embed each
- Create a Vector Search index `envato-vibe-multimodal` if missing
- Stream-upsert datapoints
- Write segment metadata to Firestore (`segments/` collection)

First run takes ~5 minutes. Subsequent runs are incremental.

## 3. Run locally

```bash
cd app && uvicorn main:app --reload --port 8080
open http://localhost:8080
```

Try `tropical beach getaway` in the search box.

## 4. Deploy to Cloud Run

```bash
bash deploy/deploy_app.sh      # FastAPI UI
bash deploy/deploy_ingest.sh   # Eventarc-triggered ingest service
```

## 5. Add your own assets (live)

Drop any `.jpg`, `.mp3`, `.mp4`, or `.svg` into `gs://<your-bucket>/ingest/`. The Eventarc trigger fires, the ingest service segments + captions + embeds + upserts, and the asset is searchable in **~7 seconds**.

```bash
gsutil cp my-photo.jpg gs://${ENVATO_GCS_BUCKET}/ingest/
```

## Common pitfalls

- **`PERMISSION_DENIED` from Vector Search** — the runner SA needs `roles/aiplatform.user`. Vector Search permissions are granular; if you see this on `find_neighbors`, the role is missing.
- **`gemini-3-flash-preview` 404** — region matters. Use `us-central1` or `global`. Check the [Gemini model regional availability](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models#gemini).
- **Firestore in Datastore mode** — won't work. Must be **Native mode**.
- **Eventarc trigger never fires** — bucket must be in the same region as the trigger. Cross-region triggers fail silently.

## Operational docs

For full deployment, monitoring, and runbook details, see [`docs/DEPLOYMENT.md`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/shutter-vibe-engine/envato/docs/DEPLOYMENT.md) in the repo.
