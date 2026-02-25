import os
import vertexai
import vertexai.agent_engines
from google.cloud import aiplatform

# Initialize
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/1859646897011032064"

def test_managed_query():
    print(f"Loading engine: {ENGINE_ID}")
    app = vertexai.agent_engines.get(ENGINE_ID)
    print(f"App type: {type(app)}")
    
    print("\nCalling stream_query...")
    try:
        # Note: AdkApp agents in Agent Engine usually expect message, user_id, session_id
        responses = app.stream_query(
            message="Hello, identify yourself and show me the session context.",
            user_id="test-user-local",
            session_id="session-123"
        )
        
        for response in responses:
            print(f"REC: {response}")
    except Exception as e:
        print(f"Error in stream_query: {e}")

if __name__ == "__main__":
    test_managed_query()
