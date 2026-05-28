#!/usr/bin/env bash
# Register this Cloud Run MCP server as a BYO_MCP custom-MCP datastore on
# a Gemini Enterprise engine via Discovery Engine setUpDataConnector.
#
# Adapted from:
#   ../atlassian-jira-integration/option-b-direct-remote-mcp/register_datastore.py
#
# Required env:
#   GE_ENGINE_ID  - target Gemini Enterprise engine id (operator creates first)
#   MCP_SERVER_URL - https://<cloud-run>.run.app/mcp
# Optional env:
#   GE_PROJECT_ID (default vtxdemos), GE_LOCATION (default global),
#   GE_COLLECTION_ID (default default_collection),
#   DATASTORE_ID (default sharepointmcp-<epoch>)
set -euo pipefail

: "${GE_ENGINE_ID:?GE_ENGINE_ID is required (the GE engine to attach to)}"
: "${MCP_SERVER_URL:?MCP_SERVER_URL is required (e.g. https://...run.app/mcp)}"

GE_PROJECT_ID="${GE_PROJECT_ID:-vtxdemos}"
GE_LOCATION="${GE_LOCATION:-global}"
GE_COLLECTION_ID="${GE_COLLECTION_ID:-default_collection}"
DATASTORE_ID="${DATASTORE_ID:-sharepointmcp-$(date +%s)}"
COLLECTION_DISPLAY_NAME="${COLLECTION_DISPLAY_NAME:-SharePoint MCP (Entra)}"

TENANT_ID="de46a3fd-0d68-4b25-8343-6eb5d71afce9"
CLIENT_ID="030b6aac-63d1-40e9-8d80-7ce928b839b8"
AUTH_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token"
SCOPES="openid profile email offline_access https://graph.microsoft.com/Sites.ReadWrite.All https://graph.microsoft.com/Files.ReadWrite.All https://graph.microsoft.com/User.Read"

CLIENT_SECRET=$(gcloud secrets versions access latest --secret=entra-ms365-mcp-client-secret --project=vtxdemos)
if [[ -z "$CLIENT_SECRET" ]]; then echo "Failed to read entra-ms365-mcp-client-secret from Secret Manager" >&2; exit 1; fi

PROJECT_NUMBER=$(gcloud projects describe "$GE_PROJECT_ID" --format='value(projectNumber)')
BASE_URL="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/${GE_LOCATION}"
TOKEN=$(gcloud auth print-access-token)

MCP_DESC="SharePoint MCP server. Provides search and read access to SharePoint sites, document libraries, folders and files (PDF/docx/text) via Microsoft Graph. Use whenever the user asks about SharePoint sites, libraries, files or document contents."
MCP_INSTR="When the user asks about SharePoint content, files, libraries or sites, ALWAYS call the SharePoint MCP tools (search, fetch, list_sites, list_libraries, list_files, read_file). Prefer search(query) for free-text questions and fetch(id) to read a specific document. Never tell the user the connector is unavailable - always attempt the tool call first."

export DATASTORE_ID COLLECTION_DISPLAY_NAME MCP_SERVER_URL AUTH_URI TOKEN_URI SCOPES CLIENT_ID CLIENT_SECRET MCP_DESC MCP_INSTR
BODY=$(python3 -c "import json,os; print(json.dumps({'collectionId': os.environ['DATASTORE_ID'], 'collectionDisplayName': os.environ['COLLECTION_DISPLAY_NAME'], 'dataConnector': {'dataSource': 'custom_mcp', 'params': {'oauth_access_token': 'placeholder-real-auth-via-3LO'}, 'connectorModes': ['ACTIONS','FEDERATED'], 'bapConfig': {'supportedConnectorModes': ['ACTIONS']}, 'entities': [{'entityName': 'mcp_data'}], 'actionConfig': {'isActionConfigured': True, 'createBapConnection': True, 'actionParams': {'instance_uri': os.environ['MCP_SERVER_URL'], 'auth_type': 'OAUTH', 'auth_uri': os.environ['AUTH_URI'], 'token_uri': os.environ['TOKEN_URI'], 'scopes': os.environ['SCOPES'], 'client_id': os.environ['CLIENT_ID'], 'client_secret': os.environ['CLIENT_SECRET'], 'mcp_server_source': 'BYO_MCP', 'registry_mcp_server_name': '', 'mcp_server_description': os.environ['MCP_DESC'], 'mcp_agent_instructions': os.environ['MCP_INSTR']}}}}))")

echo "Registering ${DATASTORE_ID} on engine ${GE_ENGINE_ID} (project ${GE_PROJECT_ID} / ${PROJECT_NUMBER})"

HTTP_STATUS=$(curl -sS -o /tmp/setup_dc.json -w "%{http_code}" -X POST -H "Authorization: Bearer ${TOKEN}" -H "x-goog-user-project: ${GE_PROJECT_ID}" -H "Content-Type: application/json" "${BASE_URL}:setUpDataConnector" -d "${BODY}")

if [[ "$HTTP_STATUS" != "200" && "$HTTP_STATUS" != "201" ]]; then
  echo "setUpDataConnector failed (HTTP ${HTTP_STATUS}):" >&2
  cat /tmp/setup_dc.json >&2
  exit 2
fi

cat /tmp/setup_dc.json
echo ""
echo "Done. Attach ${DATASTORE_ID}_mcp_data to engine ${GE_ENGINE_ID} via the GE console (Data stores -> Edit) if not auto-attached, then click Re-authenticate to bind the Entra OAuth client."
