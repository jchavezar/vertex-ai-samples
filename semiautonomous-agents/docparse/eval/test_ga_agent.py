"""Test the deployed GA agent (simple, no re-ranker)."""
import time
import vertexai
from vertexai import agent_engines

vertexai.init(project="vtxdemos", location="us-central1")
agent = agent_engines.get("projects/254356041555/locations/us-central1/reasoningEngines/8912734163484803072")

test_questions = [
    "What was the total mentions of metaverse-related keywords in 2020 Q1?",
    "What is the sum of total metaverse mentions across all four quarters of 2021?",
    "Which three industries have begun metaverse journeys?",
    "What is the title of the Sales Excellence report?",
    "On page 11, what is the long-deep scenario impact for Devices?",
    "What six categories of providers are profiled on page 23?",
    "Per page 30, what is the percentage premium of Consulting Heritage?",
    "What was the 2024 price movement for India per the page 16 map?",
    "How many SDLC AI Pods does Globant offer per page 21?",
    "What is the source and sample size of Figure 3?",
]

print("Testing deployed GA agent (gemini-2.5-flash, 92.1% composite)...\n")
latencies = []

for i, q in enumerate(test_questions, 1):
    session = agent.create_session(user_id=f"test-{i}")
    sid = session.get('id') if isinstance(session, dict) else session.id
    
    t0 = time.time()
    answer = ""
    for event in agent.stream_query(user_id=f"test-{i}", session_id=sid, message=q):
        c = event.get('content', {}) if isinstance(event, dict) else {}
        for p in c.get('parts', []):
            if isinstance(p, dict) and 'text' in p:
                answer += p['text']
    elapsed = time.time() - t0
    latencies.append(elapsed)
    
    print(f"Q{i}: {elapsed:.1f}s — {answer[:100] if answer else '(no answer)'}...")

avg = sum(latencies) / len(latencies)
print(f"\n{'='*60}")
print(f"Avg latency: {avg:.1f}s (n={len(latencies)})")
print(f"Min: {min(latencies):.1f}s  Max: {max(latencies):.1f}s")
print(f"vs eval measurement: 4.2s (direct SDK, not through Agent Runtime)")
print(f"{'='*60}")
