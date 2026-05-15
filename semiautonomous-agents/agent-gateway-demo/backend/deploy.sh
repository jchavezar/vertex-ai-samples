#!/usr/bin/env bash
# Deploy the FastAPI backend to Cloud Run.
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?set in .env}"
: "${DEPLOY_LOCATION:?set in .env}"
: "${AGENT_ENGINE_RESOURCE:?set in .env after agent deploy}"
SERVICE_NAME="${BACKEND_SERVICE_NAME:-agent-gateway-demo-backend}"
SESSION_TOKEN_KEY="${SESSION_TOKEN_KEY:-temp:sharepoint_3lo}"
FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-http://localhost:3000}"

echo "[deploy] backend → ${SERVICE_NAME}  (AE=${AGENT_ENGINE_RESOURCE})"

gcloud run deploy "${SERVICE_NAME}" --source . --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --allow-unauthenticated --set-env-vars "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},DEPLOY_LOCATION=${DEPLOY_LOCATION},AGENT_ENGINE_RESOURCE=${AGENT_ENGINE_RESOURCE},SESSION_TOKEN_KEY=${SESSION_TOKEN_KEY},FRONTEND_ORIGIN=${FRONTEND_ORIGIN}"

URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --format='value(status.url)')
echo
echo "[deploy] DONE — BACKEND_URL=${URL}"
echo "[deploy] add to .env: BACKEND_URL=${URL}"
