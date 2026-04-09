"""
Test the deployed agent on Agent Engine (sharepoint-wif-agent project).

Usage:
    uv run python test_remote.py
"""
import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("DEPLOY_PROJECT_ID", "sharepoint-wif-agent")
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")


def test():
    if not REASONING_ENGINE_RES:
        print("ERROR: REASONING_ENGINE_RES not set. Run deploy.py first.")
        return

    print(f"Connecting to: {REASONING_ENGINE_RES}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    remote_agent = agent_engines.get(REASONING_ENGINE_RES)
    session = remote_agent.create_session(user_id="test-user")

    test_queries = [
        "What is Vertex AI?",
        "Give me a short summary of what Agent Engine does",
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print("=" * 50)

        for event in remote_agent.stream_query(
            user_id="test-user",
            session_id=session.id,
            message=query,
        ):
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        print(part["text"], end="", flush=True)
        print()


if __name__ == "__main__":
    test()
