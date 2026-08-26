#!/usr/bin/env bash
# ==============================================================================
# Google ADK Light Chatbot - Startup Script
# TypeScript Frontend + Google ADK 2.1.0 Python Backend
# ==============================================================================

set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

MODE="${1:-prod}"

echo "=========================================================="
echo "✨ Google ADK Chatbot (TypeScript + Light Theme UI)"
echo "   Modo: $MODE"
echo "=========================================================="

# Check Python environment
if ! python3 -c "import fastapi, uvicorn, google.adk" &> /dev/null; then
    echo "📦 Instalando dependencias de Python..."
    pip install -r backend/requirements.txt
fi

if [ "$MODE" = "dev" ]; then
    echo "🚀 Iniciando entorno de DESARROLLO..."
    echo "  - Backend (FastAPI + ADK): http://localhost:8005"
    echo "  - Frontend (Vite + TS):     http://localhost:5180"
    
    # Run FastAPI in background
    cd "$PROJECT_DIR/backend"
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload &
    BACKEND_PID=$!
    
    # Run Vite in frontend
    cd "$PROJECT_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!

    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
else
    echo "🏗️  Verificando compilación de Frontend TypeScript..."
    if [ ! -d "$PROJECT_DIR/frontend/dist" ]; then
        cd "$PROJECT_DIR/frontend"
        npm install
        npm run build
    fi

    echo "🚀 Iniciando Servidor de Producción en http://localhost:8005..."
    cd "$PROJECT_DIR/backend"
    exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8005
fi
