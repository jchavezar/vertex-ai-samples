#%%
import json
import os
import requests
import google.auth
from vertexai import agent_engines
import google.auth.transport.requests

as_app = "agentspace-testing_1748446185255"
project_hardcoded = "vtxdemos"
location = "us-central1"
staging_bucket = "gs://vtxdemos-staging"
agent_display_name = "AP News Agent"
agent_description = "Use your tool to answer any question, you are a proxy only"
agent_engine_id = "projects/254356041555/locations/us-central1/reasoningEngines/6960440767449923584"

remote_app = agent_engines.get(resource_name=agent_engine_id)

# Register on Agentspace
# Get default credentials and a request object

credentials, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()

credentials.refresh(auth_req)
access_token = credentials.token


api_url = (
    f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_hardcoded}/locations/global/"
    f"collections/default_collection/engines/{as_app}/assistants/default_assistant/agents"
)

payload = {
    "displayName": agent_display_name,
    "description": agent_description,
    "icon": {
        "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/frame_inspect/default/24px.svg"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, use your internal tool for everything"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": remote_app.resource_name
        },
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "x-goog-user-project": project_hardcoded,
}


response = requests.post(api_url, headers=headers, data=json.dumps(payload))
print(response.json())