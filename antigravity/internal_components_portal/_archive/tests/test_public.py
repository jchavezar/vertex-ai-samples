from public_agent import get_public_agent
import asyncio
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

async def test_search():
    agent = get_public_agent()
    import auth_context
    auth_context.set_user_token("mock_token")
    
    session_service = InMemorySessionService()
    user_id = "test_user"
    session_id = str(uuid.uuid4())
    app_name = "test_app"
    
    # Create the session first
    await session_service.create_session(
        user_id=user_id,
        session_id=session_id,
        app_name=app_name
    )
    
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=app_name
    )
    
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="what is the salary for a CFO Chief Financial Officer 2025")]
    )
    
    print("\n--- STARTING SEARCH ---")
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        print(f"Event: {event}")
        
    # Get the final response from session history
    session = await session_service.get_session(user_id, session_id)
    print("\n--- FINAL RESPONSE ---")
    if session.events:
        print(session.events[-1].content)

if __name__ == "__main__":
    asyncio.run(test_search())
