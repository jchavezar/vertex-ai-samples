import os
import vertexai
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    LOCATION = "us-central1"
AGENT_ENGINE_NAME = "dynamic_workflow_orchestrator"

def test_engine():
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    
    # 1. Get the engine by display name
    print(f"Searching for Agent Engine: {AGENT_ENGINE_NAME}...")
    all_engines = list(client.agent_engines.list())
    target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)
    
    if not target_engine:
        print(f"Error: Agent Engine '{AGENT_ENGINE_NAME}' not found.")
        return
    
    print(f"Found engine: {target_engine.api_resource.name}")
    
    print("\nStarting execution...")
    # Because ADK handles interactions as a stream of events usually, we can start it using query
    # The AdkApp maps `.query()` to the agent's logic.
    prompt = "Create a short business report about the potential of AI in finance in the US"
    print(f">> USER prompt: '{prompt}'")
    
    try:
        response = target_engine.query(
            input=prompt
        )
        print("\n=== Agent Engine Response ===")
        print(response)
        print("=============================")
    except Exception as e:
        print(f"\nError interacting with Agent Engine: {e}")

if __name__ == "__main__":
    test_engine()
