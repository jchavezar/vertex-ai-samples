import os
import sys
import json
from dotenv import load_dotenv
import vertexai
from vertexai.preview import reasoning_engines as agent_engines

# Load environment variables
# Resolve .env path relative to this script
env_path = os.path.join(os.path.dirname(__file__), "../.env")
if os.path.exists(env_path):
    print(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")
    
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

if not PROJECT_ID:
    print("Error: PROJECT_ID not set in .env")
    sys.exit(1)

print(f"Initializing Vertex AI with Project: {PROJECT_ID}, Location: {LOCATION}")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
    api_transport="grpc"
)

# Use the previous streaming deployment ID
ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/9214561650181406720"

print(f"Connecting to Agent Engine (gRPC): {ENGINE_ID}")
remote_agent = agent_engines.ReasoningEngine(ENGINE_ID)

# Create a mock Gemini Enterprise payload
mock_request_json = json.dumps({
    "contents": [{"role": "user", "parts": [{"text": "Hello Gemini Enterprise"}]}],
    "systemInstruction": {"role": "system", "parts": [{"text": "You are a helpful assistant."}]},
    "tools": []
})

print("Sending payload via streaming_agent_run_with_events() [Streaming]...")
try:
    response_stream = remote_agent.streaming_agent_run_with_events(request_json=mock_request_json)
    
    for event in response_stream:
        print("\n--- Event Received ---")
        print(event)
        
    print("\nStream completed successfully!")
except Exception as e:
    print(f"\nError communicating with agent: {e}")
