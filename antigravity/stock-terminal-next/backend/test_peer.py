import asyncio
from src.news_agent import create_peer_news_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

async def test_peer():
    ticker = "NVDA"
    agent = create_peer_news_agent(ticker)
    
    svc = InMemorySessionService()
    sid = "test_peer"
    await svc.create_session(session_id=sid, user_id="user", app_name="test")
    
    runner = Runner(app_name="test", agent=agent, session_service=svc)
    
    print(f"Running {agent.name}...")
    msg = types.Content(role="user", parts=[types.Part(text=f"Find news for {ticker}")])
    
    try:
        async for _ in runner.run_async(user_id="user", session_id=sid, new_message=msg):
            pass
        session = await svc.get_session(app_name="test", user_id="user", session_id=sid)
        print(f"State Keys: {list(session.state.keys())}")
        print(f"Value: {session.state.get('peer_news')}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_peer())
