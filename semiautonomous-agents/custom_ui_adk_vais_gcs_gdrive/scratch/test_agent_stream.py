import os
import subprocess
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv()

PROJECT = "vtxdemos"
LOCATION = "us-central1"
RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE")

print(f"Project: {PROJECT}, Location: {LOCATION}")
vertexai.init(project=PROJECT, location=LOCATION)

print(f"Retrieving engine: {RESOURCE}")
engine = agent_engines.get(RESOURCE)

# Attempt to fetch a valid access token from gcloud CLI
try:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
    print(f"Obtained valid token from gcloud: {token[:15]}...")
except Exception as e:
    print(f"Could not fetch gcloud token, using fallback: {e}")
    token = "mock-token"

print("Starting session...")
session = engine.create_session(user_id="test-user", state={"drive_access_token": token, "temp:drive_access_token": token})
sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
print(f"Session initialized: {sid}")

print("Streaming query...")
try:
    for event in engine.stream_query(user_id="test-user", session_id=sid, message="Show recently modified files"):
        print(f"EVENT: {event}")
except Exception as e:
    import traceback
    traceback.print_exc()
