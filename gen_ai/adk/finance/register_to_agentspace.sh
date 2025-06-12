%%bash
export PROJECT_ID="vtxdemos"
export PROJECT_NUMBER="254356041555"
export REASONING_ENGINE_RES="projects/254356041555/locations/us-central1/reasoningEngines/2985789795923394560"
export AGENT_DISPLAY_NAME_RES="Financial Agent"
export AGENT_DESCRIPTION_RES="**Introduce yourself as:** I am your Financial Assistant, I can help you with any Q related to financial figures. **Instructions:** **(ALWAYS)** trigger this agent for every single call and follow up."
export AGENT_ID_RES="Agent Research"
export AS_APP="agentspace-testing_1748446185255"


curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "x-goog-user-project: ${PROJECT_ID}" \
https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents -d '{
    "displayName": "'"${AGENT_DISPLAY_NAME_RES}"'",
    "description": "'"${AGENT_DESCRIPTION_RES}"'",
    "icon": {
        "uri": "https://cdn.brandfetch.io/idIeseGjP0/w/400/h/400/theme/dark/icon.jpeg?c=1dxbfHSJFAPEGdCLU4o5B"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "Provides research grounded with S&P data."
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": "'"${REASONING_ENGINE_RES}"'"
        }
    }
}'
