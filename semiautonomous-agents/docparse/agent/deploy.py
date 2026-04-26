"""Deploy the docparse RAG agent to Vertex AI Agent Engine.

    uv run python deploy.py             # update if REASONING_ENGINE_RES set in env, else create new
    uv run python deploy.py new         # force fresh deployment (mints a new resource id)
    uv run python deploy.py update      # update REASONING_ENGINE_RES (must be set)

Reads .env from the parent docparse/ directory.

Required env vars (typically loaded from .env via dotenv):

    DEPLOY_PROJECT_ID         GCP project that hosts the Agent Engine
    DEPLOY_LOCATION           e.g. "us-central1" (Agent Engine deploy region)
    DEPLOY_STAGING_BUCKET     gs://… for ADK staging tarballs
    RAG_CORPUS_NAME           passed through to agent.py at runtime
    REASONING_ENGINE_RES      (optional) set after first deploy to enable updates

Why the env_vars below matter:

  - GOOGLE_CLOUD_LOCATION=global pins the genai client (used by the ADK
    Gemini wrapper) to the global endpoint where Gemini 3 preview models
    live. Without this, ADK reads the deployment region (us-central1) and
    asks for "gemini-3-flash-preview" there — 404.

  - GOOGLE_GENAI_USE_VERTEXAI=true tells the SDK to use Vertex AI auth
    instead of the public Generative Language API.

  - These env vars do NOT persist across update() calls — they must be
    re-supplied every time. Verify with:
      gcloud ai reasoning-engines describe <id> --region=<region>
"""
import os
import subprocess
import sys
from pathlib import Path

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

# Walk up to docparse/.env (one level above agent/)
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")

PROJECT_ID = os.environ["DEPLOY_PROJECT_ID"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get(
    "DEPLOY_STAGING_BUCKET", f"gs://{PROJECT_ID}-staging-agent-engine"
)

DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "docparse-rag-agent")
DESCRIPTION = (
    "Answers questions over a Vertex AI RAG Engine corpus of docparse-"
    "extracted markdown. Per-page chunks + exhaustive answering prompt."
)

# Env vars passed to the deployed container (NOT the local environment).
RUNTIME_ENV_VARS = {
    # See the doctstring at the top — these two are mandatory for
    # Gemini 3 preview models to be reachable from us-central1 deploys.
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    # Forwarded to agent/agent.py.
    "RAG_CORPUS_NAME": os.environ["RAG_CORPUS_NAME"],
    "AGENT_MODEL": os.environ.get("AGENT_MODEL", "gemini-3-flash-preview"),
    "AGENT_TOP_K": os.environ.get("AGENT_TOP_K", "20"),
}


def _ensure_bucket():
    """Create the staging bucket if it doesn't exist."""
    name = STAGING_BUCKET.replace("gs://", "").rstrip("/")
    r = subprocess.run(
        ["gcloud", "storage", "buckets", "describe", f"gs://{name}",
         "--project", PROJECT_ID],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"Creating staging bucket {name}…")
        subprocess.run(
            ["gcloud", "storage", "buckets", "create", f"gs://{name}",
             "--project", PROJECT_ID, "--location", LOCATION,
             "--uniform-bucket-level-access"],
            check=True,
        )


def _build_app():
    """Wrap root_agent in an ADK app with tracing on."""
    # Imported here so the agent module reads the (now-loaded) env vars.
    from docparse_agent import root_agent
    return reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)


def deploy():
    _ensure_bucket()
    print(f"\n=== Deploying {DISPLAY_NAME} → {PROJECT_ID} / {LOCATION} ===\n")
    vertexai.init(
        project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET,
    )
    remote = agent_engines.create(
        agent_engine=_build_app(),
        display_name=DISPLAY_NAME,
        description=DESCRIPTION,
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["docparse_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )
    print(f"\n=== Deployed ===")
    print(f"resource_name: {remote.resource_name}")
    print(f"\nNext: REASONING_ENGINE_RES={remote.resource_name}")
    print(f"Then: uv run python register_agent.py")
    return remote


def update(resource_name: str):
    _ensure_bucket()
    print(f"\n=== Updating {resource_name} ===\n")
    vertexai.init(
        project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET,
    )
    remote = agent_engines.update(
        resource_name=resource_name,
        agent_engine=_build_app(),
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["docparse_agent"],
        env_vars=RUNTIME_ENV_VARS,  # MUST re-supply on every update
    )
    print(f"updated: {remote.resource_name}")
    return remote


if __name__ == "__main__":
    existing = os.environ.get("REASONING_ENGINE_RES", "")
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "update":
        target = sys.argv[2] if len(sys.argv) > 2 else existing
        if not target:
            sys.exit("Usage: deploy.py update [resource_name] (or set REASONING_ENGINE_RES)")
        update(target)
    elif arg == "new":
        deploy()
    elif existing:
        print(f"Found existing engine: {existing}  (use 'new' to force fresh)")
        update(existing)
    else:
        deploy()
