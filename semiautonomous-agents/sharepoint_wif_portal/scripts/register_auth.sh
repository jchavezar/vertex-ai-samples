#!/bin/bash
# Register Authorization Resource in Discovery Engine
# This allows Agentspace to manage OAuth tokens for the agent
#
# Version: 1.1.0
# Date: 2026-04-04
# Last Used: 2026-04-04 09:45 UTC
# Fix: Added user_impersonation scope for WIF token exchange

set -e

# Load from .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Required variables
: "${PROJECT_NUMBER:?Set PROJECT_NUMBER in .env}"
: "${AUTH_ID:?Set AUTH_ID in .env}"
: "${OAUTH_CLIENT_ID:?Set OAUTH_CLIENT_ID in .env}"
: "${OAUTH_CLIENT_SECRET:?Set OAUTH_CLIENT_SECRET in .env}"
: "${TENANT_ID:?Set TENANT_ID in .env}"

# Microsoft Entra ID OAuth endpoints
OAUTH_TOKEN_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token"

# Build authorization URL
REDIRECT_URI="https://vertexaisearch.cloud.google.com/oauth-redirect"
# CRITICAL: user_impersonation scope required for WIF token exchange
SCOPES="openid%20profile%20email%20api%3A%2F%2F${OAUTH_CLIENT_ID}%2Fuser_impersonation"
OAUTH_AUTH_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize?response_type=code&client_id=${OAUTH_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&scope=${SCOPES}&prompt=consent"

echo "======================================="
echo "Registering Authorization Resource"
echo "======================================="
echo "PROJECT_NUMBER: ${PROJECT_NUMBER}"
echo "AUTH_ID:        ${AUTH_ID}"
echo "TENANT_ID:      ${TENANT_ID}"
echo "======================================="

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations?authorizationId=${AUTH_ID}" \
  -d '{
    "name": "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'",
    "serverSideOauth2": {
      "clientId": "'"${OAUTH_CLIENT_ID}"'",
      "clientSecret": "'"${OAUTH_CLIENT_SECRET}"'",
      "authorizationUri": "'"${OAUTH_AUTH_URI}"'",
      "tokenUri": "'"${OAUTH_TOKEN_URI}"'"
    }
  }'

echo ""
echo "======================================="
echo "Authorization registered!"
echo "Resource: projects/${PROJECT_NUMBER}/locations/global/authorizations/${AUTH_ID}"
echo "======================================="
