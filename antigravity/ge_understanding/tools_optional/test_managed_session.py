import asyncio
import vertexai
import vertexai.agent_engines

# Initialize
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

ENGINE_ID = "projects/254356041555/locations/us-central1/reasoningEngines/1320059366656704512"

async def test_managed_valid_session():
    print(f"Loading engine: {ENGINE_ID}")
    app = vertexai.agent_engines.get(ENGINE_ID)
    print(f"App type: {type(app)}")
    
    user_id = "test-user-managed"
    print(f"\nCreating session for {user_id}...")
    try:
        session = await app.async_create_session(user_id=user_id)
        session_id = session["id"] if "id" in session else session.id
        print(f"Session created: {session_id}")
        
        print(f"\nCalling async_stream_query with session {session_id}...")
        async for event in app.async_stream_query(
            message="Who are you and what is my context?",
            user_id=user_id,
            session_id=session_id
        ):
            print(f"EVENT: {event}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_managed_valid_session())
