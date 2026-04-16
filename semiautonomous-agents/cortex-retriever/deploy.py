"""
Deploy Cortex Retriever to Vertex AI Agent Engine.

Usage:
    uv run python deploy.py          # Deploy new (or update if REASONING_ENGINE_RES set)
    uv run python deploy.py new      # Force new deployment
    uv run python deploy.py update   # Update existing
"""
import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID", "")
LOCATION = os.environ.get("LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "")

from agent import root_agent


def get_env_vars() -> dict:
    return {
        "PROJECT_NUMBER": os.environ.get("PROJECT_NUMBER", ""),
        "ENGINE_ID": os.environ.get("ENGINE_ID", ""),
        "DATA_STORE_ID": os.environ.get("DATA_STORE_ID", ""),
        "WIF_POOL_ID": os.environ.get("WIF_POOL_ID", ""),
        "WIF_PROVIDER_ID": os.environ.get("WIF_PROVIDER_ID", ""),
        "AUTH_ID": os.environ.get("AUTH_ID", ""),
    }


REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "google-cloud-discoveryengine",
    "requests",
    "python-dotenv",
]


def deploy():
    if not PROJECT_ID or not STAGING_BUCKET:
        print("ERROR: PROJECT_ID and STAGING_BUCKET must be set in .env")
        sys.exit(1)

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    print(f"Deploying to {PROJECT_ID} / {LOCATION}...")

    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=get_env_vars(),
    )

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
    )

    print(f"""
Deployed successfully.
REASONING_ENGINE_RES={remote_app.resource_name}

Next steps:
  1. Add to .env: REASONING_ENGINE_RES="{remote_app.resource_name}"
  2. Register:    uv run python register.py all
""")
    return remote_app


def update(resource_name: str):
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    print(f"Updating {resource_name}...")

    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=get_env_vars(),
    )

    remote_app = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
    )

    print(f"Updated: {remote_app.resource_name}")
    return remote_app


if __name__ == "__main__":
    existing = os.environ.get("REASONING_ENGINE_RES", "")

    if len(sys.argv) > 1 and sys.argv[1] == "new":
        deploy()
    elif len(sys.argv) > 1 and sys.argv[1] == "update":
        name = sys.argv[2] if len(sys.argv) > 2 else existing
        if not name:
            print("Usage: python deploy.py update [resource_name]")
            sys.exit(1)
        update(name)
    elif existing:
        update(existing)
    else:
        deploy()
