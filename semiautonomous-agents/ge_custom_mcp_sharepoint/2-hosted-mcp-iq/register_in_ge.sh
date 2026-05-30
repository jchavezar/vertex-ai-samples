#!/usr/bin/env bash
# Register the Microsoft-hosted Work IQ SharePoint MCP server as a BYO_MCP
# custom-MCP datastore on a Gemini Enterprise engine via Discovery Engine
# setUpDataConnector.
#
# Difference vs 1-custom-mcp/register_in_ge.sh: instance_uri points at
# Microsoft's hosted endpoint; everything else (Entra OAuth client, scopes,
# DE shape) is identical. Same MS365 MCP Server Entra app for both options.
#
# Required env:
#   GE_ENGINE_ID  - target Gemini Enterprise engine id (operator creates first)
# Optional env:
#   GE_PROJECT_ID (default vtxdemos), GE_LOCATION (default global),
#   GE_COLLECTION_ID (default default_collection),
#   DATASTORE_ID (default workiqsp-<epoch>)
set -euo pipefail

# GE_ENGINE_ID optional: if unset, the datastore is created but not attached
# to any engine — the operator either creates a new engine with this
# dataStoreId or PATCHes an existing engine afterwards.
GE_ENGINE_ID="${GE_ENGINE_ID:-}"

GE_PROJECT_ID="${GE_PROJECT_ID:-vtxdemos}"
GE_LOCATION="${GE_LOCATION:-global}"
GE_COLLECTION_ID="${GE_COLLECTION_ID:-default_collection}"
DATASTORE_ID="${DATASTORE_ID:-workiqsp-$(date +%s)}"
COLLECTION_DISPLAY_NAME="${COLLECTION_DISPLAY_NAME:-Work IQ SharePoint (hosted, Preview)}"

# Microsoft-hosted Work IQ SharePoint MCP (admin panel, sockcop tenant, 2026-05-27).
MCP_SERVER_URL="${MCP_SERVER_URL:-https://agent365.svc.cloud.microsoft/agents/servers/mcp_SharePointRemoteServer}"

TENANT_ID="de46a3fd-0d68-4b25-8343-6eb5d71afce9"
CLIENT_ID="030b6aac-63d1-40e9-8d80-7ce928b839b8"
AUTH_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token"
# agent365 requires its own resource scope (McpServers.SharePoint.All) —
# Graph scopes alone return 403 "Scope 'McpServers.SharePoint.All' is not
# present in the request." Verified 2026-05-29 by minting a delegated
# token with this exact scope and successfully calling tools/list on
# https://agent365.svc.cloud.microsoft/agents/servers/mcp_SharePointRemoteServer.
# The "Agent Tools" service principal (appId ea9ffc3e-8a23-4a7d-836d-234d7c7565c1)
# must exist in the tenant; create it once via
# POST https://graph.microsoft.com/v1.0/servicePrincipals {"appId":"ea9ffc3e-..."}.
SCOPES="openid profile email offline_access https://agent365.svc.cloud.microsoft/McpServers.SharePoint.All"

CLIENT_SECRET=$(gcloud secrets versions access latest --secret=entra-ms365-mcp-client-secret --project=vtxdemos)
if [[ -z "$CLIENT_SECRET" ]]; then echo "Failed to read entra-ms365-mcp-client-secret from Secret Manager" >&2; exit 1; fi

PROJECT_NUMBER=$(gcloud projects describe "$GE_PROJECT_ID" --format='value(projectNumber)')
BASE_URL="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/${GE_LOCATION}"
TOKEN=$(gcloud auth print-access-token)

MCP_DESC="Microsoft Work IQ SharePoint MCP server (Preview, hosted by Microsoft Agent 365). Provides 35+ tools for SharePoint sites, document libraries, files (read/write/move/copy, 5 MB cap), lists, columns, sharing and sensitivity labels. Use whenever the user asks about SharePoint sites, libraries, files, lists or columns."
MCP_INSTR="When the user asks about SharePoint content, ALWAYS call the Work IQ MCP tools (findSite, findFileOrFolder, getFolderChildren, readSmallTextFile, listLists, listListItems). Prefer findFileOrFolder for free-text file/folder search and findSite for site discovery. Files larger than 5 MB cannot be read via this server. Never tell the user the connector is unavailable - always attempt the tool call first."

export DATASTORE_ID COLLECTION_DISPLAY_NAME MCP_SERVER_URL AUTH_URI TOKEN_URI SCOPES CLIENT_ID CLIENT_SECRET MCP_DESC MCP_INSTR
BODY=$(python3 -c "import json,os; print(json.dumps({'collectionId': os.environ['DATASTORE_ID'], 'collectionDisplayName': os.environ['COLLECTION_DISPLAY_NAME'], 'dataConnector': {'dataSource': 'custom_mcp', 'params': {'oauth_access_token': 'placeholder-real-auth-via-3LO'}, 'connectorModes': ['ACTIONS','FEDERATED'], 'bapConfig': {'supportedConnectorModes': ['ACTIONS']}, 'entities': [{'entityName': 'mcp_data'}], 'actionConfig': {'isActionConfigured': True, 'createBapConnection': True, 'actionParams': {'instance_uri': os.environ['MCP_SERVER_URL'], 'auth_type': 'OAUTH', 'auth_uri': os.environ['AUTH_URI'], 'token_uri': os.environ['TOKEN_URI'], 'scopes': os.environ['SCOPES'], 'client_id': os.environ['CLIENT_ID'], 'client_secret': os.environ['CLIENT_SECRET'], 'mcp_server_source': 'BYO_MCP', 'registry_mcp_server_name': '', 'mcp_server_description': os.environ['MCP_DESC'], 'mcp_agent_instructions': os.environ['MCP_INSTR']}}}}))")

echo "Registering ${DATASTORE_ID} (project ${GE_PROJECT_ID} / ${PROJECT_NUMBER})${GE_ENGINE_ID:+ -> engine ${GE_ENGINE_ID}}"
echo "  MCP URL: ${MCP_SERVER_URL}"

HTTP_STATUS=$(curl -sS -o /tmp/setup_dc_workiq.json -w "%{http_code}" -X POST -H "Authorization: Bearer ${TOKEN}" -H "x-goog-user-project: ${GE_PROJECT_ID}" -H "Content-Type: application/json" "${BASE_URL}:setUpDataConnector" -d "${BODY}")

if [[ "$HTTP_STATUS" != "200" && "$HTTP_STATUS" != "201" ]]; then
  echo "setUpDataConnector failed (HTTP ${HTTP_STATUS}):" >&2
  cat /tmp/setup_dc_workiq.json >&2
  exit 2
fi

cat /tmp/setup_dc_workiq.json
echo ""
echo "Done. Datastore: ${DATASTORE_ID}_mcp_data (location ${GE_LOCATION}, collection ${GE_COLLECTION_ID})."
echo "Next: create or PATCH a GE engine to include this dataStoreId, then click Re-authenticate in the GE console."
