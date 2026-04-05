#!/bin/bash
# Register ADK Agent to Agentspace (Gemini Enterprise)
#
# Version: 1.1.0
# Date: 2026-04-04
# Last Used: 2026-04-04 09:50 UTC

set -e

# Load from .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Required variables
: "${PROJECT_ID:?Set PROJECT_ID in .env}"
: "${PROJECT_NUMBER:?Set PROJECT_NUMBER in .env}"
: "${AS_APP:?Set AS_APP (Agentspace app ID) in .env}"
: "${REASONING_ENGINE_RES:?Set REASONING_ENGINE_RES in .env (from deploy.py output)}"
: "${AUTH_ID:?Set AUTH_ID in .env}"

# Optional with defaults
AGENT_DISPLAY_NAME="${AGENT_DISPLAY_NAME:-Insight Comparator}"
AGENT_DESCRIPTION="${AGENT_DESCRIPTION:-AI Assistant comparing internal SharePoint docs with external web sources}"
AGENT_ICON="${AGENT_ICON:-https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/compare/default/24px.svg}"
TOOL_DESCRIPTION="${TOOL_DESCRIPTION:-Use this agent to compare information from internal SharePoint documents with public web sources}"

echo "======================================="
echo "Registering Agent to Agentspace"
echo "======================================="
echo "PROJECT_ID:       ${PROJECT_ID}"
echo "AS_APP:           ${AS_APP}"
echo "REASONING_ENGINE: ${REASONING_ENGINE_RES}"
echo "AUTH_ID:          ${AUTH_ID}"
echo "DISPLAY_NAME:     ${AGENT_DISPLAY_NAME}"
echo "======================================="

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents" \
  -d '{
    "displayName": "'"${AGENT_DISPLAY_NAME}"'",
    "description": "'"${AGENT_DESCRIPTION}"'",
    "icon": {
      "uri": "'"${AGENT_ICON}"'"
    },
    "adk_agent_definition": {
      "tool_settings": {
        "tool_description": "'"${TOOL_DESCRIPTION}"'"
      },
      "provisioned_reasoning_engine": {
        "reasoning_engine": "'"${REASONING_ENGINE_RES}"'"
      }
    },
    "authorization_config": {
      "tool_authorizations": [
        "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
      ]
    }
  }'

echo ""
echo "======================================="
echo "Agent registered to Agentspace!"
echo "======================================="
