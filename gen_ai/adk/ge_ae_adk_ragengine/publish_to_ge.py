import json
import requests
import google.auth

as_app = "agentspace-testing_1748446185255"
agent_display_name = "Q3 2025 Report Agent"
agent_description = "Use the agent to answer any question"
resource_name = "projects/254356041555/locations/us-central1/reasoningEngines/428813932879151104"

#%%
# Register on Agentspace
# Get default credentials and a request object

credentials, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()

credentials.refresh(auth_req)
access_token = credentials.token


api_url = (
    f"https://discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/global/"
    f"collections/default_collection/engines/{as_app}/assistants/default_assistant/agents"
)

payload = {
    "displayName": agent_display_name,
    "description": agent_description,
    "icon": {
        "uri": "https://www.svgrepo.com/show/533555/engine.svg"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, use your tool"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": resource_name,
        },
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "x-goog-user-project": project,
}


response = requests.post(api_url, headers=headers, data=json.dumps(payload))