#!/usr/bin/env bash
# Local dev server for Vector Search Canvas. Mirrors the multimodal-search
# dev.sh — high port to dodge collisions, absolute path to uvicorn so nohup
# doesn't strip PATH and break us.
set -euo pipefail

PORT="${PORT:-8770}"
HOST="${HOST:-127.0.0.1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

VENV_UVICORN="$(cd "${SCRIPT_DIR}/../shutter-vibe-engine" && pwd)/.venv/bin/uvicorn"
if [[ -x "${VENV_UVICORN}" ]]; then
  UVICORN="${VENV_UVICORN}"
elif command -v uvicorn >/dev/null 2>&1; then
  UVICORN="$(command -v uvicorn)"
else
  echo "ERROR: uvicorn not found. Expected at ${VENV_UVICORN} or on PATH." >&2
  exit 1
fi

if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi

export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-vtxdemos}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"

echo "→ Vector Search Canvas dev server"
echo "  http://${HOST}:${PORT}"
echo "  project=${GOOGLE_CLOUD_PROJECT}  region=${GOOGLE_CLOUD_LOCATION}"
echo "  Ctrl+C to stop. Edit Python → auto-reload. Edit JS/CSS → hard-refresh."
echo ""

exec "${UVICORN}" app.main:app --reload --host "${HOST}" --port "${PORT}"
