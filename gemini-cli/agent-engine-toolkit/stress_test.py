import asyncio
import os
import time
from google.genai import Client
from google.adk.events.event import Event

# Configuration
PROJECT = "vtxdemos"
LOCATION = "us-central1"
# Replace this with the actual engine name after deployment
ENGINE_NAME = "projects/254356041555/locations/us-central1/reasoningEngines/4503945973533245440"
NUM_CONCURRENT_REQUESTS = 80

async def send_query(client, session_id, query_index):
    """Sends a single query to a specific session and returns performance metrics."""
    start_time = time.time()
    try:
        # We use a unique session ID for each query to test session creation overhead
        # In Agent Engine, interacting with a reasoning engine via genai client:
        # Note: The exact method for genai.Client() to CALL an agent engine might vary.
        # Usually it's client.models.generate_content or a specialized agent_engines method.
        # Based on documentation, we can use the remote_agent object or the engine name.
        
        # Simulating the call using the reasoning_engines interface or similar
        # For this stress test, we are measuring response time and success/failure.
        
        # Actual call pattern for Agent Engine (Reasoning Engine) via google-genai:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=ENGINE_NAME,
            contents=f"Stress test query {query_index}. Reply with 'OK'.",
            config={"candidate_count": 1}
        )
        
        end_time = time.time()
        return {
            "index": query_index,
            "success": True,
            "latency": end_time - start_time,
            "response": response.text if hasattr(response, 'text') else str(response)
        }
    except Exception as e:
        end_time = time.time()
        return {
            "index": query_index,
            "success": False,
            "latency": end_time - start_time,
            "error": str(e)
        }

async def run_stress_test():
    client = Client(
        vertexai=True,
        project=PROJECT,
        location=LOCATION
    )
    
    print(f"🚀 Starting stress test: {NUM_CONCURRENT_REQUESTS} concurrent queries to {ENGINE_NAME}...")
    
    tasks = []
    for i in range(NUM_CONCURRENT_REQUESTS):
        # Generate a unique session ID for each request
        session_id = f"stress-test-session-{int(time.time())}-{i}"
        tasks.append(send_query(client, session_id, i))
    
    start_total = time.time()
    results = await asyncio.gather(*tasks)
    end_total = time.time()
    
    # Analysis
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    latencies = [r["latency"] for r in results if r["success"]]
    
    print("\n--- Stress Test Report ---")
    print(f"Total Requests: {NUM_CONCURRENT_REQUESTS}")
    print(f"Successes: {len(successes)}")
    print(f"Failures: {len(failures)}")
    print(f"Total Duration: {end_total - start_total:.2f}s")
    
    if latencies:
        print(f"Average Latency (Success): {sum(latencies)/len(latencies):.2f}s")
        print(f"Min Latency: {min(latencies):.2f}s")
        print(f"Max Latency: {max(latencies):.2f}s")
    
    if failures:
        print("\nTop 5 Errors:")
        error_msgs = [f["error"] for f in failures]
        for msg in list(set(error_msgs))[:5]:
            count = error_msgs.count(msg)
            print(f"- [{count}] {msg}")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
