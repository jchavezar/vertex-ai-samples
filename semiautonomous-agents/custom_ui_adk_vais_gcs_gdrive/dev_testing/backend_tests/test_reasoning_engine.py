import os
import sys
import logging
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
AGENT_ENGINE_RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()

print(f"Project: {PROJECT}")
print(f"Location: {LOCATION}")
print(f"Resource: {AGENT_ENGINE_RESOURCE}")

vertexai.init(project=PROJECT, location=LOCATION)

try:
    engine = agent_engines.get(AGENT_ENGINE_RESOURCE)
    print("Successfully retrieved agent engine:", engine)
    
    # Try listing sessions
    print("Engine attributes / methods:", dir(engine))
    
    # Try a simple query
    print("Streaming a test query...")
    # Since we need a valid user_id and session_id, let's try calling stream_query with some dummy session if possible,
    # or let's create a session.
    # Note: we need a valid access token. We don't have one in a static script, but let's see if we can create a session
    # with dummy state or no state.
    state = {"temp:drive_access_token": "dummy", "drive_access_token": "dummy"}
    session = engine.create_session(user_id="test_user", state=state)
    print("Created session:", session)
    session_id = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
    print("Session ID:", session_id)
    
    events = []
    for event in engine.stream_query(user_id="test_user", session_id=session_id, message="Hi"):
        print("Received Event:", type(event), event)
        events.append(event)
        
except Exception as e:
    logging.exception("Failed to test agent engine")
