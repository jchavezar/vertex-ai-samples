#!/usr/bin/env bash
# ==============================================================================
# START PORTAL: OUTLOOK STREAMASSIST OAUTH FLOW
# ==============================================================================
# Runs both the FastAPI backend and the React Vite dev server concurrently.
# ==============================================================================

set -o errexit
set -o pipefail

# Resolve paths
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
if lsof -i :8005 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 8005 in use. Clearing listener..."
  kill -9 $(lsof -t -i:8005) 2>/dev/null || true
fi
if lsof -i :5173 -sTCP:LISTEN -t >/dev/null; then
  echo "[SYSTEM] Port 5173 in use. Clearing listener..."
  kill -9 $(lsof -t -i:5173) 2>/dev/null || true
fi

# 2. Sync and Start FastAPI Backend
echo "[SYSTEM] Syncing backend dependencies..."
cd "$DIR/backend"
uv sync

echo "[SYSTEM] Launching FastAPI Backend on http://localhost:8005..."
uv run uvicorn main:app --port 8005 --host 0.0.0.0 &
PIDS+=($!)

# 3. Start React Frontend
echo "[SYSTEM] Syncing frontend dependencies..."
cd "$DIR/frontend"
npm install

echo "[SYSTEM] Launching Vite Frontend on http://localhost:5173..."
npm run dev -- --host 0.0.0.0 &
PIDS+=($!)

# Wait for both processes
wait
