#%%
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

vertexai.init(
    project="vtxdemos",
    location="us-central1",
    staging_bucket="gs://vtxdemos-staging",
)

from agent_1.agent import root_agent as agent1
from agent_2.agent import root_agent as agent2

app = reasoning_engines.AdkApp(
    agent=agent1,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    agent_engine=app,
    display_name="sports_agent",
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ]
)
print("Agent Engine 1 Deployed")
agent1_resource_name = remote_app.resource_name

vertexai.init(
    project="a2a-sockcop",
    location="us-central1",
    staging_bucket="gs://a2a-sockcop-staging",
)

app = reasoning_engines.AdkApp(
    agent=agent2,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    agent_engine=app,
    display_name="news_agent",
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ]
)
print("Agent Engine 2 Deployed")
agent2_resource_name = remote_app.resource_name
