#%%
import os
import json
import requests
import vertexai
import google.auth
from agent import root_agent
from dotenv import load_dotenv
from vertexai import agent_engines
import google.auth.transport.requests
from vertexai.preview import reasoning_engines

#%%
as_app = os.getenv("AGENTSPACE_ID")
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
staging_bucket = os.getenv("STAGING_BUCKET")
agent_display_name = os.getenv("AGENT_DISPLAY_NAME")
agent_description = os.getenv("AGENT_DESCRIPTION")
template_model_id = os.getenv("TEMPLATE_MODEL_ARMOR_ID")

vertexai.init(project=project, staging_bucket=staging_bucket)

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-modelarmor"
    ],
    extra_packages=[
        "agent.py",
    ],
    env_vars={
        "TEMPLATE_MODEL_ARMOR_ID":template_model_id
    }
)

#%%
# Testing Agent Engine
agent_context = '{"message":{"role":"user","parts":[{"text":"Im Jesus Chavez"}]}}'

deployed_agent = agent_engines.get(remote_app.resource_name)

for response in deployed_agent.streaming_agent_run_with_events(request_json=agent_context):
    print(response)

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
        "uri": "https://symbols.getvecta.com/stencil_4/12_google-cloud-armor.566a831ff9.svg"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, ask for a document and use your tool"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine": remote_app.resource_name
        }
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "x-goog-user-project": project,
}


response = requests.post(api_url, headers=headers, data=json.dumps(payload))

