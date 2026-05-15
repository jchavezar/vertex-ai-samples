"""Deploy The Paperclip Detective to Vertex AI Agent Engine."""
import os
import sys

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

load_dotenv()

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ.get("LOCATION", "us-central1")
STAGING_BUCKET = os.environ["STAGING_BUCKET"]

from agent import root_agent  # noqa: E402

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "python-dotenv",
]


def deploy() -> str:
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    print(f"Deploying to {PROJECT_ID} / {LOCATION}…")
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    remote = agent_engines.create(
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
    )
    print(f"REASONING_ENGINE_RES={remote.resource_name}")
    return remote.resource_name


def update(resource_name: str) -> str:
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    print(f"Updating {resource_name}…")
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    remote = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
    )
    print(f"Updated: {remote.resource_name}")
    return remote.resource_name


if __name__ == "__main__":
    existing = os.environ.get("REASONING_ENGINE_RES", "")
    if len(sys.argv) > 1 and sys.argv[1] == "new":
        deploy()
    elif existing:
        update(existing)
    else:
        deploy()
