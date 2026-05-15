#!/usr/bin/env bash
# Deploy the MCP server to Cloud Run.
# In demo / pre-gateway mode this is --allow-unauthenticated for easy curl-testing.
# Once the Agent Gateway is live, switch to --no-allow-unauthenticated and rely
# on the gateway's mTLS for ingress auth.
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?set in .env}"
: "${DEPLOY_LOCATION:?set in .env}"
SERVICE_NAME="${MCP_SERVICE_NAME:-agent-gateway-demo-mcp}"
DEMO_REAL_MCP="${DEMO_REAL_MCP:-0}"

echo "[deploy] project=${GOOGLE_CLOUD_PROJECT} region=${DEPLOY_LOCATION} mode=$([ "$DEMO_REAL_MCP" = 1 ] && echo real || echo stub)"

gcloud run deploy "${SERVICE_NAME}" --source . --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --allow-unauthenticated --set-env-vars "DEMO_REAL_MCP=${DEMO_REAL_MCP}"

URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --format='value(status.url)')
echo
echo "[deploy] DONE — MCP_SERVER_URL=${URL}"
echo "[deploy] add to .env: MCP_SERVER_URL=${URL}"
