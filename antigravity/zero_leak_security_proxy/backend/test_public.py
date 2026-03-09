from public_agent import get_public_agent
import asyncio
from google.adk.agents.invocation_context import InvocationContext

async def test_search():
    agent = get_public_agent()
    import auth_context
    auth_context.set_user_token("mock_token")
    
    ctx = InvocationContext()
    events = []
    async for event in agent.run_async("what is the salary for a CFO Chief Financial Officer 2025", ctx):
        events.append(event)
        
    print("\n--- RESPONSE ---")
    print(events[-1].content)

if __name__ == "__main__":
    asyncio.run(test_search())
