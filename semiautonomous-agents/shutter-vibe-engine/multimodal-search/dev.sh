#!/usr/bin/env bash
# Local dev server for Vibe Search v2.
# Uses a high port (8765) to dodge whatever else is bound on common ports.
#
# Usage:
#   bash dev.sh           # start on :8765 with --reload
#   PORT=9000 bash dev.sh # override port
set -euo pipefail

PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Locate uvicorn — prefer the shutter-vibe-engine venv, fall back to PATH.
VENV_UVICORN="$(cd "${SCRIPT_DIR}/.." && pwd)/.venv/bin/uvicorn"
if [[ -x "${VENV_UVICORN}" ]]; then
  UVICORN="${VENV_UVICORN}"
elif command -v uvicorn >/dev/null 2>&1; then
  UVICORN="$(command -v uvicorn)"
else
  echo "ERROR: uvicorn not found. Expected at ${VENV_UVICORN} or on PATH." >&2
  exit 1
fi

# Free the port if something already holds it (a stale uvicorn from earlier).
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi

# Required env for Vertex AI / Firestore / GCS.
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-vtxdemos}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
export ENVATO_GCS_BUCKET="${ENVATO_GCS_BUCKET:-envato-vibe-demo}"

echo "→ Vibe Search dev server"
echo "  http://${HOST}:${PORT}"
echo "  project=${GOOGLE_CLOUD_PROJECT}  region=${GOOGLE_CLOUD_LOCATION}"
echo "  Ctrl+C to stop. Edit Python → auto-reload. Edit JS/CSS → hard-refresh browser."
echo ""

exec "${UVICORN}" app.main:app --reload --host "${HOST}" --port "${PORT}"
