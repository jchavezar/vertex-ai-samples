#%%
import vertexai
from agent import root_agent
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

vertexai.init(project="vtxdemos", staging_bucket="gs://vtxdemos-staging")

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

#%%
session = app.create_session(user_id="u_123")
for event in app.stream_query(
        user_id="u_123",
        session_id=session.id,
        message="what you can do?",
):
    print(event)


#%%
# deploy

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
    extra_packages=["agent.py"]
)

#%%

rm = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/6289954178785607680")

agent_context = '{"message":{"role":"user","parts":[{"text":"what you can do?"}]},"events":[{"content":{"role":"user","parts":[{"text":"how were you built ?"}]},"author":"AgentSpace_root_agent"},{"content":{"role":"model","parts":[{"functionCall":{"name":"agentspaceak","args":{"question":"How were you built?"},"id":"14076651604820872102"}}]},"author":"AgentSpace_root_agent","id":"14076651604820872102"}]}'

for response in rm.streaming_agent_run_with_events(request_json=agent_context):
    print(response)