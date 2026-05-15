#!/usr/bin/env bash
# Deploy the MCP server to Cloud Run (HTTPS, public ingress, OAuth-gated by the server itself).
set -euo pipefail

PROJECT="${PROJECT:-sharepoint-wif}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-firestore-rag-mcp}"
COLLECTION="${COLLECTION:-mcp_docs}"
OAUTH_CLIENT_ID="${OAUTH_CLIENT_ID:-}"
ALLOWED_DOMAIN="${ALLOWED_DOMAIN:-}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/docparse/${SERVICE}:latest"

if [[ -z "$OAUTH_CLIENT_ID" ]]; then
  echo "WARN: OAUTH_CLIENT_ID is empty — server will accept ANY valid Google token. Set OAUTH_CLIENT_ID to the client_id you registered for Gemini Enterprise."
fi

echo "=== Build image ==="
gcloud builds submit --tag "$IMAGE" --project="$PROJECT" --region="$REGION" .

echo "=== Deploy Cloud Run service ==="
ENV_VARS="FIRESTORE_PROJECT=${PROJECT},FIRESTORE_COLLECTION=${COLLECTION}"
[[ -n "$OAUTH_CLIENT_ID" ]] && ENV_VARS="${ENV_VARS},OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}"
[[ -n "$ALLOWED_DOMAIN" ]] && ENV_VARS="${ENV_VARS},ALLOWED_DOMAIN=${ALLOWED_DOMAIN}"

gcloud run deploy "$SERVICE" --image="$IMAGE" --project="$PROJECT" --region="$REGION" --platform=managed --allow-unauthenticated --port=8080 --memory=512Mi --cpu=1 --min-instances=0 --max-instances=4 --timeout=300 --set-env-vars="$ENV_VARS"

URL=$(gcloud run services describe "$SERVICE" --region="$REGION" --project="$PROJECT" --format='value(status.url)')
echo
echo "=== Done ==="
echo "Service URL : $URL"
echo "MCP URL     : ${URL}/mcp/"
echo "Health      : ${URL}/healthz"
