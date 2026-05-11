"""Deploy docgen-agent to Vertex AI Agent Engine (Agent Runtime).

Usage:
    cd semiautonomous-agents/docgen-agent
    cp .env.example .env       # edit values
    uv run python deploy.py            # create new (or update if AGENT_ENGINE_RESOURCE set)
    uv run python deploy.py new        # force fresh deployment
    uv run python deploy.py update     # update the engine in AGENT_ENGINE_RESOURCE

After a successful create, paste the printed `resource_name` into .env as
AGENT_ENGINE_RESOURCE so future updates and `register.py` can find it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import vertexai  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from vertexai import agent_engines  # noqa: E402
from vertexai.preview import reasoning_engines  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
DEPLOY_LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", "gs://vtxdemos-staging")
DISPLAY_NAME = os.environ.get("AGENT_ENGINE_DISPLAY_NAME", "docgen-agent")

# Pinned at deploy time so the runtime always knows where to call Gemini.
# GOOGLE_CLOUD_PROJECT is reserved by Agent Engine — do NOT set it here.
RUNTIME_ENV = {
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "GOOGLE_CLOUD_LOCATION": os.environ.get("RUNTIME_GENAI_LOCATION", "global"),
    "DOCGEN_AGENT_MODEL": os.environ.get("DOCGEN_AGENT_MODEL", "gemini-2.5-flash"),
}

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.88.0",
    "google-adk>=1.0.0",
    "google-genai>=1.0.0",
    "reportlab>=4.0",
]


def _build_app():
    from agent import root_agent  # local import: vertexai.init() must run first

    return reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)


def deploy_new():
    print(f"[deploy] project={PROJECT} region={DEPLOY_LOCATION} staging={STAGING_BUCKET}")
    print(f"[deploy] runtime env: {RUNTIME_ENV}")
    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION, staging_bucket=STAGING_BUCKET)
    app = _build_app()
    remote = agent_engines.create(
        agent_engine=app,
        display_name=DISPLAY_NAME,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
        env_vars=RUNTIME_ENV,
    )
    print("\n[deploy] DONE")
    print(f"[deploy] resource_name = {remote.resource_name}")
    print("\nAdd to .env:")
    print(f'AGENT_ENGINE_RESOURCE="{remote.resource_name}"')
    return remote


def deploy_update(resource_name: str):
    print(f"[deploy] UPDATE {resource_name}")
    print(f"[deploy] runtime env: {RUNTIME_ENV}")
    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION, staging_bucket=STAGING_BUCKET)
    app = _build_app()
    remote = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
        env_vars=RUNTIME_ENV,
    )
    print(f"[deploy] UPDATED {remote.resource_name}")
    return remote


def main():
    existing = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "new":
        deploy_new()
    elif arg == "update":
        target = sys.argv[2] if len(sys.argv) > 2 else existing
        if not target:
            print("Usage: deploy.py update <resource_name>  (or set AGENT_ENGINE_RESOURCE)")
            sys.exit(1)
        deploy_update(target)
    else:
        if existing:
            print(f"[deploy] AGENT_ENGINE_RESOURCE is set -> updating {existing}")
            print("        (run `deploy.py new` to force a fresh deployment)")
            deploy_update(existing)
        else:
            deploy_new()


if __name__ == "__main__":
    main()
