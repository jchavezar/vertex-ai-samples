"""
Deploy ADK Agent to Agent Engine in sharepoint-wif-agent project.

Usage:
    uv run python deploy.py          # Create new or update existing
    uv run python deploy.py new      # Force new deployment
    uv run python deploy.py update   # Update existing (uses REASONING_ENGINE_RES from .env)
"""
import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()

# Deploy to Project A (sharepoint-wif-agent)
PROJECT_ID = os.environ.get("DEPLOY_PROJECT_ID", "sharepoint-wif-agent")
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", f"gs://{PROJECT_ID}-staging")

from agent import root_agent


def deploy():
    """Deploy agent to Agent Engine in sharepoint-wif-agent."""
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
        staging_bucket=STAGING_BUCKET,
    )

    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    remote_app = agent_engines.create(
        agent_engine=app,
        display_name="cross-project-assistant",
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ],
        extra_packages=["agent"],
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

2. Register in Gemini Enterprise (vtxdemos):
   uv run python register_agent.py
""")
    return remote_app


def update(resource_name: str):
    """Update existing Agent Engine deployment."""
    print(f"Updating: {resource_name}")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    remote_app = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ],
        extra_packages=["agent"],
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
        print("Use 'python deploy.py new' to force a new deployment")
        update(existing_engine)
    else:
        deploy()
