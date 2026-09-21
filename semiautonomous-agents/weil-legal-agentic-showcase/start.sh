#!/bin/bash
# ==============================================================================
# Weil, Gotshal & Manges LLP — Autonomous Legal-Tech Innovation Showcase
# One-Click Unified Launcher (Backend Port 8000 | Frontend Port 5173)
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "====================================================================="
echo "  🏛️ WEIL, GOTSHAL & MANGES LLP — LEGAL-TECH INNOVATION SHOWCASE"
echo "  Google Cloud Vertex AI • Google ADK • Antigravity Managed Agents"
echo "====================================================================="

# Clean up any lingering processes on ports 8000 and 5173
echo "🔍 Checking port availability (8000, 5173)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Check if dependencies are already available in current python
if python3 -c "import fastapi, uvicorn, numpy" 2>/dev/null; then
    echo "✅ Python environment verified."
elif [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# Ensure frontend dependencies exist
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo "🚀 Starting FastAPI Backend on http://localhost:8000..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "🚀 Starting Vite Frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Trap signals for graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down Weil Legal-Tech Showcase..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    echo "✅ Shutdown complete. Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo ""
echo "====================================================================="
echo "  ✨ WEIL LEGAL-TECH SHOWCASE IS LIVE & READY FOR THE BRIEFING!"
echo "  👉 Cockpit Portal:  http://localhost:5173"
echo "  👉 Backend API:     http://localhost:8000"
echo "  👉 Swagger Docs:    http://localhost:8000/docs"
echo "====================================================================="
echo "  Press Ctrl+C to terminate all services."
echo ""

wait
