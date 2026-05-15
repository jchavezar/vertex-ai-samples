#!/usr/bin/env bash
# Create the Agent-Identity connector for Microsoft Entra 3LO.
# If the alpha CLI surface isn't available in your gcloud, fall back to
# the Console: Agent Registry → select agent → Identity tab → Auth Providers.
set -euo pipefail

source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"; : "${DEPLOY_LOCATION:?}"; : "${CONNECTOR_NAME:?}"
: "${ENTRA_TENANT_ID:?Set after Entra app registration}"
: "${ENTRA_CLIENT_ID:?}"; : "${ENTRA_CLIENT_SECRET:?}"

AUTH_URL="https://login.microsoftonline.com/${ENTRA_TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL="https://login.microsoftonline.com/${ENTRA_TENANT_ID}/oauth2/v2.0/token"
SCOPES="${ENTRA_SCOPES:-https://graph.microsoft.com/Files.Read offline_access openid profile}"

echo "[infra/20] Creating connector ${CONNECTOR_NAME} (Entra 3LO)…"
gcloud alpha agent-identity connectors create "${CONNECTOR_NAME}" --project="${GOOGLE_CLOUD_PROJECT}" --location="${DEPLOY_LOCATION}" --three-legged-oauth-authorization-url="${AUTH_URL}" --three-legged-oauth-token-url="${TOKEN_URL}" --three-legged-oauth-client-id="${ENTRA_CLIENT_ID}" --three-legged-oauth-client-secret="${ENTRA_CLIENT_SECRET}" --allowed-scopes="${SCOPES// /,}"

PROJECT_NUMBER=$(gcloud projects describe "${GOOGLE_CLOUD_PROJECT}" --format='value(projectNumber)')
CONNECTOR_RESOURCE="projects/${PROJECT_NUMBER}/locations/${DEPLOY_LOCATION}/connectors/${CONNECTOR_NAME}"
echo
echo "[infra/20] DONE — CONNECTOR_RESOURCE=${CONNECTOR_RESOURCE}"
echo "[infra/20] add to .env: CONNECTOR_RESOURCE=${CONNECTOR_RESOURCE}"
echo
echo "[infra/20] Now describe it to capture the Auth-Manager redirect URI you must add to your Entra app registration:"
echo "           gcloud alpha agent-identity connectors describe ${CONNECTOR_NAME} --location=${DEPLOY_LOCATION}"
