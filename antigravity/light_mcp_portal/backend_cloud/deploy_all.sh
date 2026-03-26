#!/bin/bash
set -e

# Change to the script's directory (backend_cloud)
cd "$(dirname "$0")"

echo "====================================="
echo " Deploying ServiceNow MCP to Cloud Run"
echo "====================================="

# Read environment variables from the parent .env file
source ../.env

if [ -z "$SERVICENOW_INSTANCE_URL" ]; then
    echo "❌ Error: SERVICENOW_INSTANCE_URL is not set in ../.env"
    exit 1
fi

echo "🚀 Deploying to Cloud Run: servicenow-mcp-prod"
gcloud run deploy servicenow-mcp-prod \
    --project $GOOGLE_CLOUD_PROJECT \
    --source ./servicenow_mcp \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars SERVICENOW_INSTANCE_URL=$SERVICENOW_INSTANCE_URL \
    --set-env-vars SERVICENOW_BASIC_AUTH_USER=$SERVICENOW_BASIC_AUTH_USER \
    --set-env-vars SERVICENOW_BASIC_AUTH_PASS=$SERVICENOW_BASIC_AUTH_PASS \
    --format="value(status.url)" > mcp_url.txt

MCP_URL=$(cat mcp_url.txt)/sse
echo "✅ Cloud Run deployed at: $MCP_URL"

echo ""
echo "====================================="
echo " Deploying Adk Agent to Agent Engine "
echo "====================================="

export SERVICENOW_MCP_URL=$MCP_URL
cd agents
# Install requirements if testing locally
uv pip install -r requirements.txt || true
# Run deployment script
uv run python deploy_agent_engine.py

echo "Deployment Sequence Finished."
