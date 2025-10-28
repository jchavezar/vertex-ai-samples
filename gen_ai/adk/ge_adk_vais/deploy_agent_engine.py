#%%
import os
import asyncio
import vertexai
from agent import root_agent
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

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
        print(event)

asyncio.run(send_message("what are the latest news about AI and give me the date of those news"))

#%%
# Deploy on Agent Engine

vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), staging_bucket="gs://vtxdemos_staging")

display_name = "ge_adk_vais_agent"
deploy_agent = agent_engines.create(
    agent_engine=local_agent,
    display_name=display_name,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ],
    extra_packages=["agent.py"]
)

#%%
# Remote Test (Optional)
async def remote_send_message(prompt: str):
    session = await deploy_agent.async_create_session(user_id="jesus_c")
    async for event in deploy_agent.async_stream_query(
            user_id="jesus_c",
            session_id=session["id"],
            message=prompt,
    ):
        print(event)

asyncio.run(remote_send_message("what are the latest news about AI and give me the date of those news"))

#%%
# Update the deployed agent (Optional)
remote_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{display_name}"')]
remote_agent = agent_engines.get(remote_agent[0])

remote_agent.update(
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ],
    extra_packages=["agent.py"])
