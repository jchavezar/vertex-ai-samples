---
title: Architecture
description: Components, data flow, and the two Cloud Run services.
---

## System diagram

```mermaid
flowchart TB
    subgraph User["User Browser"]
        UI[index_v2.html<br/>+ static/*.js]
    end

    subgraph CloudRun["Cloud Run"]
        APP["app/main.py<br/>FastAPI"]
        INGEST["app/ingest.py<br/>Eventarc handler"]
    end

    subgraph Storage["Storage"]
        GCS[(GCS bucket<br/>envato-vibe-demo)]
        FS[(Firestore<br/>segments/ uploads/)]
    end

    subgraph Vertex["Vertex AI"]
        EMB["gemini-embedding-2-preview<br/>3072-d multimodal"]
        CAP["gemini-3-flash-preview<br/>captioning + rescue"]
        TTS["gemini-3.1-flash-tts-preview<br/>VoiceGen"]
        VS[(Vector Search 2.0<br/>STREAM_UPDATE)]
    end

    UI -- "GET /api/search?q=..." --> APP
    UI -- "POST /api/upload" --> APP
    UI -- "POST /api/create/voice" --> APP
    APP -- "embed (text)" --> EMB
    APP -- "find_neighbors" --> VS
    APP -- "fetch metadata" --> FS
    APP -- "presigned URLs" --> GCS
    APP -- "TTS" --> TTS

    APP -. "drop file" .-> GCS
    GCS == "object.finalized<br/>Eventarc" ==> INGEST
    INGEST -- "ffmpeg cut + thumb" --> GCS
    INGEST -- "rescue caption" --> CAP
    INGEST -- "embed (bytes + caption)" --> EMB
    INGEST -- "write segment doc" --> FS
    INGEST -- "upsert_datapoints" --> VS

    classDef vertex fill:#E8F0FE,stroke:#1A73E8,color:#0A2A6B
    classDef store fill:#FEF7E0,stroke:#F4B400,color:#5A3E00
    classDef cr fill:#E6F4EA,stroke:#0F9D58,color:#0A4724
    class EMB,CAP,TTS,VS vertex
    class GCS,FS store
    class APP,INGEST cr
```

## Two services, one repo

The runtime is **two Cloud Run services** that share a Firestore collection and a Vector Search index.

### `envato-vibe-app` — FastAPI UI
- Source: `app/main.py`, `app/static/`, `app/templates/`
- Build: `deploy/Dockerfile.app`
- Deploy: `bash deploy/deploy_app.sh`
- Endpoints: `/api/search`, `/api/upload`, `/api/segment/*`, `/api/kit/*`, `/api/create/voice`
- Public, no auth (toggle in deploy script if you want IAP)

### `envato-vibe-ingest` — Eventarc handler
- Source: `app/ingest.py` (driver) + `pipeline/build.py` (segment + embed logic)
- Build: `deploy/Dockerfile.ingest`
- Deploy: `bash deploy/deploy_ingest.sh` (also wires the Eventarc trigger on `bucket=$ENVATO_GCS_BUCKET, type=object.finalized, prefix=ingest/`)
- Private, requires Pub/Sub publish permissions for the GCS service agent

## Why STREAM_UPDATE not BATCH

The Vector Search index is configured for streaming upserts.

| Mode | Cost (relative) | Time-to-searchable | Best for |
|---|---|---|---|
| BATCH_UPDATE  | 1×    | hours (rebuild)        | static catalogs |
| STREAM_UPDATE | ~1.5–2× | seconds (incremental) | live drop-zones, demos |

For this demo, the "drop a file → it's searchable" magic is the entire point. STREAM_UPDATE is the right call. For a static 10M-asset catalog, BATCH would be cheaper.

## Why two embedding models in the same space

We don't, actually — both query and indexing use the same model: `gemini-embedding-2-preview`.

What confuses people: at index time, audio is *also* run through `gemini-3-flash-preview` to generate a 1-line caption, and that caption is embedded *too*. Both vectors get stored on the same datapoint. At query time, we average them. This is a recall trick specific to audio (raw audio embeddings cluster less cleanly than image embeddings); it's not a separate model living in a separate space.

## What lives where

| Concern | Lives in | Why |
|---|---|---|
| Asset bytes | GCS         | Cheap, presigned-URL friendly |
| Vectors     | Vector Search index | High-dim ANN search |
| Per-segment metadata | Firestore (`segments/`) | Fast lookup by datapoint id, sub-100ms |
| Per-asset state      | Firestore (`uploads/`)  | Idempotent ingest, dedup by hash |
| Static UI            | Cloud Run (app)         | Same origin as the API |

## What's *not* in this repo

- A custom embedding model. We use Google's stock `gemini-embedding-2-preview`.
- A re-ranker. The vibe-slider re-rank is purely client-side, perceptual features only.
- A vector DB other than Vertex Vector Search. (Pinecone / Weaviate / Qdrant would all work; the abstraction in `pipeline/build.py` is one swap away.)
