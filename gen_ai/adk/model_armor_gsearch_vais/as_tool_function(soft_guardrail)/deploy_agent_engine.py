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

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-modelarmor"
    ],
    extra_packages=["agent.py"]
)