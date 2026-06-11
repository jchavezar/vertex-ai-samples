#!/bin/bash
# Start both backend and frontend servers for Gemini Enterprise MCP Co-work Portal

# Get current script folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=================================================="
echo " Starting Gemini Enterprise Co-work Portal"
echo "=================================================="

# Function to clean up background processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start Backend FastAPI
echo "[*] Starting Backend (FastAPI) on port 8002..."
cd "$DIR/backend"
PYTHONUNBUFFERED=1 uv run uvicorn main:app --port 8002 &
BACKEND_PID=$!

# Wait a moment
sleep 2

# 2. Start Frontend Vite
echo "[*] Starting Frontend (React/Vite) on port 5174..."
cd "$DIR/frontend"
npm run dev -- --port 5174 &
FRONTEND_PID=$!

# Wait for background jobs
wait $BACKEND_PID $FRONTEND_PID
