# Multimodal Vibe Search on Vertex AI

> Type a vibe → get the photo, the video clip, the music track, the SFX, and the graphic that share that mood. One query, five modalities, ranked in a shared 3072-dim embedding space.

**📖 Read the full story (with hero video, embedding-space visualization, and architecture deep-dive):**
**→ [`site/`](./site/) — published at [jchavezar.github.io/vertex-ai-samples/multimodal-search/](https://jchavezar.github.io/vertex-ai-samples/multimodal-search/)**

![hero](./docs/hero.gif)

---

## Repository layout

```
multimodal-search/
├── app/              FastAPI service (UI + ingest endpoints)
├── pipeline/         Offline indexing & backfill scripts
├── deploy/           Cloud Run / Cloud Build / Eventarc deploy
├── docs/             Screenshots, hero clip, embedding-space figure, ops docs
├── site/             Astro Starlight narrative site (GitHub Pages)
├── assets/           Sample seed assets
└── archive/          Previous iteration & v1 code, kept for reference
```

## Quickstart

```bash
# 1. Install + auth (one-time)
gcloud auth application-default login
pip install -r app/requirements.txt

# 2. Build the index (sample assets in assets/)
python pipeline/build.py

# 3. Run the app locally
cd app && uvicorn main:app --reload --port 8080
open http://localhost:8080
```

## Deploy

```bash
bash deploy/deploy_app.sh      # FastAPI on Cloud Run
bash deploy/deploy_ingest.sh   # Eventarc-triggered ingest service
```

## Documentation

- **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** — full deploy/runbook
- **[docs/DEMO_SCRIPT.md](./docs/DEMO_SCRIPT.md)** — live-demo flow
- **[docs/DEMO_QUESTIONS.md](./docs/DEMO_QUESTIONS.md)** — Q&A primer
- **[archive/](./archive/)** — previous README/STORY drafts kept for reference

---

Built by [Jesus Chavez](https://www.linkedin.com/in/jchavezar/) · Customer Engineer, Google Cloud
