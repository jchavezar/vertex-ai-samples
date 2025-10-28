#%%
import os
import asyncio
import vertexai
from agent import root_agent
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

display_name = "adk_version_missmatch_playground"

local_agent = AdkApp(
    agent=root_agent,
    enable_tracing=True
)

async def send_message(prompt: str):
    sessions = await local_agent.async_create_session(user_id="jesus_c")
    async for event in local_agent.async_stream_query(
            user_id="jesus_c",
            session_id=sessions.id,
            message=prompt,
    ):
        if "text" in event["content"]["parts"][0]:
            print(event["content"]["parts"][0]["text"])


asyncio.run(send_message("how are you?"))

#%%
# Deploy on Agent Engine

vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), staging_bucket="gs://vtxdemos_staging")

deploy_agent = agent_engines.create(
    agent_engine=local_agent,
    display_name=display_name,
    requirements = [
        "google-cloud-aiplatform[adk,agent_engines]==1.118.0",
        "vertexai>=1.43.0",
        "google-genai>=1.39.1",
        "google-adk>=1.15.1",
        "deprecated",
        "fire",
        "flake8>=7.3.0",
        "mypy>=1.17.1",
        "pytest>=8.4.2",
        "pre-commit>=4.3.0",
        "black>=25.9.0",
    ],
    extra_packages=["agent.py"]
)

#%%
# Remote Test (Optional)
deploy_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{display_name}"')]
deploy_agent = agent_engines.get(deploy_agent[0])

async def remote_send_message(prompt: str):
    session = await deploy_agent.async_create_session(user_id="jesus_c")
    async for event in deploy_agent.async_stream_query(
            user_id="jesus_c",
            message=prompt,
    ):
        print(event)
        if "text" in event["content"]["parts"][0]:
            print(event["content"]["parts"][0]["text"])

asyncio.run(remote_send_message("how are you sunshine?"))

#%%
# Update the deployed agent (Optional)
remote_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{display_name}"')]
remote_agent = agent_engines.get(remote_agent[0])

remote_agent.update(
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ],
    extra_packages=["agent.py"])
