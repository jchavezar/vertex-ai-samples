#!/usr/bin/env bash
# Provision the Agent Gateway via REST (the gcloud CLI doesn't have
# `agent-gateways` commands yet — uses networkservices.googleapis.com/v1beta1).
# PERMANENT binding for the (project, region) once any agent is bound.
set -euo pipefail

source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"; : "${DEPLOY_LOCATION:?}"; : "${GATEWAY_NAME:?}"

PROJECT_NUMBER=$(gcloud projects describe "${GOOGLE_CLOUD_PROJECT}" --format='value(projectNumber)')
PARENT="projects/${PROJECT_NUMBER}/locations/${DEPLOY_LOCATION}"
TOKEN="$(gcloud auth print-access-token)"

# Check if it already exists (idempotent).
EXISTING=$(curl -s -H "Authorization: Bearer ${TOKEN}" "https://networkservices.googleapis.com/v1beta1/${PARENT}/agentGateways/${GATEWAY_NAME}" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('name',''))" 2>/dev/null || echo "")

if [[ -n "$EXISTING" && "$EXISTING" != *"NOT_FOUND"* ]]; then
  echo "[infra/10] Gateway already exists: ${EXISTING}"
  GATEWAY_RESOURCE="${EXISTING}"
else
  echo "[infra/10] Creating Agent Gateway ${GATEWAY_NAME} in ${GOOGLE_CLOUD_PROJECT}/${DEPLOY_LOCATION}"
  echo "           This binding is PERMANENT for that project/region."

  BODY=$(cat <<EOF
{
  "protocols": ["MCP"],
  "googleManaged": { "governedAccessPath": "AGENT_TO_ANYWHERE" },
  "registries": ["//agentregistry.googleapis.com/projects/${PROJECT_NUMBER}/locations/${DEPLOY_LOCATION}"]
}
EOF
)
  RESP=$(curl -s -X POST -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" -H "x-goog-user-project: ${GOOGLE_CLOUD_PROJECT}" "https://networkservices.googleapis.com/v1beta1/${PARENT}/agentGateways?agentGatewayId=${GATEWAY_NAME}" -d "${BODY}")
  echo "[infra/10] Create response:"
  echo "${RESP}" | python3 -m json.tool
  GATEWAY_RESOURCE="${PARENT}/agentGateways/${GATEWAY_NAME}"
fi

echo
echo "[infra/10] Granting Reasoning Engine SA permission to USE the gateway…"
ROLE_ID="AgentGatewayUse"
if ! gcloud iam roles describe "${ROLE_ID}" --project="${GOOGLE_CLOUD_PROJECT}" >/dev/null 2>&1; then
  gcloud iam roles create "${ROLE_ID}" --project="${GOOGLE_CLOUD_PROJECT}" --title="Agent Gateway use" --permissions="networkservices.agentGateways.get,networkservices.agentGateways.use,networkservices.operations.get" 2>&1 | tail -2
fi
gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com" --role="projects/${GOOGLE_CLOUD_PROJECT}/roles/${ROLE_ID}" --condition=None 2>&1 | tail -2 || true

echo
echo "[infra/10] DONE — GATEWAY_RESOURCE=${GATEWAY_RESOURCE}"
echo "[infra/10] add to .env: GATEWAY_RESOURCE=${GATEWAY_RESOURCE}"
