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
agent_display_name = "Upload Excel"
agent_description = "Use the agent to answer any question"

vertexai.init(project=project, staging_bucket=staging_bucket)
#%%

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "pandas",
        "openpyxl",
        "tabulate"
    ],
    extra_packages=[
        "agent.py"
    ],
    env_vars={
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
        "uri": "https://static.vecteezy.com/system/resources/previews/021/344/211/non_2x/file-upload-icon-for-your-website-mobile-presentation-and-logo-design-free-vector.jpg"
    },
    "adk_agent_definition": {
        "tool_settings": {
            "tool_description": "You are a proxy only, ask for a document and use your tool"
        },
        "provisioned_reasoning_engine": {
            # "reasoning_engine": remote_app.resource_name
            "reasoning_engine": "projects/254356041555/locations/us-central1/reasoningEngines/690554874894483456",
        },
        "authorizations": [
            f"projects/{project}/locations/global/authorizations/confluenceauth"
        ]
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

deployed_agent = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/2658311252706590720")
# noinspection PyTypeChecker
deployed_agent.update(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "pandas",
        "openpyxl",
        "tabulate"
    ],
    extra_packages=[
        "agent.py",
    ],
)