#!/bin/bash
set -e

# start.sh - Launch Minimalist Chatbot Local Environment

# Color codes
GREEN='\033[0;32%'
BLUE='\033[0;34%'
YELLOW='\033[1;33%'
RED='\033[0;31%'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}  Aura — Minimalist Chatbot Development Launcher    ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Navigate to script directory
cd "$(dirname "$0")"

# Step 1: Install dependencies
echo -e "\n${YELLOW}[1/3] Validating and installing npm dependencies...${NC}"
npm install

# Step 2: Verify gcloud authentication
echo -e "\n${YELLOW}[2/3] Verifying Google Cloud SDK Authentication...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: 'gcloud' CLI is not installed.${NC}"
    echo -e "Please install Google Cloud SDK and authenticate to proceed."
    exit 1
fi

echo -e "Attempting to retrieve GCP Access Token..."
GCP_TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null || gcloud auth print-access-token 2>/dev/null || true)

if [ -z "$GCP_TOKEN" ]; then
    echo -e "${YELLOW}Warning: No active GCP credentials detected.${NC}"
    echo -e "Please run 'gcloud auth application-default login' to authorize the chatbot to make calls on your behalf."
    echo -e "Press Enter to proceed anyway, or Ctrl+C to abort and authenticate first."
    read -r
else
    echo -e "${GREEN}Authentication verified! Token successfully acquired.${NC}"
fi

# Step 3: Run development servers
echo -e "\n${YELLOW}[3/3] Starting Frontend (Vite) and Backend (Express)...${NC}"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}Backend:  http://localhost:8001${NC}"
echo -e "${BLUE}====================================================${NC}"

npm run dev
