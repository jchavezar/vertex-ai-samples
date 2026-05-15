#!/usr/bin/env bash
# Grant the agent's SA `roles/iap.egressor` on the registered MCP service,
# scoped via the documented CEL attribute `mcp.resourceName`.
set -euo pipefail

source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"; : "${AGENT_ENGINE_RESOURCE:?}"; : "${MCP_SERVICE_RESOURCE:?}"

PROJECT_NUMBER=$(gcloud projects describe "${GOOGLE_CLOUD_PROJECT}" --format='value(projectNumber)')
ENGINE_ID="${AGENT_ENGINE_RESOURCE##*/}"
# Per `IdentityType.AGENT_IDENTITY` docs the per-agent SA is auto-provisioned.
# Format derived from the agent-identity guide; verify with:
#   gcloud iam service-accounts list --filter='email~agent-' --project=${GOOGLE_CLOUD_PROJECT}
AGENT_SA="agent-${ENGINE_ID}@project-${PROJECT_NUMBER}.iam.gserviceaccount.com"

CONDITION_TITLE="${MCP_SERVICE_DISPLAY_NAME:-sharepoint-mcp}-egress"
CEL="resource.type == 'agentregistry.googleapis.com/Service' && mcp.resourceName == '${MCP_SERVICE_RESOURCE}'"

echo "[infra/40] agent_sa=${AGENT_SA}"
echo "[infra/40] mcp     =${MCP_SERVICE_RESOURCE}"
echo "[infra/40] CEL     =${CEL}"

gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" --member="serviceAccount:${AGENT_SA}" --role="roles/iap.egressor" --condition="title=${CONDITION_TITLE},expression=${CEL}"

echo
echo "[infra/40] DONE."
