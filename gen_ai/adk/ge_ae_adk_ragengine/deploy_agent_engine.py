#%%
import os
import asyncio
import vertexai
from typing import Union, Any
from agent import root_agent
from vertexai import agent_engines

client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

display_agent_engine_name = "ge_ae_adk_ragengine"

local_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

async def send_message(prompt: str, app: Union[vertexai.agent_engines.AdkApp, Any]):
    session = await app.async_create_session(user_id="jesus_c")
    async for event in app.async_stream_query(
            user_id="jesus_c",
            session_id=session["id"] if "id" in session else session.id,
            message=prompt,
    ):
        print(event)

asyncio.run(send_message("hi", app=local_app))

#%%
# Deploy to Agent Engine
remote_app = client.agent_engines.create(
    agent=local_app,
    config={
        "display_name": display_agent_engine_name,
        "staging_bucket": "gs://vtxdemos-staging",
        "requirements": "requirements.txt",
        "extra_packages": ["agent.py"],
    }
)

#%%
# Test Agent Engine
resource_name = [agent.api_resource.name for agent in client.agent_engines.list() if agent.api_resource.display_name==display_agent_engine_name]
remote_app = client.agent_engines.get(name=resource_name[0])
asyncio.run(send_message("hi", app=remote_app))

#%%
## Update the deployed agent engine [Optional]
resource_name = [agent.api_resource.name for agent in client.agent_engines.list() if agent.api_resource.display_name==display_agent_engine_name]

remote_app = client.agent_engines.update(
    name=resource_name[0],
    agent=local_app,
    config={
        "display_name": display_agent_engine_name,
        "staging_bucket": "gs://vtxdemos-staging",
        "requirements": "requirements.txt",
        "extra_packages": ["agent.py"],
    }
)


#%%
## Force Delete Agents [Optional]
resource_name = [agent.api_resource.name for agent in client.agent_engines.list() if agent.api_resource.display_name==display_agent_engine_name]

client.agent_engines.delete(
    name=resource_name[0],
    force=True
)