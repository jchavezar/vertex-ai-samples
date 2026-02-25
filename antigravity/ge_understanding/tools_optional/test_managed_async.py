import asyncio
import vertexai
import vertexai.agent_engines

# Initialize
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/1859646897011032064"

async def test_managed_async():
    print(f"Loading engine: {ENGINE_ID}")
    app = vertexai.agent_engines.get(ENGINE_ID)
    print(f"App type: {type(app)}")
    
    print("\nCalling async_stream_query...")
    try:
        # Pass the message as 'request_json' if you want to mimic the GE pattern,
        # OR just as 'message'.
        async for event in app.async_stream_query(
            message="Who are you and what is my context?",
            user_id="test-user-async",
            session_id="session-async-456"
        ):
            print(f"EVENT: {event}")
    except Exception as e:
        print(f"Error in async_stream_query: {e}")

if __name__ == "__main__":
    asyncio.run(test_managed_async())
