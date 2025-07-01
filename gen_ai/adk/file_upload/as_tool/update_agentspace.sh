%%bash
export PROJECT_ID="vtxdemos"
export PROJECT_NUMBER="254356041555"
export REASONING_ENGINE_RES="projects/254356041555/locations/us-central1/reasoningEngines/4951399927038083072"
export AGENT_DISPLAY_NAME_RES="Uploader 24 Jun v3"
export AGENT_DESCRIPTION_RES="You are a proxy only, Use always you agent to know your mission"
export AGENT_ID_RES="Super The Super Uploader Agent"
export AS_APP="agentspace-testing_1748446185255"


curl -X PATCH -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "x-goog-user-project: ${PROJECT_ID}" \
https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/agentspace-testing_1748446185255/assistants/default_assistant/agents/7241341353697183458 -d '{
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
