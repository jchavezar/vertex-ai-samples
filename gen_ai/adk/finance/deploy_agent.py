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
            message="whats the rating for GeoThermal Power Corp?",
):
    print(event)


#%%
# deploy

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-storage"
    ],
    extra_packages=["agent.py"]
)

#%%
remote_session = remote_app.create_session(user_id="u_456")

#%%
for event in remote_app.stream_query(
        user_id="u_456",
        session_id=remote_session["id"],
        message="Analyze my current portfolio risk based on sector and the latest tariff news",
):
    print(event)


#%%
# import vertexai
#
# vertexai.init(project="vtxdemos", staging_bucket="gs://vtxdemos-staging")
#
# from vertexai import agent_engines
# agent_engines.delete("projects/254356041555/locations/us-central1/reasoningEngines/1720489406864818176", force=True)