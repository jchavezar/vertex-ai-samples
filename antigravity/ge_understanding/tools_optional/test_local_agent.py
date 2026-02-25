import asyncio
import sys
import os
import asyncio

# Add the directory containing agent_pkg to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_pkg.agent import GEMINIPayloadInterceptor

async def test_logic():
    print("Starting local test...")
    agent = GEMINIPayloadInterceptor()
    
    # Simulate a GE payload
    payload = {
        "user_message": "Search for socks",
        "session_id": "test-session-123"
    }
    
    request_json = str(payload).replace("'", '"')
    
    print(f"Testing with payload: {request_json}")
    
    async for event in agent.streaming_agent_run_with_events(request_json):
        print(f"Received event: {event}")

if __name__ == "__main__":
    asyncio.run(test_logic())



if __name__ == "__main__":
    asyncio.run(test_logic())
