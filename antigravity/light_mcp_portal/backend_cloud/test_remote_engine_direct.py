import os
import asyncio
import logging
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

# Fix path to load agents
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

from google.adk.sessions import InMemorySessionService
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from vertexai.agent_engines import AdkApp
from agents.agent import root_agent
import vertexai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_remote")

async def main():
    # Initialize vertexai
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    engine_id = os.environ.get("AGENT_ENGINE_ID")
    if not engine_id:
         print("❌ AGENT_ENGINE_ID not set in .env")
         return
         
    if "/" in engine_id:
        engine_id = engine_id.split("/")[-1]
        
    print(f"Initializing Remote AdkApp for Engine ID: {engine_id}")
    
    # Initialize SessionService for local runner (InMemory is fine for client)
    session_service = InMemorySessionService()
    
    # Initialize the remote app pointing to Vertex AI
    cloud_session_service = VertexAiSessionService(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location="us-central1",
        agent_engine_id=engine_id
    )
    remote_app = AdkApp(agent=root_agent, session_service_builder=lambda: cloud_session_service)
    
    print("Sending query to Remote Agent Engine via async_stream_query...")
    try:
        async for event in remote_app.async_stream_query(
            user_id="default_user",
            message="List ServiceNow incidents"
        ):
            print(f"Received event type: {getattr(event, 'type', 'unknown')}")
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                 for part in event.content.parts:
                     if hasattr(part, 'text') and part.text:
                         print(part.text, end="")
    except Exception as e:
        print(f"\n❌ Error during stream: {e}")
        
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
