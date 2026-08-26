#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "  EBC EXECUTIVE AI TRANSFORMATION SHOWCASE - LAUNCHER"
echo "  Target Display: 100-inch Executive Boardroom Display"
echo "  Model: Gemini 3.7 / 2.5 on Vertex AI"
echo "=================================================================="

# Check and free ports 8000 and 5178 if occupied
for PORT in 8000 5178; do
  PID=$(lsof -ti :$PORT 2>/dev/null || true)
  if [ -n "$PID" ]; then
    echo "⚠️  Port $PORT is currently occupied by PID(s): $PID. Releasing port..."
    kill -9 $PID 2>/dev/null || true
    sleep 1
  fi
done

echo "🚀 Starting FastAPI Backend on port 8000..."
cd "$DIR/backend"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "🚀 Starting Vite Frontend on port 5178..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================================================="
echo "  ✅ Services successfully launched!"
echo "  - Backend API:   http://localhost:8000 (Docs: http://localhost:8000/docs)"
echo "  - Frontend UI:   http://localhost:5178"
echo "=================================================================="

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
