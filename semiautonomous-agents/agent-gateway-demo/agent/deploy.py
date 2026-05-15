"""Deploy the agent to Vertex AI Agent Engine.

Two modes (controlled via env `USE_AGENT_IDENTITY`):

  USE_AGENT_IDENTITY=0  (default) — deploy WITHOUT identity_type or
    agent_gateway_config. Used for the early end-to-end test before the
    Agent Gateway resource is provisioned. Token reaches the MCP via the
    `header_provider` in agent.py, which reads it from session state.

  USE_AGENT_IDENTITY=1 — deploy WITH `identity_type=AGENT_IDENTITY` and
    `agent_gateway_config.agent_to_anywhere_config.agent_gateway=...`.
    Use ONLY after `infra/10_create_gateway.sh` has provisioned the
    gateway and `infra/20_create_connector.sh` has created the connector.

Reuses the established `vertexai.Client(...).agent_engines.create(config={...})`
pattern from observability-orchestra/agent/deploy.py.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT.parent / ".env")  # also pick up the top-level .env

from vertexai import Client  # noqa: E402
from vertexai._genai import types as ge_types  # noqa: E402
from vertexai.agent_engines import AdkApp  # noqa: E402

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
DEPLOY_LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", "gs://vtxdemos-staging")
DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "agent-gateway-demo")

USE_AGENT_IDENTITY = os.environ.get("USE_AGENT_IDENTITY", "0") == "1"
GATEWAY_RESOURCE = os.environ.get("GATEWAY_RESOURCE", "")

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.151.0",
    "google-genai>=1.70.0",
    "google-adk>=1.28.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]
if USE_AGENT_IDENTITY:
    # The extra that pulls in `google.adk.integrations.agent_identity`.
    REQUIREMENTS.append("google-adk[agent-identity]")

RUNTIME_ENV = {
    "GOOGLE_GENAI_USE_VERTEXAI": "1",
    "GOOGLE_CLOUD_LOCATION": os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    "AGENT_MODEL": os.environ.get("AGENT_MODEL", "gemini-2.5-flash"),
    "MCP_SERVER_URL": os.environ.get("MCP_SERVER_URL", ""),
    "SESSION_TOKEN_KEY": os.environ.get("SESSION_TOKEN_KEY", "temp:sharepoint_3lo"),
    "USE_AGENT_IDENTITY": "1" if USE_AGENT_IDENTITY else "0",
}
if USE_AGENT_IDENTITY:
    RUNTIME_ENV["CONNECTOR_RESOURCE"] = os.environ.get("CONNECTOR_RESOURCE", "")
    RUNTIME_ENV["CONTINUE_URI"] = os.environ.get("CONTINUE_URI", "")
# IMPORTANT: do NOT inject GOOGLE_CLOUD_PROJECT — Agent Engine reserves it.


def _build_app() -> AdkApp:
    from agent import root_agent  # noqa: WPS433  vertexai env must be set first
    return AdkApp(agent=root_agent, enable_tracing=True)


def _config() -> dict:
    cfg: dict = {
        "display_name": DISPLAY_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": REQUIREMENTS,
        "extra_packages": ["agent.py"],
        "env_vars": RUNTIME_ENV,
    }
    if USE_AGENT_IDENTITY:
        if not GATEWAY_RESOURCE:
            sys.exit("USE_AGENT_IDENTITY=1 but GATEWAY_RESOURCE is empty.")
        cfg["identity_type"] = ge_types.IdentityType.AGENT_IDENTITY
        cfg["agent_gateway_config"] = {
            "agent_to_anywhere_config": {"agent_gateway": GATEWAY_RESOURCE}
        }
        # service_account is intentionally omitted — mutually exclusive.
    return cfg


def _existing(client: Client) -> str | None:
    for e in client.agent_engines.list():
        if e.api_resource.display_name == DISPLAY_NAME:
            return e.api_resource.name
    return None


def main() -> None:
    print(f"[deploy] project={PROJECT_ID} region={DEPLOY_LOCATION}")
    print(f"[deploy] mode={'AGENT_IDENTITY' if USE_AGENT_IDENTITY else 'pre-gateway'}")
    print(f"[deploy] env: {RUNTIME_ENV}")

    client = Client(project=PROJECT_ID, location=DEPLOY_LOCATION)
    cfg = _config()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "new":
        existing = None
    else:
        existing = _existing(client)

    app = _build_app()
    if existing and arg != "new":
        print(f"[deploy] UPDATE {existing}")
        remote = client.agent_engines.update(name=existing, agent=app, config=cfg)
    else:
        print("[deploy] CREATE (no existing engine matched)")
        remote = client.agent_engines.create(agent=app, config=cfg)

    name = remote.api_resource.name
    print(f"\n[deploy] DONE — resource: {name}")
    print(f"[deploy] add to .env: AGENT_ENGINE_RESOURCE={name}")


if __name__ == "__main__":
    main()
