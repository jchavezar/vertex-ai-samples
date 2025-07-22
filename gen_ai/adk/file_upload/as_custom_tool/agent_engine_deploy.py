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
# Deploy Agent Engine
remote_app = agent_engines.create(
    # display_name="file_upload_custom_tool",
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
    extra_packages=["agent.py"]
)

""#%%
# Update Agent Engine
remote_app = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/1779229716067123200")
remote_app.update(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
    extra_packages=["agent.py"]
)
