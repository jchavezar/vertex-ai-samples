from agents.workflow_agent import root_agent
from vertexai.agent_engines import AdkApp
import asyncio

async def main():
    print("Creating local AdkApp...")
    app = AdkApp(agent=root_agent)
    
    print("Testing stream_query locally...")
    user_id = "test_user_666"
    
    # AdkApp requires session creation as well if we're using it programmatically instead of REST
    # Oh wait, AdkApp.stream_query creates an implicit session if we don't provide one, but we can provide user_id and session_id
    session_id = "test_session_123"
    try:
        app.create_session(user_id=user_id, session_id=session_id)
    except Exception as e:
        print(f"create_session error (might be fine if it exists): {e}")

    # Notice we pass message="Tell me a joke" instead of input_text="Tell me a joke"
    # because stream_query takes kwargs and turns them into input parameters OR populates ctx.messages.
    print("Calling stream_query...")
    try:
        response_stream = app.stream_query(message="Tell me a very brief fact about quantum computing.", user_id=user_id, session_id=session_id)
        for event in response_stream:
            print(f"Event: {event}")
            
        print("\nSending continuation prompt...")
        response_stream_2 = app.stream_query(message="Yes, please.", user_id=user_id, session_id=session_id)
        for event in response_stream_2:
            print(f"Event: {event}")
    except Exception as e:
        print(f"Error during stream_query: {e}")

if __name__ == "__main__":
    asyncio.run(main())
