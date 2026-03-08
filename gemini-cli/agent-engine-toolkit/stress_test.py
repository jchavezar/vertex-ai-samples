import asyncio
import os
import time
import vertexai
import json
from datetime import datetime

# --- CONFIGURATION ---
PROJECT = "vtxdemos"
LOCATION = "us-central1"
AGENT_ENGINE_NAME = "root_agent_test"
NUM_CONCURRENT_REQUESTS = 80
LOG_FILE = "logs.txt"

async def send_query(app, query_index):
    """Sends a single query, returns metrics and logs result."""
    start_time = time.time()
    user_id = f"stress-user-{query_index}"
    query_text = f"Stress test query #{query_index}: What is the speed of light in a vacuum? Reply in one sentence."
    
    try:
        # Create Session
        session = await app.async_create_session(user_id=user_id)
        session_id = session["id"] if isinstance(session, dict) and "id" in session else session.id
        
        # Stream Query
        response_text = ""
        async for event in app.async_stream_query(
            user_id=user_id,
            session_id=session_id,
            message=query_text
        ):
            if hasattr(event, 'text'): response_text += event.text
            elif isinstance(event, dict) and 'text' in event: response_text += event['text']
        
        latency = time.time() - start_time
        return {
            "index": query_index,
            "success": True,
            "latency": latency,
            "query": query_text,
            "response": response_text.strip()
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "index": query_index,
            "success": False,
            "latency": latency,
            "query": query_text,
            "error": str(e)
        }

async def run_detailed_test():
    vertexai.init(project=PROJECT, location=LOCATION)
    client = vertexai.Client(project=PROJECT, location=LOCATION)
    
    found = next((e for e in client.agent_engines.list() if e.api_resource.display_name == AGENT_ENGINE_NAME), None)
    if not found: return print(f"Error: {AGENT_ENGINE_NAME} not found.")
    app = client.agent_engines.get(name=found.api_resource.name)

    print(f"🔥 Launching Stress Test: {NUM_CONCURRENT_REQUESTS} requests...")
    results = await asyncio.gather(*[send_query(app, i) for i in range(NUM_CONCURRENT_REQUESTS)])
    
    # Save Logs
    with open(LOG_FILE, "w") as f:
        f.write(f"STRESS TEST LOGS - {datetime.now()}\n")
        f.write("="*80 + "\n")
        for r in results:
            f.write(f"Query #{r['index']} | Success: {r['success']} | Latency: {r['latency']:.2f}s\n")
            f.write(f"Q: {r['query']}\n")
            if r['success']: f.write(f"A: {r['response']}\n")
            else: f.write(f"ERROR: {r['error']}\n")
            f.write("-" * 40 + "\n")

    # Metrics
    successes = [r for r in results if r['success']]
    latencies = [r['latency'] for r in successes]
    
    final_metrics = {
        "total_requests": NUM_CONCURRENT_REQUESTS,
        "success_count": len(successes),
        "failure_count": len(results) - len(successes),
        "avg_latency": sum(latencies)/len(latencies) if latencies else 0,
        "min_latency": min(latencies) if latencies else 0,
        "max_latency": max(latencies) if latencies else 0,
        "errors": list(set([r['error'] for r in results if not r['success']]))
    }
    
    # Output report to console
    print("\n" + "#"*50)
    print("       🚀 VERTEX AI AGENT ENGINE STRESS REPORT")
    print("#"*50)
    print(f"Engine:         {found.api_resource.name}")
    print(f"Requests:       {final_metrics['total_requests']}")
    print(f"Success Rate:   {(final_metrics['success_count']/final_metrics['total_requests'])*100:.1f}%")
    print(f"Avg Latency:    {final_metrics['avg_latency']:.2f}s")
    print(f"Max Latency:    {final_metrics['max_latency']:.2f}s")
    print(f"Logs Saved to:  {LOG_FILE}")
    print("#"*50)
    
    if final_metrics['failure_count'] > 0:
        print("\n⚠️ QUOTA LIMITATIONS DETECTED:")
        for err in final_metrics['errors']:
            if "429" in err:
                print(f" - [429] Rate Limit Reached: {err[:150]}...")

if __name__ == "__main__":
    asyncio.run(run_detailed_test())
