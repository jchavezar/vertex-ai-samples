#!/usr/bin/env bash
# sockagent dev server — starts backend + frontend
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sockagent dev ==="
echo "Starting backend on :8080 and frontend on :5173"
echo ""

# Backend
cd "$DIR/backend"
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!

# Frontend
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
