import json
import requests
import google.auth

as_app = "agentspace-testing_1748446185255"
agent_display_name = "Excel File Upload"
agent_description = "Use the agent to answer any question"
resource_name = "projects/254356041555/locations/us-central1/reasoningEngines/4066033581934247936"

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
        "uri": "https://static.vecteezy.com/system/resources/previews/021/344/211/non_2x/file-upload-icon-for-your-website-mobile-presentation-and-logo-design-free-vector.jpg"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, ask for a document and use your tool"
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