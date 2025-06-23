%%bash
export PROJECT_ID="vtxdemos"
export PROJECT_NUMBER="254356041555"
export REASONING_ENGINE_RES="projects/254356041555/locations/us-central1/reasoningEngines/8800429496067948544"
export REASONING_ENGINE_RES="projects/254356041555/locations/us-central1/reasoningEngines/5003895010194620416"
export AGENT_DISPLAY_NAME_RES="Super Uploader Agent v3"
export AGENT_DESCRIPTION_RES="You are a proxy only, Use always you agent to know your mission"
export AGENT_ID_RES="Super Uploader Agent"
export AS_APP="agentspace-testing_1748446185255"


curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "x-goog-user-project: ${PROJECT_ID}" \
https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents -d '{
    "displayName": "'"${AGENT_DISPLAY_NAME_RES}"'",
    "description": "'"You are an Assistant with multiple tools"'",
    "icon": {
        "uri": "https://img.icons8.com/?size=100&id=60984&format=png&color=000000"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, ask for a document and use your tool"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": "'"${REASONING_ENGINE_RES}"'"
        }
    }
}'
