import asyncio
import logging
from src.analyst_copilot import discover_peers_realtime, create_analyst_copilot
from google.genai import types
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

async def test_discovery():
    print("Testing discover_peers_realtime('FSLR')...")
    peers = await discover_peers_realtime("FSLR")
    print(f"Result: {peers}")

async def test_agent_decision():
    print("\nTesting Analyst Copilot Agent Decision...")
    agent = create_analyst_copilot()
    svc = InMemorySessionService()
    await svc.create_session("test_session", "system", "analyst_copilot")
    runner = Runner("test", agent, svc)
    
    msg = types.Content(role="user", parts=[types.Part(text="I am trying to get up to speed on the investability of FSLR. Consult the analyst copilot for a macro perspective.")])
    
    print("Running Agent...")
    async for event in runner.run_async("system", "test_session", msg):
        if event.content:
            print(f"Agent Output: {event.content.parts[0].text if event.content.parts else ''}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
    # asyncio.run(test_agent_decision())
