---
title: How it works
description: The shared embedding space, segment-level indexing, and rescue captioning explained.
---

## The single trick everything is built on

> Embed the bytes, not the tags.

`gemini-embedding-2-preview` produces a **3072-dim vector** for any of: text, image, short audio clip, or short video clip. Vectors of semantically related media land near each other in cosine distance — regardless of modality. *That's the whole game.*

You can verify this empirically on the homepage's UMAP projection: 300 real assets from the demo, projected to 2D, color-coded by modality. Photos, videos, and graphics overlap heavily. Music sits in its own region (audio embeddings are looser), which is exactly why we cheat on music — see [Rescue captioning](#rescue-captioning) below.

## Segments, not whole files

A 3-minute song or a 60-second drone shot doesn't have *one* vibe — it has several. Indexing the whole file averages everything out and surfaces nothing.

Instead, every asset is **chunked** before embedding:

| Asset type | Segment | Why |
|---|---|---|
| Music / SFX  | 30s windows | A vibe lives in a phrase, not a track. |
| Video        | 4s clips around scene cuts | One shot ≈ one feeling. |
| Photo / SVG  | The whole image | Already a single moment. |

Each segment becomes its own datapoint in Vector Search. The asset's metadata in Firestore points back to the parent — so when a segment matches, the UI can render the parent and seek to the segment's timestamp.

## Rescue captioning (audio's secret sauce)

Raw audio embeddings are *fine* but not great. To boost recall:

1. Send each segment to `gemini-3-flash-preview` with the prompt: *"In one line, describe the mood/scene this audio belongs to."*
2. Embed the caption as text into the same 3072-dim space.
3. Store **both** vectors. At query time, average them.

Result: a query for *"sunset at the beach"* surfaces world-percussion tracks instead of random synthwave.

## Streaming upserts (~7s end-to-end)

The Vector Search index is configured `STREAM_UPDATE`, not `BATCH_UPDATE`. Trade-off: ~2× cost per QPS, but a freshly-uploaded MP3 is queryable in under 10 seconds.

The path:

1. User drops `track.mp3` on the page → POST `/api/upload` → file lands in `gs://<your-ingest-bucket>/ingest/track.mp3`.
2. **Eventarc trigger** fires on `object.finalized` → invokes the ingest Cloud Run service.
3. Ingest service: ffmpeg-cuts segments → captions each (Gemini Flash) → embeds (Gemini Embeddings 2) → upserts datapoints to Vector Search.
4. Firestore writes the segment metadata.
5. Next search query already finds it.

## Why three Gemini models, not one

| Model | Where | Why |
|---|---|---|
| `gemini-embedding-2-preview` | both build & query | The only model that produces multimodal vectors in a shared space. |
| `gemini-3-flash-preview`     | build (rescue captions) | TTFT matters at scale — flash beats pro for short captions. |
| `gemini-3.1-flash-tts-preview` | optional voice-over feature | Native multi-speaker TTS with emotion tags from a single API. |

## Vibe slider (post-search re-rank)

The "warmth / saturation / contrast" sliders on the results page **do not re-query Vector Search**. They re-rank the top-K results client-side using cheap perceptual features extracted at index time and shipped with the metadata. Snappy and free.
