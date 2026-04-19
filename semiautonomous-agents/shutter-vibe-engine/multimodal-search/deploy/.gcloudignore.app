# .gcloudignore variant for the vibe-search-app (FastAPI UI) build.
# Keeps app/ sources; excludes ingest/pipeline/v1 code, local caches, docs, site.
.git/
.venv/
__pycache__/
*.pyc

# Heavy local data — pipeline regenerates from public sources
multimodal-search/assets/
multimodal-search/segments_cache/
data/local_cache/
*.npz
*.npy

# Logs / scratch
*.log
nohup.out
server_pid.txt

# Local-only research / unrelated code
research/
findings/
antigravity/
# (demos/_client.py is needed — Dockerfile.app COPYs it explicitly)

# v1 / archived sources
multimodal-search/archive/

# Docs / site / narrative — not needed in the runtime image
multimodal-search/docs/
multimodal-search/site/

# Ingest-only sources — not needed for the user-facing app
multimodal-search/app/ingest.py
multimodal-search/pipeline/

# Other dockerfiles / requirements
multimodal-search/deploy/Dockerfile.ingest
multimodal-search/deploy/requirements.ingest.txt
