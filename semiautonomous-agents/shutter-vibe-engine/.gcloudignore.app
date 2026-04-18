# .gcloudignore variant for the envato-vibe-app (FastAPI UI) build.
# Mirrors .gcloudignore but KEEPS the v2 app sources & assets that the
# ingest build excludes: app_v2.py, templates/, static/.
.git/
.venv/
__pycache__/
*.pyc

# Heavy local data — pipeline regenerates from public sources
envato/assets/
envato/index/
envato/segments_cache/
data/local_cache/
*.npz
*.npy

# Logs / scratch
*.log
nohup.out
server_pid.txt

# Local-only research notebooks/scratch
research/
findings/
# (demos/ is needed — Dockerfile.app copies demos/_client.py)

# Don't include the v1 app or the ingest-only sources in the app build.
envato/app.py
envato/pipeline.py
envato/ingest_handler.py
envato/pipeline_v2.py

# Don't ship the alternate Dockerfile or the ingest requirements.
Dockerfile
envato/Dockerfile.ingest
envato/requirements.ingest.txt
