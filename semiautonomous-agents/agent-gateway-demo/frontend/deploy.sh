#!/usr/bin/env bash
# Build + deploy the Next.js frontend to Cloud Run.
set -euo pipefail
source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"; : "${DEPLOY_LOCATION:?}"; : "${BACKEND_URL:?set after backend deploy}"
: "${ENTRA_TENANT_ID:?Set after Entra app registration}"; : "${ENTRA_CLIENT_ID:?}"
SERVICE_NAME="${FRONTEND_SERVICE_NAME:-agent-gateway-demo-ui}"

echo "[deploy] frontend → ${SERVICE_NAME}  (backend=${BACKEND_URL})"

gcloud run deploy "${SERVICE_NAME}" --source . --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --allow-unauthenticated --set-build-env-vars="NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL},NEXT_PUBLIC_ENTRA_TENANT_ID=${ENTRA_TENANT_ID},NEXT_PUBLIC_ENTRA_CLIENT_ID=${ENTRA_CLIENT_ID},NEXT_PUBLIC_ENTRA_SCOPES=${ENTRA_SCOPES:-https://graph.microsoft.com/Files.Read offline_access openid profile}"

URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${GOOGLE_CLOUD_PROJECT}" --region="${DEPLOY_LOCATION}" --format='value(status.url)')
echo
echo "[deploy] DONE — FRONTEND_URL=${URL}"
echo
echo "[deploy] IMPORTANT: add ${URL} to your Entra app registration → Authentication → Redirect URIs"
echo "[deploy] add to .env: FRONTEND_URL=${URL}"
