from public_agent import get_public_agent
from google.adk.agents.runner import Runner
import asyncio

async def test_search():
    agent = get_public_agent()
    # Mock token for test
    import auth_context
    auth_context.set_user_token("mock_token")
    
    runner = Runner(agent=agent)
    events = []
    async for event in runner.run_async("what is the salary for a CFO Chief Financial Officer 2025"):
        events.append(event)
    print("\n--- RESPONSE ---")
    print(events[-1].content)

if __name__ == "__main__":
    asyncio.run(test_search())
