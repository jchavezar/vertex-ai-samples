#!/usr/bin/env bash
set -e

# Kill any existing processes on ports 8090 and 5174
lsof -ti :8090 | xargs kill -9 2>/dev/null || true
lsof -ti :5174 | xargs kill -9 2>/dev/null || true

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting ADK Enterprise Assistant..."

# Start Backend
echo "Starting Backend (FastAPI + ADK InMemoryRunner on port 8090)..."
cd "$PROJECT_DIR/backend"
uv run uvicorn main:app --host 0.0.0.0 --port 8090 &
BACKEND_PID=$!

# Wait for backend health
echo "Waiting for backend health endpoint..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:8090/health > /dev/null; then
    echo "✅ Backend is healthy on http://127.0.0.1:8090"
    break
  fi
  sleep 1
done

# Start Frontend
echo "Starting Frontend (Vite + React 19 on port 5174)..."
cd "$PROJECT_DIR/frontend"
npm run dev -- --port 5174 --host &
FRONTEND_PID=$!

echo "✨ Services started successfully!"
echo "Backend:  http://127.0.0.1:8090"
echo "Frontend: http://127.0.0.1:5174"

# Trap exit signals
trap "kill -9 $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM EXIT
wait
