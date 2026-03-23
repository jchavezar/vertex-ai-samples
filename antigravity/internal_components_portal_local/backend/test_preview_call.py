import vertexai
from vertexai.preview import reasoning_engines
import os
from dotenv import load_dotenv
import asyncio

load_dotenv(override=True)
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")

ENGINE_ID = "projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/3149353695427166208"
print(f"Loading ReasoningEngine via preview: {ENGINE_ID}")

try:
    remote_app = reasoning_engines.ReasoningEngine(ENGINE_ID)
    print("Methods on ReasoningEngine object:")
    print([m for m in dir(remote_app) if not m.startswith("_")])
    
    # Testing remote_app.stream instead of query
    print("\nTesting remote_app.stream('Hello'):")
    if hasattr(remote_app, "stream"):
        for event in remote_app.stream(input="What is the temperature in Seattle? Respond STRICTLY with SEARCH."):
            print("Event stream:", event)
    else:
        print("remote_app missing stream method")

except Exception as e:
    print("Error:", str(e))
