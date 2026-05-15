#!/bin/bash
set -e

echo "🚀 Deploying Security Proxy Frontend to Cloud Run..."

# Load local .env.local variables for MSAL configuration
if [ -f .env.local ]; then
  source .env.local
fi

# Backend Cloud Run service URL.
# IMPORTANT: This MUST point at `pwc-zero-leak-proxy`, NOT `mcp-sharepoint-server`
# (which belongs to `internal_components_portal_remote`'s shared FastMCP SSE server).
BACKEND_URL="https://pwc-zero-leak-proxy-254356041555.us-central1.run.app/chat"

echo "Using Backend URL: $BACKEND_URL"

# Generate docker-env.txt to explicitly bundle it into the docker build
# without hitting .dockerignore traps for .env files.
echo "VITE_BACKEND_URL=${BACKEND_URL}" > docker-env.txt

if [ -n "$VITE_CLIENT_ID" ]; then
  echo "VITE_CLIENT_ID=${VITE_CLIENT_ID}" >> docker-env.txt
fi
if [ -n "$VITE_TENANT_ID" ]; then
  echo "VITE_TENANT_ID=${VITE_TENANT_ID}" >> docker-env.txt
fi

gcloud run deploy security-proxy-frontend \
  --source . \
  --project vtxdemos \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=5 \
  --quiet

# Clean up
rm -f docker-env.txt

echo "✅ Frontend deployed successfully."
