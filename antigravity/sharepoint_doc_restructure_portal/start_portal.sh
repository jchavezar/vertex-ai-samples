#!/usr/bin/env bash
# ==============================================================================
# START PORTAL: SHAREPOINT DOCUMENT RESTRUCTURE PORTAL
# ==============================================================================
# Runs both the FastAPI backend and the React Vite dev server concurrently.
# ==============================================================================

set -o errexit
set -o pipefail

# Resolve paths
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="/usr/local/google/home/jesusarguelles/vertex-ai-samples/antigravity/light_mcp_portal/.venv/bin/python"

# PIDs list to kill on exit
PIDS=()

cleanup() {
  echo -e "\n[SYSTEM] Terminating dev servers..."
  for pid in "${PIDS[@]}"; do
    kill -9 "$pid" 2>/dev/null || true
  done
  echo "[SYSTEM] Off."
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Port Conflict management
echo "[SYSTEM] Checking ports..."
if lsof -i :8095 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 8095 in use. Clearing listener..."
  kill -9 $(lsof -t -i:8095) 2>/dev/null || true
fi
if lsof -i :5185 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 5185 in use. Clearing listener..."
  kill -9 $(lsof -t -i:5185) 2>/dev/null || true
fi

# 2. Start FastAPI Backend
echo "[SYSTEM] Launching FastAPI Backend on http://localhost:8095..."
cd "$DIR"
$VENV_PYTHON -m uvicorn backend.main:app --port 8095 --host 0.0.0.0 &
PIDS+=($!)

# 3. Start React Frontend
echo "[SYSTEM] Launching Vite Frontend on http://localhost:5185..."
cd "$DIR/frontend"
npm run dev -- --host 0.0.0.0 &
PIDS+=($!)

# Wait for both processes
wait
