#!/bin/bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Starting LangChain + Workspace MCP Assistant on http://localhost:8003..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
