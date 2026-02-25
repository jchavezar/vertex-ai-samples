
import os
import asyncio
from dotenv import load_dotenv

# Load env vars from parent directory as per main.py logic
load_dotenv(dotenv_path="../.env")

from agent import video_expert_agent
from vertexai.agent_engines import AdkApp
import vertexai

async def test_agent():
    print("Initializing Vertex AI...")
    vertexai.init(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    
    app = AdkApp(agent=video_expert_agent)
    
    print("Creating session...")
    session = await app.async_create_session(user_id="test_user")
    session_id = session["id"] if isinstance(session, dict) else session.id
    print(f"Session created: {session_id}")
    
    prompt = "generate a 4 second video of a cute kitten playing with a yarn ball"
    print(f"Sending prompt: {prompt}")
    
    async for event in app.async_stream_query(
        user_id="test_user",
        session_id=session_id,
        message=prompt
    ):
        print(f"EVENT: {type(event)}")
        print(f"CONTENT: {event}")

if __name__ == "__main__":
    asyncio.run(test_agent())
