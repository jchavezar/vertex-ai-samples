"""Deploy the ADK agent to Vertex AI Agent Runtime.

Mirrors what the upstream demo's deploy_agent.py does, minus the
Gemini Enterprise registration. Reads PROJECT_ID / REGION from the env.
"""

from __future__ import annotations

import os
import sys

from vertexai import agent_engines, init as vertexai_init
from vertexai.preview.reasoning_engines import AdkApp

from agent import root_agent

PROJECT  = os.environ.get("PROJECT_ID") or sys.exit("export PROJECT_ID first")
REGION   = os.environ.get("REGION", "us-central1")
BUCKET   = os.environ.get("STAGING_BUCKET", f"gs://{PROJECT}-build-{REGION}")

env_vars = {
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "GOOGLE_CLOUD_LOCATION": REGION,
    "MODEL_NAME":             os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite"),
    "MCP_REGISTRY_PROJECT":   PROJECT,
    "MCP_REGISTRY_LOCATION":  REGION,
}


def main() -> None:
    vertexai_init(project=PROJECT, location=REGION, staging_bucket=BUCKET)

    app = AdkApp(agent=root_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-adk>=0.4",
            "google-cloud-aiplatform[agent_engines]",
            "httpx",
        ],
        extra_packages=["agent.py"],
        display_name="legacy-dms-assistant",
        description="ADK agent that calls MCP tools via Agent Gateway.",
        env_vars=env_vars,
    )

    print()
    print("resource_name =", remote.resource_name)
    print()
    print("Set this in your shell before step 17 of the README:")
    print(f"  export REASONING_ENGINE_NAME='{remote.resource_name}'")
    print(f"  export AGENT_ID='{remote.resource_name.split('/')[-1]}'")


if __name__ == "__main__":
    main()
