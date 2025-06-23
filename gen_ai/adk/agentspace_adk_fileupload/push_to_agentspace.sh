%%bash
export PROJECT_ID="vtxdemos"
export PROJECT_NUMBER="254356041555"
export AGENT_AGENT_ID="projects/254356041555/locations/us-central1/reasoningEngines/4161545958015893504"
export AGENT_DISPLAY_NAME="Comparator Agent"
export AGENT_DESCRIPTION="**Instructions:** **(ALWAYS)** let the comparator agent/tool detect the intent and respond all the questions directly, you are a proxy only, do not use your outputs"
export AGENT_ID="Comparator Agent"
export AS_APP="agentspace"

curl -X PATCH -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "x-goog-user-project: ${PROJECT_ID}" \
https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant?updateMask=agent_configs -d '{
    "name": "projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/deep_research",
    "displayName": "Deep Research",
    "agentConfigs": [
    {
      "displayName": "'"${AGENT_DISPLAY_NAME}"'",
      "vertexAiSdkAgentConnectionInfo": {
        "reasoningEngine": "'"${AGENT_AGENT_ID}"'"
      },
      "toolDescription": "'"${AGENT_DESCRIPTION}"'",
      "icon": {
        "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/corporate_fare/default/24px.svg"
      },
      "id": "'"${AGENT_ID}"'"
    }
    ]
  }'
