import asyncio
from agent import video_expert_agent
from vertexai.agent_engines import AdkApp
import vertexai
import os

async def main():
    vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])
    
    local_app = AdkApp(
        agent=video_expert_agent,
        enable_tracing=True
    )
    
    session = await local_app.async_create_session(user_id="user")
    
    async for event in local_app.async_stream_query(
        user_id="user",
        session_id=session.id,
        message="Generate a video of a futuristic william wallace cat"
    ):
        print(type(event))
        print(event)

asyncio.run(main())
