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
VENV_PYTHON="$DIR/.venv/bin/python"

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
if lsof -i :8086 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 8086 in use. Clearing listener..."
  kill -9 $(lsof -t -i:8086) 2>/dev/null || true
fi
if lsof -i :5190 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 5190 in use. Clearing listener..."
  kill -9 $(lsof -t -i:5190) 2>/dev/null || true
fi

# 2. Start FastAPI Backend
echo "[SYSTEM] Launching FastAPI Backend on http://localhost:8086..."
cd "$DIR"
$VENV_PYTHON -m uvicorn backend.main:app --port 8086 --host 0.0.0.0 &
PIDS+=($!)

# 3. Start React Frontend
echo "[SYSTEM] Launching Vite Frontend on http://localhost:5190..."
cd "$DIR/frontend"
npm run dev -- --host 0.0.0.0 &
PIDS+=($!)

# Wait for both processes
wait
