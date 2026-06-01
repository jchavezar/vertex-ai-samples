"""
Deploy adk-drive-ae to Vertex AI Agent Engine.

Usage:
    cd vertex-ai-samples/semiautonomous-agents/adk-drive-ae
    cp .env.example .env       # edit GOOGLE_CLOUD_PROJECT / DEPLOY_STAGING_BUCKET
    uv run python scripts/deploy.py            # create new (or update if AGENT_ENGINE_RESOURCE set)
    uv run python scripts/deploy.py new        # force a new deployment
    uv run python scripts/deploy.py update     # update the engine in AGENT_ENGINE_RESOURCE

After a successful create, paste the printed resource_name into .env as
AGENT_ENGINE_RESOURCE so the backend and future updates can find it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `agent/` importable when running this script from anywhere.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import vertexai  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from vertexai import agent_engines  # noqa: E402
from vertexai.preview import reasoning_engines  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env", override=True)

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
# Agent Engine itself is regional — us-central1. The model location (global) is
# carried via env vars set on the deployed app, not the deploy region.
DEPLOY_LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", f"gs://{PROJECT}-agent-engine")
DISPLAY_NAME = "adk-drive-ae"

# Pin the model location for the deployed runtime — gemini-3-flash-preview
# only serves from `global`. The app must export this env var at runtime
# regardless of what the deploy script's shell has set.
RUNTIME_ENV = {
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "GOOGLE_CLOUD_LOCATION": "global",
    # GOOGLE_CLOUD_PROJECT is reserved by Agent Engine — it sets it automatically.
}

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.88.0",
    "google-adk>=1.0.0",
    "google-genai>=1.0.0",
    "httpx>=0.27.0",
]


def _build_app():
    # Imported here so vertexai.init() runs first (sets ADC region).
    from agent import root_agent

    return reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)


def deploy_new():
    print(f"[deploy] project={PROJECT} location={DEPLOY_LOCATION} staging={STAGING_BUCKET}")
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
