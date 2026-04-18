# Envato EBC — Demo Run-of-Show

**Audience:** Envato product + engineering leadership
**Date:** Wednesday 2026-04-29
**Total runtime target:** 12–14 minutes for the live portion, plus ~8 min Q&A
**Headline story:** *"This is a working slice of your catalog where the search bar speaks photo, video, music, and SFX in the same multimodal vector space — and a new upload becomes searchable in seconds."*

---

## Pre-demo setup (T-5 minutes before walking on)

1. **Open these tabs in this order** so the muscle memory of `Cmd+1..5` lines up:
   1. Web app at the Cloud Run URL (or `http://localhost:8091` if running off your laptop).
   2. GCS console showing `gs://envato-vibe-demo/ingest/` (empty).
   3. Terminal tailing ingest logs:
      ```bash
      gcloud run services logs tail envato-vibe-ingest --region us-central1
      ```
   4. Firestore console on the `segments` collection.
   5. (optional) Vector Search index page showing datapoint count.

2. **Pre-warm queries** (so first-touch latency isn't a cold start):
   - `calm cinematic underscore`
   - `drone shot of ocean at golden hour`
   - `cozy coffee shop morning`

3. **On disk, in `~/demo-assets/`:**
   - `mystery-track.mp3` — a 20–30s clip NOT in the corpus, for the "sounds-like + ingest" act.
   - `coffee-shot.jpg` — a photo NOT in the corpus.
   - `client-photo.jpg` — any cozy/warm-toned still for image-to-anything.

4. **Confirm health:** open `/api/health` in a tab — should return `{"ok": true, "stats": {"segments_indexed": ~1060}}`.

---

## Opening hook — 60 seconds

> "Before I show you anything, here's the only sentence that matters today. Your catalog has tens of millions of assets across photos, video, music, and SFX. Today, every one of those modalities is searched by a different system, indexed by different metadata, and stitched together at the UI. **What we're going to demo is one search system that speaks all four — because Gemini Embeddings 2 puts them in the same vector space.** A user types `morning coffee`, and we hand them the photo, the video loop, the music track, AND the cafe ambience SFX, ranked together, in a single round-trip. That's the whole pitch. Now let me show you it actually works."

Click into the web app.

---

## Act 1: text → mixed media (the basic vibe search) — 3 minutes

**Goal:** establish that one query returns four modalities at once, and that what comes back is *moments* (segments), not whole assets.

### Query 1 — `cozy coffee shop morning`
- **What the audience sees:** photos of latte art and warm window light, a video loop of macro coffee pouring, an acoustic-folk-guitar music segment, and a corporate-uplifting track. All in a single grid, grouped by modality.
- **Narration while it loads:** "I just typed three words. Behind the scenes: that text was embedded by Gemini Embeddings 2 — same model, same 3072-dimensional space — and we ran one nearest-neighbor query against Vertex Vector Search. No keyword matching. No tag taxonomy. Pure semantic similarity in a shared multimodal space."
- **Point at the latency card:** "Embed: ~280ms. Vector Search: ~10ms. Firestore hydrate: ~15ms. End to end about 300 milliseconds."

### Query 2 — `drone shot of ocean at golden hour`
- **What they see:** ocean waves slow-motion clips dominate the video rail, tropical beach drone aerials in photos, ambient cinematic underscore in audio.
- **Narration:** "Notice the video rail isn't returning *whole videos* — those are 10-second segments. If a contributor uploaded a 90-second drone reel, we indexed nine windows with 2-second overlap, so we can find the exact moment the camera tilts down, not just the asset that contains it."

### Query 3 — `neon cyberpunk street`
- **What they see:** neon sign night videos, neon cyberpunk street photos, electronic synthwave music. Cross-modal coherence on a *vibe*, not a literal noun.
- **Narration:** "We never told the system 'synthwave goes with neon streets.' That alignment lives in the embedding model — the audio bytes for that synthwave track are projected into the same 3072-dim space as the pixels of those neon signs. That's the multimodal magic."

### Query 4 — `sad rainy day`
- **What they see:** moody photos (low-key lighting), slow ambient music, snow-falling slow-motion video standing in for melancholy.
- **Narration:** "This one is interesting because there's no tag in the catalog for 'sad.' The model is reading mood from pixel statistics and instrumentation — minor key, low energy, low saturation imagery."

---

## Act 2: image → anything (cross-modal from a reference photo) — 2.5 minutes

**Goal:** show that the *query* can be any modality — drop a photo, get back music + video + photos that match the *vibe* of the photo.

### Action
- Drag `client-photo.jpg` (warm cafe latte still) into the upload zone OR click the image-search icon.
- Hits `POST /api/image-to-anything`.

### What they see
- Photos visually similar (warm tones, shallow DOF, latte art).
- Video segments of coffee pouring, candle flame close-ups.
- **Audio segments** — acoustic folk guitar, jazz piano improvisation. The system found *music that feels like the photo*.

### Narration
> "I just embedded a JPEG. Same model, same 3072-dim space. The query vector landed near photos that share the visual style, but ALSO near audio segments whose embeddings encode 'warm, intimate, slow tempo.' This is what we mean by *true* multimodal — the audio and the image were never compared via a translated caption. Their raw bytes were embedded directly and the cosine similarity is meaningful across the modality boundary."

> "For an Envato user this means: a designer working on a brand mood-board can drop their hero photo into the music tab and find the soundtrack that scores it. Same gesture, no manual cross-referencing."

---

## Act 3: sounds-like (audio query → similar audio) — 2 minutes

**Goal:** show the third query modality — upload an audio file, get similar audio.

### Action
- Drag `mystery-track.mp3` (a 25-second clip — pick something with clear character: lofi beat, or ambient pad) into the audio search zone.
- Hits `POST /api/search/sounds-like`.

### What they see
- Top hits: music segments matching genre/mood/tempo. Lofi → other lofi. Ambient pad → ambient cinematic underscore segments.
- The result cards show timestamps — `t60-90s` — proving these are *moments inside* longer tracks, not whole-track matches.

### Narration
> "The mp3 bytes were embedded directly — Gemini Embeddings 2 listens to audio. No transcription, no genre classifier in front of it. The 3072-dim vector this produced lands next to vectors of *segments* of other songs that sound similar — same instrumentation, same tempo, same mood."

> "For Envato: 'find me music that sounds like this rough cut my client sent.' That's a query you couldn't type before. Now it's a drop target."

---

## Act 4: live ingest (the production loop) — 3 minutes

**Goal:** prove this isn't a static demo — the ingestion path works end-to-end, and a brand-new asset becomes queryable in seconds.

### Action
1. Pull up the GCS tab. Show that `gs://envato-vibe-demo/ingest/` is empty.
2. Pull up the ingest logs terminal.
3. From a third terminal:
   ```bash
   gsutil cp ~/demo-assets/coffee-shot.jpg gs://envato-vibe-demo/ingest/
   ```
4. **Talk while it runs (it'll take ~4–6 seconds for a photo):**
   > "What just happened: GCS finalized the object, Eventarc fired the event into Cloud Run, the ingest service segmented the asset (one segment for a photo), called Gemini 3.1 Flash Lite to caption it as structured JSON, called Gemini Embeddings 2 to generate a 3072-dim multimodal vector from the image bytes plus the caption, wrote the rich Firestore document, and upserted the datapoint into the Vector Search stream-update index."
5. Watch for `[ingest] done   asset_id=upload-coffee-shot-... segments=1 elapsed=3.7s`.
6. Switch to the web app, type `coffee with latte art on a wooden table` (or whatever describes the photo).
7. The new photo appears in the top results.

### Narration after
> "End to end, between 3 and 8 seconds for a photo. For a 30-second music track it's about 30 seconds. For a 30-second video — multiple segments, each captioned and embedded — it's a couple of minutes. **Critically: there is no batch job. There is no nightly reindex. The catalog is live.** A contributor uploads, and within their next sip of coffee, their asset is searchable to every user."

If time permits: also drop the `mystery-track.mp3` into ingest. Show that within ~30s, the same `sounds-like` query that found neighbors before now also surfaces the brand-new track.

---

## Closing — 40 seconds

> "Three Google Cloud capabilities you saw, in one demo:
>
> **One — Gemini Embeddings 2 in preview.** A single multimodal model, 3072 dimensions, that puts text, images, audio, and video into the same vector space. Not a triplet of single-modality models stitched together — one model that lets you search across modality boundaries with a single nearest-neighbor query.
>
> **Two — Vertex AI Vector Search 2.0 with segment-level indexing.** Not 'find the asset that contains the moment' — *find the moment.* Tens of milliseconds at this scale, scales to hundreds of millions of vectors with stream upsert.
>
> **Three — Eventarc-driven ingestion.** Drop a file in a bucket, it's queryable in seconds. The catalog is live, no cron, no Spark job, no reindex window.
>
> Combined: the search bar speaks every modality, every new asset is live in seconds, and the user feels like the catalog *understands* them. Happy to dig into anything you want."

---

## Q&A prep — anticipated questions with crisp answers

### "What does this cost at our scale (tens of millions of assets, millions of queries/day)?"

- **Indexing (one-time, then per-upload):** captioning ~$0.005–0.012 per segment, embedding ~$0.001 per segment. At 30M assets averaging 3 segments each → ~$400K one-time captioning + ~$90K embedding. Per-upload thereafter is fractions of a cent.
- **Per query:** ~$0.0003 (1× embed + 1× VS lookup + 1× Firestore batch get). 10M queries/day → ~$3K/day query cost.
- **Vector Search hosting:** ~$14/month per always-on endpoint at the demo SKU; production scales by replica count and shard count. Order of magnitude $5–20K/month for 100M-vector tier.
- **GCS + Firestore:** rounding error vs. the above.

### "What's the latency at production scale?"

- Today, on a 1K-vector index: ~300ms p50 end-to-end (dominated by the embed call at ~280ms).
- Vertex Vector Search holds ~10ms p50 lookup at 100M+ vectors per replica.
- Firestore `get_all` batch fetch stays sub-50ms for K=20.
- The bottleneck IS and WILL REMAIN the embedding call. Mitigation: client-side query caching, optional smaller-dim variant of the embedding (when available in GA).

### "When does Gemini Embeddings 2 go GA, and what's the SLA we'd commit against?"

- Currently `gemini-embedding-2-preview`. GA timeline: track the Vertex AI release notes — typically 60–90 days from the preview milestone.
- Pre-GA, no production SLA. POC and dev work fine; production launch should be planned around GA. Pricing is also subject to change at GA.

### "How does this compare to what Shutterstock or Adobe Stock are doing?"

- Most of the marketplace search stacks today are: ElasticSearch over manual tags + a separate CLIP-style image search + a separate audio classifier. Three indexes, three rankers, joined at the UI.
- This demo is one index, one ranker. The cross-modal results aren't post-hoc joined — they're literally nearest neighbors in the same space.
- The other vendors that *do* have multimodal search (e.g. TwelveLabs for video) are usually single-modality-deep. Gemini Embeddings 2 is the first widely-available embedding that's strong across all four modalities.

### "How do you handle cold start and scale?"

- Cloud Run min-instances=1 on the app service eliminates cold start at ~$10/month idle.
- Vector Search endpoint is always-on (managed). No cold start.
- Embedding API is stateless and pre-warm; first query of the day is no slower than the thousandth.
- Burst handling: Cloud Run autoscales; embedding API rate limits are the real cap (mitigation: queue + batch embed for ingest, on-demand for queries).

### "What's your eval methodology? How do you know recall is good?"

- Honest answer: **at this prototype scale we're showing qualitative recall, not measured.** The original plan called for 30 hand-labeled `(query → expected segment)` golden pairs and a Recall@K dashboard at `/api/eval`. We deferred the eval harness to focus on the live demo loop.
- For production, we recommend: (a) start with editorial-curated golden queries from your existing search analytics top 1K, (b) MTurk or internal-team relevance ratings on top-10 hits per query, (c) A/B against your current production ranker on click-through and add-to-collection rate.

### "What if the model returns garbage for a query?"

- We have a **zero-result rescue** path live in `app_v2.py`: if the top hit's cosine similarity is below 0.45, we (a) ask Gemini 3.1 Flash Lite to rewrite the query into something more "in-vocabulary" for the catalog, then (b) fall back to embedding 3 visual paraphrases and union-ranking. The result card surfaces which rescue strategy fired (`catalog_detour` or `visual_paraphrase`) so the user knows.

### "Can users filter? License, BPM, color, etc.?"

- Yes. Vector Search namespaces (`modality`, `tempo_bucket`, `length_bucket`, `kind`) are filtered at search time — no over-fetch. Color palette is a post-filter against `caption.dominant_colors` from the structured caption JSON. Adding more facets is purely a Firestore + Gemini-caption-schema additive change; no re-embedding.

### "Privacy, IP, copyright — anything we need to know about?"

- Gemini Embeddings is a *retrieval* model — it produces vectors, not generations. No content from your catalog is used to train Google models.
- Captions written into Firestore are derived from the asset itself plus its existing metadata. They're stored in your project, in your region, on your bill.
- All asset bytes stay in `gs://envato-vibe-demo` (your bucket, your IAM). The model API receives bytes for inference and returns vectors; no persistence on Google's side beyond the standard inference logging policy.

### "What would it take to put this on our actual catalog?"

- Replace the `MANIFEST_PATH` corpus harvest with a one-time backfill job pointed at your existing asset DB → run `pipeline_v2.py` over it.
- Replace the Eventarc trigger source from `gs://envato-vibe-demo/ingest/` to whichever bucket(s) your contributor uploads land in.
- Tighten the IAM service account, add VPC-SC perimeter if required.
- Add eval harness + an A/B switch in your existing search frontend pointing 1% of traffic at this endpoint.
- Realistic timeline: 6–10 engineer-weeks for a production-grade pilot on a slice of the catalog.
