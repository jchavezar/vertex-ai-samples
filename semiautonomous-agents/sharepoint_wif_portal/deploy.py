"""
Deploy ADK Agent to Vertex AI Agent Engine.
Internal vs External Insight Comparator

Version: 1.1.0
Date: 2026-04-04
Last Deployed: 2026-04-04 13:17 UTC
"""
import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "")
LOCATION = os.environ.get("LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "")

# Import the agent
from agent import root_agent


def get_env_vars() -> dict:
    """Get environment variables for deployed agent."""
    return {
        "PROJECT_NUMBER": os.environ.get("PROJECT_NUMBER", ""),
        "ENGINE_ID": os.environ.get("ENGINE_ID", ""),
        "DATA_STORE_ID": os.environ.get("DATA_STORE_ID", ""),
        "WIF_POOL_ID": os.environ.get("WIF_POOL_ID", ""),
        "WIF_PROVIDER_ID": os.environ.get("WIF_PROVIDER_ID", ""),
        # AUTH_ID is optional - agent auto-detects from state keys if not set
        "AUTH_ID": os.environ.get("AUTH_ID", ""),
    }


def deploy():
    """Deploy agent to Agent Engine."""
    if not PROJECT_ID:
        print("ERROR: PROJECT_ID not set in .env")
        sys.exit(1)
    if not STAGING_BUCKET:
        print("ERROR: STAGING_BUCKET not set in .env")
        sys.exit(1)

    print(f"""
=====================================
Deploying Insight Comparator Agent
=====================================
Project:  {PROJECT_ID}
Location: {LOCATION}
Staging:  {STAGING_BUCKET}
=====================================
""")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    env_vars = get_env_vars()
    print(f"Environment variables: {list(env_vars.keys())}")

    # Wrap agent in AdkApp
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=env_vars,
    )

    # Deploy to Agent Engine
    print("Creating Agent Engine deployment...")

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "google-cloud-discoveryengine",
            "requests",
            "python-dotenv",
            "httpx",
        ],
        extra_packages=["agent"],  # The agent subdirectory
    )

    print(f"""
=====================================
Deployment Complete!
=====================================
Resource Name: {remote_app.resource_name}
=====================================

Next steps:
1. Add to .env:
   REASONING_ENGINE_RES="{remote_app.resource_name}"

2. Register Authorization (if not done):
   ./register_auth.sh

3. Register Agent to Agentspace:
   ./register_agent.sh

4. Test locally:
   python test_agent.py
""")

    return remote_app


def update(resource_name: str):
    """Update existing Agent Engine deployment."""
    print(f"Updating: {resource_name}")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    env_vars = get_env_vars()

    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=env_vars,
    )

    remote_app = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "google-cloud-discoveryengine",
            "requests",
            "python-dotenv",
            "httpx",
        ],
        extra_packages=["agent"],  # The agent subdirectory
    )

    print(f"Updated: {remote_app.resource_name}")
    return remote_app


if __name__ == "__main__":
    existing_engine = os.environ.get("REASONING_ENGINE_RES", "")

    if len(sys.argv) > 1 and sys.argv[1] == "update":
        resource_name = sys.argv[2] if len(sys.argv) > 2 else existing_engine
        if not resource_name:
            print("Usage: python deploy.py update [resource_name]")
            print("       Or set REASONING_ENGINE_RES in .env")
            sys.exit(1)
        update(resource_name)
    elif len(sys.argv) > 1 and sys.argv[1] == "new":
        deploy()
    elif existing_engine:
        print(f"Found existing engine: {existing_engine}")
        print("Use 'python deploy.py new' to create new engine")
        update(existing_engine)
    else:
        deploy()
