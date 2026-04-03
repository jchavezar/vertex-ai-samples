"""
Deploy ADK Agent to Vertex AI Agent Engine.
"""
import os
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "vtxdemos")
LOCATION = os.environ.get("LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "gs://vtxdemos-staging")

# Import the agent
from agent import root_agent


def deploy():
    """Deploy agent to Agent Engine."""
    print(f"""
=====================================
Deploying ADK Agent to Agent Engine
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

    # Environment variables for the deployed agent
    env_vars = {
        "PROJECT_NUMBER": os.environ.get("PROJECT_NUMBER", ""),
        "ENGINE_ID": os.environ.get("ENGINE_ID", ""),
        "DATA_STORE_ID": os.environ.get("DATA_STORE_ID", ""),
        "WIF_POOL_ID": os.environ.get("WIF_POOL_ID", ""),
        "WIF_PROVIDER_ID": os.environ.get("WIF_PROVIDER_ID", ""),
        "AUTH_ID": os.environ.get("AUTH_ID", "sharepointauth2"),  # Updated default
    }
    print(f"Environment variables: {env_vars}")

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
        ],
        extra_packages=["agent"],  # Include agent package
    )

    print(f"""
=====================================
Deployment Complete!
=====================================
Resource Name: {remote_app.resource_name}
=====================================

Next steps:
1. Register Authorization (if not done):
   ./register_auth.sh

2. Register Agent to Agentspace:
   export REASONING_ENGINE_RES="{remote_app.resource_name}"
   ./register_agent.sh

3. Test the agent:
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

    env_vars = {
        "PROJECT_NUMBER": os.environ.get("PROJECT_NUMBER", ""),
        "ENGINE_ID": os.environ.get("ENGINE_ID", ""),
        "DATA_STORE_ID": os.environ.get("DATA_STORE_ID", ""),
        "WIF_POOL_ID": os.environ.get("WIF_POOL_ID", ""),
        "WIF_PROVIDER_ID": os.environ.get("WIF_PROVIDER_ID", ""),
        "AUTH_ID": os.environ.get("AUTH_ID", "sharepointauth2"),  # Updated default
    }

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
        ],
        extra_packages=["agent"],
    )

    print(f"Updated: {remote_app.resource_name}")
    return remote_app


if __name__ == "__main__":
    import sys

    # Check for existing reasoning engine in .env
    existing_engine = os.environ.get("REASONING_ENGINE_RES", "")

    if len(sys.argv) > 1 and sys.argv[1] == "update":
        resource_name = sys.argv[2] if len(sys.argv) > 2 else existing_engine
        if not resource_name:
            print("Usage: python deploy.py update [resource_name]")
            print("       Or set REASONING_ENGINE_RES in .env")
            sys.exit(1)
        update(resource_name)
    elif len(sys.argv) > 1 and sys.argv[1] == "new":
        # Force new deployment
        deploy()
    elif existing_engine:
        # Auto-update if engine exists
        print(f"Found existing engine in .env: {existing_engine}")
        print("Use 'python deploy.py new' to create a new engine instead")
        update(existing_engine)
    else:
        deploy()
