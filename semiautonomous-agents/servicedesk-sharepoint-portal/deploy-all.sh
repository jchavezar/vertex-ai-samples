#!/bin/bash
# Deploy all components to Google Cloud
# Usage: ./deploy-all.sh

set -e

# Configuration
PROJECT="${GOOGLE_CLOUD_PROJECT:-}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICENOW_URL="${SERVICENOW_INSTANCE_URL:-}"

if [ -z "$PROJECT" ]; then
    echo "ERROR: Set GOOGLE_CLOUD_PROJECT environment variable"
    exit 1
fi

if [ -z "$SERVICENOW_URL" ]; then
    echo "ERROR: Set SERVICENOW_INSTANCE_URL environment variable"
    exit 1
fi

echo "================================================"
echo "Deploying Light MCP Cloud Portal"
echo "================================================"
echo "Project:  $PROJECT"
echo "Location: $LOCATION"
echo "ServiceNow: $SERVICENOW_URL"
echo "================================================"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Deploy MCP Server
echo ""
echo "--- Step 1: Deploying MCP Server ---"
cd mcp-server
gcloud run deploy servicenow-mcp \
    --project "$PROJECT" \
    --source . \
    --region "$LOCATION" \
    --allow-unauthenticated \
    --set-env-vars "SERVICENOW_INSTANCE_URL=$SERVICENOW_URL"

MCP_URL=$(gcloud run services describe servicenow-mcp \
    --project "$PROJECT" \
    --region "$LOCATION" \
    --format 'value(status.url)')/mcp

echo "MCP Server URL: $MCP_URL"
cd ..

# Step 2: Deploy Agent to Agent Engine
echo ""
echo "--- Step 2: Deploying Agent to Agent Engine ---"
cd agent

# Create .env for agent
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT
GOOGLE_CLOUD_LOCATION=$LOCATION
STAGING_BUCKET=gs://${PROJECT}-staging
SERVICENOW_MCP_URL=$MCP_URL
EOF

pip install -r requirements.txt -q
python deploy.py

# Get agent ID from output
AGENT_ID=$(grep "AGENT_ENGINE_ID=" ../backend/.env 2>/dev/null | cut -d'=' -f2 || echo "")
cd ..

if [ -z "$AGENT_ID" ]; then
    echo "WARNING: Could not get AGENT_ENGINE_ID automatically."
    echo "Check agent/deploy.py output and set it manually."
    read -p "Enter AGENT_ENGINE_ID: " AGENT_ID
fi

# Step 3: Deploy TypeScript Backend
echo ""
echo "--- Step 3: Deploying TypeScript Backend ---"
cd backend
npm install
npm run build

gcloud run deploy portal-backend \
    --project "$PROJECT" \
    --source . \
    --region "$LOCATION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT,GOOGLE_CLOUD_LOCATION=$LOCATION,AGENT_ENGINE_ID=$AGENT_ID"

BACKEND_URL=$(gcloud run services describe portal-backend \
    --project "$PROJECT" \
    --region "$LOCATION" \
    --format 'value(status.url)')

echo "Backend URL: $BACKEND_URL"
cd ..

# Summary
echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "MCP Server:  $MCP_URL"
echo "Agent ID:    $AGENT_ID"
echo "Backend:     $BACKEND_URL"
echo ""
echo "Update your frontend to use:"
echo "  VITE_API_URL=$BACKEND_URL"
echo ""
echo "Test with:"
echo "  curl -X POST $BACKEND_URL/api/chat \\"
echo "    -H 'Authorization: Bearer YOUR_JWT' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"List incidents\"}'"
echo "================================================"
