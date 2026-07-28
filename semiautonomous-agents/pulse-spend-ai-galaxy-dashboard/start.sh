#!/bin/bash
set -e

echo "========================================================="
echo "🌌 PulseSpend AI: Expense Analytics & Spend Galaxy Stack"
echo "========================================================="

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "📍 Project Root: $PROJECT_DIR"

# 1. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "🐍 Installing Backend Python Dependencies..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q

# 2. Frontend NPM Setup
echo "⚡ Installing Frontend Node Dependencies..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi

# 3. Environment check
cd "$PROJECT_DIR"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📄 Copying .env.example to .env..."
    cp .env.example .env
fi

export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-vtxdemos}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
export GOOGLE_GENAI_USE_VERTEXAI="True"
export ENRICHED_DATA_PATH="$PROJECT_DIR/data/enriched_dataset.json"

echo "🚀 Starting FastAPI Backend Daemon on port 8001..."
PYTHONUNBUFFERED=1 python3 "$PROJECT_DIR/backend/main.py" &
BACKEND_PID=$!

echo "✨ Starting Vite Frontend Dev Server on port 5173..."
cd "$PROJECT_DIR/frontend"
npm run dev -- --port 5173 --host &
FRONTEND_PID=$!

trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" INT TERM EXIT

echo ""
echo "========================================================="
echo "🎉 PulseSpend AI is Live!"
echo "   📊 Dashboard UI:  http://localhost:5173"
echo "   🔌 Backend API:   http://127.0.0.1:8001/api/health"
echo "========================================================="
echo "Press Ctrl+C to terminate both servers."

wait
