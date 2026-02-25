import asyncio
import logging
from google.adk.sessions import InMemorySessionService
from agents import DelegationTools

# Configure logging to see what happens
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_delegation")

async def test_delegation():
    print("--- Starting Delegation Test ---")
    session_service = InMemorySessionService()
    
    # Callback to verify completion
    completion_event = asyncio.Event()
    
    def on_complete(task_id, result):
        print(f"Callback received! Task: {task_id}, Result: {result}")
        completion_event.set()

    tools = DelegationTools(session_service, on_complete=on_complete)
    
    # Start background task directly
    msg = await tools.start_background_task("Test heavy task")
    print(f"Main tool returned: {msg}")
    
    # Wait for background completion (timeout 10s)
    print("Waiting for background task...")
    try:
        await asyncio.wait_for(completion_event.wait(), timeout=15.0)
        print("--- Test Passed: Background task completed ---")
    except asyncio.TimeoutError:
        print("--- Test Failed: Timeout waiting for background task ---")

if __name__ == "__main__":
    asyncio.run(test_delegation())
