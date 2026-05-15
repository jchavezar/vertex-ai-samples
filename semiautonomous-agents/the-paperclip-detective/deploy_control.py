"""Deploy the google/adk-samples academic-research agent UNCHANGED, as a control.

Same code as upstream — `tools=[AgentTool(websearch), AgentTool(newresearch)]`, no
`load_artifacts`. We deploy and register it next to The Paperclip Detective so the
user can attach the same PDF and observe what happens: does the model actually read
the file (which would falsify our verdict), or does it bluff from filename alone
(which would confirm our verdict)?
"""
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

from control_academic_research.agent import root_agent  # noqa: E402

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]",
    "python-dotenv",
]


def deploy() -> str:
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    print(f"Deploying CONTROL (academic-research, unchanged) to {PROJECT_ID} / {LOCATION}…")
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    remote = agent_engines.create(
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["control_academic_research"],
    )
    print(f"CONTROL_REASONING_ENGINE_RES={remote.resource_name}")
    return remote.resource_name


if __name__ == "__main__":
    deploy()
