#%%
import os
import json
import requests
import vertexai
import google.auth
from agent import root_agent
from vertexai import agent_engines
import google.auth.transport.requests
from vertexai.preview import reasoning_engines

as_app = "agentspace-testing_1748446185255"
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
staging_bucket = "gs://vtxdemos-staging"
agent_display_name = "Image Object Detector"
agent_description = "Agent to either ask general questions or detect objects from images"
agent_engine_display_name = "image_object_detector"

vertexai.init(project=project, staging_bucket=staging_bucket)
#%%

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    display_name=agent_engine_display_name,
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-genai",
        "google-adk",
        "pydantic",
        "Pillow",
    ],
    extra_packages=[
        "agent.py",
    ],
)

#%%
# Testing Agent Engine
# agent_context = '{"message":{"role":"user","parts":[{"text":"Im Jesus Chavez"}]}}'
#
# deployed_agent = agent_engines.get(remote_app.resource_name)
#
# for response in deployed_agent.streaming_agent_run_with_events(request_json=agent_context):
#     print(response)

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
    "x-goog-user-project": project,
}


response = requests.post(api_url, headers=headers, data=json.dumps(payload))


# Update Agent Engine [Optional]
#%%

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

# deployed_agent = agent_engines.get(remote_app.resource_name)
agent_resource_name = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{agent_engine_display_name}"')][0]
deployed_agent = agent_engines.get(agent_resource_name)

# noinspection PyTypeChecker
deployed_agent.update(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-genai",
        "google-adk",
        "pydantic",
        "Pillow",
    ],
    extra_packages=[
        "agent.py",
    ],
)

# Testing Agent Deployed
#%%
agent_resource_name = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{agent_engine_display_name}"')][0]
deployed_agent = agent_engines.get(agent_resource_name)
agent_context = ('{"message":{"role":"user","parts":[{"text":"Hi Detect an image of a cat"}]}}')

for response in deployed_agent.streaming_agent_run_with_events(request_json=agent_context):
    print(response)