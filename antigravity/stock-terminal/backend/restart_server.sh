#!/bin/bash
echo "=== EMERGENCY RESTART SCRIPT ==="
echo "Force killing all python and uvicorn processes..."

# Find PIDs for uvicorn and main.py related to this project
# Be careful not to kill system python, but in this env it's likely fine to target uvicorn
pids=$(ps aux | grep -E "uvicorn|main.py" | grep -v grep | awk '{print $2}')

if [ -n "$pids" ]; then
  echo "Found processes: $pids"
  echo "Killing them with -9 (SIGKILL)..."
  echo "$pids" | xargs kill -9
else
  echo "No existing server processes found."
fi

# Kill any stuck curl requests
echo "Killing stuck curl processes..."
pkill -9 curl || true

echo "Waiting 2 seconds for ports to clear..."
sleep 2

echo "Checking port 8001..."
lsof -i :8001

echo "Starting Backend Server Fresh..."
cd "$(dirname "$0")" || exit

# Check if venv exists
if [ -f ".venv/bin/python" ]; then
    ./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
else
    echo "ERROR: .venv not found. Trying global python..."
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
fi
