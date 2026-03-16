import os
import vertexai
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

if LOCATION == "global":
    LOCATION = "us-central1"

print(f"Initializing Vertex AI in Project: {PROJECT_ID}, Location: {LOCATION}")
vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

print("Fetching agent engine...")
# The engine name from our deploy output
engine_name = "projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/7262493104274407424"

remote_app = client.agent_engines.get(name=engine_name)

print("Agent Engine loaded.")
print(f"Name: {remote_app.api_resource.name}")
print(f"Display Name: {remote_app.api_resource.display_name}")
print(f"Description: {remote_app.api_resource.description}")

# Verbose prints removed for cleaner output

print("\n--- Testing Agent Engine ---")
print("We need to simulate the multi-turn session.")
print("Creating a session ID...")
user_id = "tester-obj"

try:
    print("Creating session in Agent Engine...")
    remote_session = remote_app.create_session(user_id=user_id)
    session_id = remote_session["id"]
    print(f"Session created with ID: {session_id}")
except Exception as e:
    print(f"Error creating session: {e}")
    session_id = "test-session-fallback-12345"

print("1. Sending initial prompt...")
initial_prompt = "Tell me a very brief fact about quantum computing."
print(f"User: {initial_prompt}")

try:
    response_stream = remote_app.stream_query(message=initial_prompt, user_id=user_id, session_id=session_id)
    for chunk in response_stream:
        print(f"Chunk received: {chunk}")
except Exception as e:
    print(f"Error calling stream_query: {e}")

print("\n2. Sending continuation prompt...")
continuation_prompt = "Yes, please."
print(f"User: {continuation_prompt}")
try:
    response_stream_2 = remote_app.stream_query(message=continuation_prompt, user_id=user_id, session_id=session_id)
    for chunk in response_stream_2:
        print(f"Chunk received: {chunk}")
except Exception as e:
    print(f"Error calling stream_query: {e}")

print("\nTest completed.")
