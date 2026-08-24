#!/usr/bin/env bash
# ==============================================================================
# Antigravity // Legacy to AI-Native Modernization Hub
# High-Impact Executive Briefing Center (EBC) Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

BACKEND_PORT=${PORT:-8008}
FRONTEND_PORT=${FRONTEND_PORT:-5178}

echo "======================================================================"
echo "⚡ ANTIGRAVITY // LEGACY TO AI-NATIVE MODERNIZATION HUB"
echo "======================================================================"
echo "Initializing Executive Briefing Center (EBC) Showcase Environment..."

# 1. Proactive Port Conflict Management
check_and_free_port() {
  local port=$1
  local name=$2
  local pids=$(lsof -ti :${port} 2>/dev/null || true)
  if [ -n "${pids}" ]; then
    echo "⚠️  Port ${port} (${name}) is in use by PID(s): ${pids}. Terminating stale listener..."
    kill -9 ${pids} 2>/dev/null || true
    sleep 1
  fi
}

check_and_free_port ${BACKEND_PORT} "FastAPI Backend"
check_and_free_port ${FRONTEND_PORT} "Vite React Frontend"

# 2. Start Backend using uv
echo "🚀 Starting FastAPI Backend on port ${BACKEND_PORT}..."
cd "${BACKEND_DIR}"
PORT=${BACKEND_PORT} uv run uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload &
BACKEND_PID=$!

# Wait for backend health check
echo "⏳ Waiting for backend readiness..."
for i in {1..20}; do
  if curl -s "http://localhost:${BACKEND_PORT}/api/health" >/dev/null 2>&1; then
    echo "✅ Backend online at http://localhost:${BACKEND_PORT}/api/health"
    break
  fi
  sleep 0.5
done

# 3. Start Frontend using npm / vite
echo "🎨 Starting React 19 Frontend on port ${FRONTEND_PORT}..."
cd "${FRONTEND_DIR}"
VITE_API_URL="http://localhost:${BACKEND_PORT}" npm run dev -- --port ${FRONTEND_PORT} --host &
FRONTEND_PID=$!

cleanup() {
  echo ""
  echo "🛑 Terminating Antigravity Modernization Hub servers..."
  kill ${BACKEND_PID} 2>/dev/null || true
  kill ${FRONTEND_PID} 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo ""
echo "======================================================================"
echo "🌟 ANTIGRAVITY MODERNIZATION HUB IS LIVE"
echo "======================================================================"
echo "🖥️  Frontend UI:   http://localhost:${FRONTEND_PORT}"
echo "📡 Backend API:   http://localhost:${BACKEND_PORT}/docs"
echo "======================================================================"
echo "Press Ctrl+C to terminate all services."
echo ""

wait
