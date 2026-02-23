import os
import json
from dotenv import load_dotenv
import vertexai
from vertexai.preview import reasoning_engines as agent_engines

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Force gRPC transport to avoid REST streaming parsing issues
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
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
