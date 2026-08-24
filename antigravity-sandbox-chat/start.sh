#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo " Starting Antigravity Managed Agent Sandbox Chat"
echo " Backend: http://127.0.0.1:8090"
echo " Frontend: http://localhost:5174"
echo " Target Project: vtxdemos | Model: antigravity-preview-05-2026"
echo "=========================================================="

# Check and kill any stale processes on 8090 or 5174 if present
if lsof -t -i:8090 > /dev/null 2>&1; then
  echo "[INFO] Freeing port 8090..."
  kill -9 $(lsof -t -i:8090) || true
fi

if lsof -t -i:5174 > /dev/null 2>&1; then
  echo "[INFO] Freeing port 5174..."
  kill -9 $(lsof -t -i:5174) || true
fi

# Start FastAPI Backend with uv
echo "[INFO] Starting Backend..."
(cd "$DIR/backend" && uv run python main.py) &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start Vite Frontend
echo "[INFO] Starting Frontend..."
(cd "$DIR/frontend" && npm run dev -- --port 5174 --host) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT INT TERM

wait
