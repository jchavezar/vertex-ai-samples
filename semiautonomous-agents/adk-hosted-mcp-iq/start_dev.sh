#!/usr/bin/env bash
# Startup script for SharePoint Hosted Explorer Custom UI test
set -e

# Setup trap to kill background processes on exit
trap 'kill $(jobs -p)' EXIT

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo "Starting SharePoint Hosted Explorer Custom UI Test"
echo "=================================================="

# 1. Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# 2. Sync python dependencies via uv
echo "Syncing backend python dependencies..."
cd adk-agent
uv sync
cd ..

# 3. Start Backend Server (FastAPI on Port 8002)
echo "Starting backend server (Port 8002)..."
cd adk-agent
uv run python main.py &
BACKEND_PID=$!
cd ..

# 4. Start Frontend Server (Vite on Port 5175)
echo "Starting frontend dev server (Port 5175)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "=================================================="
echo "Servers are running."
echo "--------------------------------------------------"
echo "Frontend: http://localhost:5175"
echo "Backend:  http://localhost:8002"
echo "=================================================="
echo "Make sure you have forwarded ports 8002 and 5175!"
echo "Press Ctrl+C to terminate both servers."
echo "=================================================="

wait
