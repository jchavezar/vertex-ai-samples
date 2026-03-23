import vertexai
import os
from dotenv import load_dotenv
import asyncio

load_dotenv(override=True)
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")
client = vertexai.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="us-central1")

ENGINE_ID = "projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/3149353695427166208"
print(f"Loading engine: {ENGINE_ID}")
remote_app = client.agent_engines.get(name=ENGINE_ID)

async def test():
    print("\n3. Testing remote_app.stream_query():")
    try:
        if hasattr(remote_app, "stream_query") or True: # Force call if attr check hides it
            for event in remote_app.stream_query(message="What is the temperature in Seattle? Respond STRICTLY with SEARCH.", user_id="test_user_123"):
                print("Event stream_query:", event)
        else:
            print("remote_app missing stream_query")
    except Exception as e3:
        print("stream_query Error:", str(e3))

    print("\n2. Testing remote_app.run_async():")
    try:
        if hasattr(remote_app, "run_async"):
            async for event in remote_app.run_async("SEARCH"):
                print("Event run_async:", event)
        else:
             print("remote_app missing run_async")
    except Exception as e2:
         print("run_async Error:", str(e2))

    print("\n3. Testing AdkApp.async_stream_query directly if wrapping needed:")
    # Wait, let's keep it simple at first.
    pass

asyncio.run(test())
