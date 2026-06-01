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
    state = {"temp:drive_access_token": "dummy", "drive_access_token": "dummy"}
    session = engine.create_session(user_id="test_user", state=state)
    session_id = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
    print("Created Session ID:", session_id)
    
    print("Streaming query...")
    for event in engine.stream_query(user_id="test_user", session_id=session_id, message="Search my files for goog 10k"):
        print("\n--- NEW EVENT ---")
        print("Type:", type(event))
        print("Repr:", repr(event))
        print("Str:", str(event))
        try:
            print("Attributes:", dir(event))
        except Exception:
            pass
except Exception as e:
    logging.exception("Failed to run inspection")
