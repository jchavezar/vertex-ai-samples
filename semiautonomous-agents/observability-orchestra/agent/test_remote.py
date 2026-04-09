"""
Test the deployed Observability Orchestra agent on Agent Engine.

Usage:
    python test_remote.py
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

import vertexai
from vertexai import agent_engines

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID", "5346318665211969536")

# Test queries
TEST_QUERIES = [
    # Should route to Claude (analytical)
    "Explain the difference between synchronous and asynchronous programming.",
    # Should route to Flash-Lite (creative)
    "Brainstorm 3 names for a cloud monitoring startup.",
]

print(f"""
========================================
Remote Agent Testing
========================================
Project:  {PROJECT_ID}
Location: {LOCATION}
Agent ID: {AGENT_ENGINE_ID}
========================================
""")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Get remote agent
agent = agent_engines.get(AGENT_ENGINE_ID)
print(f"Connected to agent: {agent}")

# Create session
session = agent.create_session(user_id="test-observability")
session_id = session.get("id") if isinstance(session, dict) else session.id
print(f"Session created: {session_id}\n")

for i, query in enumerate(TEST_QUERIES, 1):
    print(f"--- Query {i}/{len(TEST_QUERIES)} ---")
    print(f"User: {query}\n")

    response_text = ""
    for event in agent.stream_query(
        user_id="test-observability",
        session_id=session_id,
        message=query
    ):
        if isinstance(event, dict):
            content = event.get("content", {})
            for part in content.get("parts", []):
                if isinstance(part, dict) and part.get("text"):
                    response_text += part["text"]
        elif hasattr(event, 'content'):
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text

    print(f"Response:\n{response_text[:500]}{'...' if len(response_text) > 500 else ''}\n")
    print("=" * 50 + "\n")

print("Remote testing complete!")
print(f"""
Check observability:
- Cloud Trace: https://console.cloud.google.com/traces/list?project={PROJECT_ID}
- Cloud Logging: https://console.cloud.google.com/logs/query?project={PROJECT_ID}
""")
