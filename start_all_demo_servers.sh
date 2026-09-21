#!/bin/bash
# ==============================================================================
# Master Unified Demo Server Launcher for Weil Executive Workshop
# Ports Managed:
#   - 8089: Weil 5-Act Modernization Portal (serve_weil.py)
#   - 5173: Weil Deal Cockpit & 3D Galactic Universe (Vite Frontend)
#   - 8000: Weil Legal-Tech Agent Platform (FastAPI Backend)
# ==============================================================================

set -e

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOG_DIR="$REPO_ROOT/.demo_logs"
mkdir -p "$LOG_DIR"

WEIL_MOD_DIR="$REPO_ROOT/semiautonomous-agents/weil-modernization"
WEIL_SHOWCASE_DIR="$REPO_ROOT/semiautonomous-agents/weil-legal-agentic-showcase"

stop_all() {
    echo "🛑 Stopping all demo servers and parent watcher trees..."
    pkill -9 -f "weil-legal-agentic-showcase" 2>/dev/null || true
    pkill -9 -f "serve_weil.py" 2>/dev/null || true
    pkill -9 -f "uvicorn backend.main:app" 2>/dev/null || true
    lsof -ti:8089 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "✅ All demo server ports and watcher processes released."
}

status_all() {
    echo "================================================================="
    echo "📊 WEIL WORKSHOP DEMO SERVERS STATUS"
    echo "================================================================="
    
    # 8089 Check
    if lsof -i:8089 >/dev/null 2>&1; then
        echo "  🟢 Port 8089 [UP]  : Weil 5-Act Modernization -> http://localhost:8089/"
    else
        echo "  🔴 Port 8089 [DOWN]: Weil 5-Act Modernization"
    fi

    # 5173 Check
    if lsof -i:5173 >/dev/null 2>&1; then
        echo "  🟢 Port 5173 [UP]  : Weil Deal Cockpit        -> http://localhost:5173/"
        echo "  🟢 Port 5173 [UP]  : 3D Galactic Constellation -> http://localhost:5173/constellation.html"
    else
        echo "  🔴 Port 5173 [DOWN]: Weil Deal Cockpit & 3D Constellation"
    fi

    # 8000 Check
    if lsof -i:8000 >/dev/null 2>&1; then
        echo "  🟢 Port 8000 [UP]  : Legal-Tech API Backend   -> http://localhost:8000/docs"
    else
        echo "  🔴 Port 8000 [DOWN]: Legal-Tech API Backend"
    fi
    echo "================================================================="
}

if [ "$1" == "--stop" ] || [ "$1" == "stop" ]; then
    stop_all
    exit 0
fi

if [ "$1" == "--status" ] || [ "$1" == "status" ]; then
    status_all
    exit 0
fi

echo "================================================================="
echo "🚀 INITIALIZING ALL WEIL DEMO SERVERS (POST-REBOOT LAUNCHER)"
echo "================================================================="

# 1. Clean lingering ports
echo "🧹 Releasing ports 8089, 5173, 8000..."
stop_all >/dev/null 2>&1 || true
sleep 1

# 2. Boot Weil 5-Act Modernization Server (Port 8089)
if [ -d "$WEIL_MOD_DIR" ]; then
    echo "⚡ Launching Weil 5-Act Modernization Server (Port 8089)..."
    cd "$WEIL_MOD_DIR"
    nohup python3 serve_weil.py > "$LOG_DIR/weil_modernization_8089.log" 2>&1 &
    cd "$REPO_ROOT"
fi

# 3. Boot Weil Legal-Tech Backend (Port 8000)
if [ -d "$WEIL_SHOWCASE_DIR/backend" ]; then
    echo "⚡ Launching FastAPI Legal-Tech Backend (Port 8000)..."
    cd "$WEIL_SHOWCASE_DIR"
    if [ -f "backend/.venv/bin/activate" ]; then
        source backend/.venv/bin/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend_8000.log" 2>&1 &
    deactivate 2>/dev/null || true
    cd "$REPO_ROOT"
fi

# 4. Boot Weil Showcase & 3D Constellation Frontend (Port 5173)
if [ -d "$WEIL_SHOWCASE_DIR/frontend" ]; then
    echo "⚡ Launching Vite Frontend & 3D Constellation (Port 5173)..."
    cd "$WEIL_SHOWCASE_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        echo "   (Installing frontend npm dependencies...)"
        npm install --silent
    fi
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$LOG_DIR/frontend_5173.log" 2>&1 &
    cd "$REPO_ROOT"
fi

# 5. Wait and probe health
echo "⏳ Verifying services health..."
sleep 2.5

status_all

echo ""
echo "🎯 PRESENTATION SHORTCUTS FOR TOMORROW:"
echo "  • Act 1-5 Modernization Suite : http://localhost:8089/"
echo "  • 3D Galactic Universe        : http://localhost:5173/constellation.html"
echo "  • Executive Legal-Tech Cockpit: http://localhost:5173/"
echo "  • FastAPI Swagger API         : http://localhost:8000/docs"
echo ""
echo "💡 Commands:"
echo "  • Stop all servers : ./start_all_demo_servers.sh --stop"
echo "  • Check status     : ./start_all_demo_servers.sh --status"
echo "================================================================="
