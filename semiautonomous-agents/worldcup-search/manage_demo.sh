#!/usr/bin/env bash

# Premium colors and formatting
GREEN='\033[0;32m'
GOLD='\033[0;33m'
EMERALD='\033[38;5;48m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRAFTS_DIR="${ROOT_DIR}/drafts"

show_usage() {
    echo -e "${BOLD}🏆 FIFA WorldCup Scout - Demo Manager${NC}"
    echo -e "Usage: ./manage_demo.sh [start|stop|clean|deploy] [draft_name]"
    echo -e ""
    echo -e "Commands:"
    echo -e "  ${GREEN}start${NC} [name]  Create a clean draft, copy premium assets, setup dependencies, and launch server (defaults to 'live-demo')"
    echo -e "  ${GOLD}stop${NC}          Kill any active server currently listening on port 8000"
    echo -e "  ${RED}clean${NC} [name]  Stop the server and permanently remove the draft directory (defaults to 'live-demo')"
    echo -e "  ${EMERALD}deploy${NC}        Enhance the workspace and deploy the agent to Google's Agent Runtime with built-in Cloud Trace"
    echo -e ""
}

stop_server() {
    echo -e "${GOLD}Checking for active processes on port 8000...${NC}"
    PID=$(lsof -t -i :8000 2>/dev/null)
    if [ -n "$PID" ]; then
        echo -e "${RED}Found process ${PID} listening on port 8000. Killing it...${NC}"
        kill -9 $PID
        echo -e "${GREEN}Port 8000 freed successfully.${NC}"
    else
        echo -e "No active processes found on port 8000."
    fi
}

start_demo() {
    DRAFT_NAME=${1:-"live-demo"}
    TARGET_DIR="${DRAFTS_DIR}/${DRAFT_NAME}"

    stop_server

    echo -e "${EMERALD}Recreating clean draft folder for: ${DRAFT_NAME}...${NC}"
    mkdir -p "${TARGET_DIR}/app/static"

    # Copy files from master app folder to target draft
    echo -e "Copying assets and codebase templates..."
    cp -R "${ROOT_DIR}/app/" "${TARGET_DIR}/app"
    cp "${ROOT_DIR}/pyproject.toml" "${TARGET_DIR}/pyproject.toml" 2>/dev/null || true
    cp "${ROOT_DIR}/uv.lock" "${TARGET_DIR}/uv.lock" 2>/dev/null || true

    # Sync dependencies
    echo -e "Syncing Python virtual environment in ${TARGET_DIR}..."
    cd "${TARGET_DIR}" || exit
    
    # Check if uv is installed, use uv for ultra-fast sync
    if command -v uv &> /dev/null; then
        uv sync --no-dev
    else
        echo -e "${GOLD}uv not found. Initializing standard virtualenv...${NC}"
        python3 -m venv .venv
        source .venv/bin/python -m pip install -r requirements.txt 2>/dev/null || .venv/bin/pip install fastapi uvicorn google-adk google-cloud-logging google-genai
    fi

    echo -e "${EMERALD}Launching FastAPI Grounded Server in the background...${NC}"
    GOOGLE_CLOUD_PROJECT=vtxdemos GOOGLE_CLOUD_LOCATION=global PYTHONPATH=. .venv/bin/python app/fast_api_app.py > server.log 2>&1 &
    
    # Give it a couple seconds to boot
    sleep 2
    
    echo -e "\n${BOLD}${GREEN}🚀 WorldCup Scout Demo is LIVE!${NC}"
    echo -e "--------------------------------------------------------"
    echo -e "👉 Custom UI:      ${BOLD}${EMERALD}http://localhost:8000/${NC}"
    echo -e "👉 WorldCup Path:   ${BOLD}${EMERALD}http://localhost:8000/worldcup${NC}"
    echo -e "👉 Live Logs:       tail -f ${TARGET_DIR}/server.log"
    echo -e "--------------------------------------------------------"
}

clean_demo() {
    DRAFT_NAME=${1:-"live-demo"}
    TARGET_DIR="${DRAFTS_DIR}/${DRAFT_NAME}"

    stop_server

    if [ -d "$TARGET_DIR" ]; then
        echo -e "${RED}Deleting draft directory: ${TARGET_DIR}...${NC}"
        rm -rf "$TARGET_DIR"
        echo -e "${GREEN}Cleanup complete! No traces left behind.${NC}"
    else
        echo -e "Draft directory ${TARGET_DIR} does not exist."
    fi
}

deploy_agent_runtime() {
    echo -e "${EMERALD}Enhancing project configuration for Google's Agent Runtime...${NC}"
    # Run enhance command to ensure manifest has agent_runtime target
    agents-cli scaffold enhance . --deployment-target agent_runtime --no-confirm-project 2>/dev/null || true
    
    echo -e "${EMERALD}Triggering Agent Runtime deployment (with built-in Cloud Trace)...${NC}"
    echo -e "${GOLD}Note: Agent Runtime deploys run server-side and take ~5-10 minutes.${NC}"
    
    # Run standard agents-cli deploy in no-wait mode so the CLI returns instantly
    agents-cli deploy --project vtxdemos --region us-east1 --no-wait --no-confirm-project
    
    echo -e "\n${BOLD}${GREEN}🚀 Agent Runtime Deployment Initiated successfully!${NC}"
    echo -e "------------------------------------------------------------------------"
    echo -e "👉 Check Status:        ${BOLD}agents-cli deploy --status${NC}"
    echo -e "👉 View Cloud Traces:    ${BOLD}${EMERALD}https://console.cloud.google.com/trace/explorer?project=vtxdemos${NC}"
    echo -e "------------------------------------------------------------------------"
}

# Main routing
case "$1" in
    start)
        start_demo "$2"
        ;;
    stop)
        stop_server
        ;;
    clean)
        clean_demo "$2"
        ;;
    deploy)
        deploy_agent_runtime
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
