import asyncio
from src.news_agent import create_specific_news_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

async def test_sub_agent():
    ticker = "NVDA"
    agent = create_specific_news_agent(ticker)
    
    session_service = InMemorySessionService()
    sid = "test_sub"
    await session_service.create_session(session_id=sid, user_id="user", app_name="test")
    
    runner = Runner(app_name="test", agent=agent, session_service=session_service)
    
    print(f"Running {agent.name}...")
    msg = types.Content(role="user", parts=[types.Part(text=f"Find news for {ticker}")])
    
    async for event in runner.run_async(user_id="user", session_id=sid, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: print(f"TEXT: {part.text[:50]}...")
                
    # Access state directly through the sessions dict if get_session fails
    try:
        session = session_service.sessions[sid]
        print(f"\nFinal State Keys: {list(session.state.keys())}")
        print(f"Value for specific_news: {session.state.get('specific_news')}")
    except Exception as e:
        print(f"Error accessing session: {e}")

if __name__ == "__main__":
    asyncio.run(test_sub_agent())
