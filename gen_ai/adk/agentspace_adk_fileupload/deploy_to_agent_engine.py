#%%
import vertexai
import os
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

AGENT_DISPLAY_NAME="Comparator"

vertexai.init(
    project="vtxdemos",
    location="us-central1",
    staging_bucket="gs://vtxdemos-staging",
)

app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

agent_config =  {
    "agent_engine" : app,
    "display_name" : AGENT_DISPLAY_NAME,
    "requirements" : [
        "google-genai",
        "google-cloud-aiplatform[agent_engines,adk]",
    ],
    "extra_packages" : [
        "agent.py",
    ],
}

existing_agents=list(agent_engines.list(filter='display_name="Comparator"'))

if existing_agents:
    print(f"Number of existing agents found for {AGENT_DISPLAY_NAME}:" + str(len(list(existing_agents))))

if existing_agents:
    #update the existing agent
    remote_app = existing_agents[0].update(**agent_config)
else:
    #create a new agent
    remote_app = agent_engines.create(**agent_config)



#%%

from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
session = app.create_session(user_id="u_123")

for event in app.stream_query(
        user_id="u_123",
        session_id=session.id,
        message="how are you bro?",
):
    print(event)


#%%
from vertexai import agent_engines

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)
ae = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/4161545958015893504")

#%%
agent_context = '{"message":{"role":"user","parts":[{"text":"what you can do?"}]},"events":[{"content":{"role":"user","parts":[{"text":"how were you built ?"}]},"author":"AgentSpace_root_agent"},{"content":{"role":"model","parts":[{"functionCall":{"name":"agentspaceak","args":{"question":"How were you built?"},"id":"14076651604820872102"}}]},"author":"AgentSpace_root_agent","id":"14076651604820872102"}]}'

for response in ae.streaming_agent_run_with_events(request_json=agent_context):
    print(response)
