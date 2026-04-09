#!/bin/bash
# A2A Protocol Dojo — Start All Services
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

cleanup() {
    echo ""
    echo "Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    echo "All services stopped."
}

trap cleanup EXIT INT TERM

echo "================================================"
echo "  A2A Protocol Dojo — Starting Services"
echo "================================================"
echo ""

# Install deps if needed
echo "[1/4] Installing agent dependencies..."
cd "$DIR/agents" && uv sync --quiet 2>/dev/null

echo "[2/4] Installing backend dependencies..."
cd "$DIR/backend" && uv sync --quiet 2>/dev/null

echo "[3/4] Installing frontend dependencies..."
cd "$DIR/frontend" && npm install --silent 2>/dev/null

echo ""
echo "Starting services..."
echo ""

# Start Echo Agent (port 8001)
cd "$DIR/agents"
uv run python echo_agent.py &
PIDS+=($!)
echo "  Echo Agent     → http://localhost:8001"

# Start Gemini Agent (port 8002)
uv run python gemini_agent.py &
PIDS+=($!)
echo "  Gemini Agent   → http://localhost:8002"

# Start Backend Gateway (port 8000)
cd "$DIR/backend"
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning &
PIDS+=($!)
echo "  Backend        → http://localhost:8000"

# Start Frontend (port 5173)
cd "$DIR/frontend"
npx vite --host 0.0.0.0 &
PIDS+=($!)
echo "  Frontend       → http://localhost:5173"

echo ""
echo "================================================"
echo "  All services running! Open http://localhost:5173"
echo "  Press Ctrl+C to stop all services."
echo "================================================"

wait
