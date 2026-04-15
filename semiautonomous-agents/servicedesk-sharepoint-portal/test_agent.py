#!/usr/bin/env python3
"""
Quick test script for the deployed Router Agent.
Usage: uv run python test_agent.py "your message here"
"""
import os
import sys
import vertexai

PROJECT_ID = "deloitte-plantas"
LOCATION = "us-central1"
AGENT_ID = "7037824945568612352"

def main():
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello, what can you help me with?"

    print(f"Querying agent: {message}")
    print("-" * 50)

    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client()

    agent = client.agent_engines.get(
        name=f"projects/{os.environ['PROJECT_NUMBER']}/locations/{LOCATION}/reasoningEngines/{AGENT_ID}"
    )

    for chunk in agent.stream_query(user_id="cli-test", message=message):
        if isinstance(chunk, dict):
            text = chunk.get('content', {}).get('parts', [{}])[0].get('text', '')
            if text:
                print(text, end='', flush=True)

    print()
    print("-" * 50)

if __name__ == "__main__":
    main()
