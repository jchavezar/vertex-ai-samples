# .gcloudignore variant for the envato-vibe-app (FastAPI UI) build.
# Keeps app/ sources; excludes ingest/pipeline/v1 code, local caches, docs, site.
.git/
.venv/
__pycache__/
*.pyc

# Heavy local data — pipeline regenerates from public sources
envato/assets/
envato/segments_cache/
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
envato/archive/

# Docs / site / narrative — not needed in the runtime image
envato/docs/
envato/site/

# Ingest-only sources — not needed for the user-facing app
envato/app/ingest.py
envato/pipeline/

# Other dockerfiles / requirements
envato/deploy/Dockerfile.ingest
envato/deploy/requirements.ingest.txt
