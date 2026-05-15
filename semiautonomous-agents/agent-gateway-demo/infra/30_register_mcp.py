"""Register the Cloud Run MCP server in the Agent Registry.

Uses agentregistry.googleapis.com/v1alpha/.../services (the SOLE write path,
per the discovery doc + memory note `agent_registry_api.md`). The published
gcloud surface for this is unreliable, so we POST directly.

Idempotent: if a service with the same display_name already exists in the
registry, we re-use it instead of creating a duplicate.
"""
from __future__ import annotations

import os
import sys

import google.auth
import google.auth.transport.requests
import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
DISPLAY_NAME = os.environ.get("MCP_SERVICE_DISPLAY_NAME", "sharepoint-mcp")
MCP_SERVER_URL = os.environ["MCP_SERVER_URL"].rstrip("/")
# .env may already have /mcp suffix; strip it so we always end up with exactly one.
if MCP_SERVER_URL.endswith("/mcp"):
    MCP_SERVER_URL = MCP_SERVER_URL[:-4]

PROJECT_NUMBER = os.environ.get("GOOGLE_CLOUD_PROJECT_NUMBER")
if not PROJECT_NUMBER:
    import subprocess

    PROJECT_NUMBER = subprocess.check_output(
        ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
        text=True,
    ).strip()

PARENT = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
BASE = f"https://agentregistry.googleapis.com/v1alpha/{PARENT}"


def _headers() -> dict[str, str]:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID,
    }


def find_existing() -> str | None:
    """List services in the registry; return the resource name of the one
    whose display_name matches, or None."""
    resp = requests.get(f"{BASE}/services", headers=_headers(), timeout=30)
    if resp.status_code != 200:
        print(f"[warn] list services -> {resp.status_code}: {resp.text[:200]}")
        return None
    for svc in resp.json().get("services", []) or []:
        if svc.get("displayName") == DISPLAY_NAME:
            return svc.get("name")
    return None


def create_service() -> str:
    body = {
        "displayName": DISPLAY_NAME,
        # Verified via discovery doc: McpServerSpec.type ∈
        # {NO_SPEC, TOOL_SPEC}; for NO_SPEC the `content` field must be empty.
        "mcpServerSpec": {"type": "NO_SPEC"},
        # Interface.protocolBinding ∈ {JSONRPC, GRPC, HTTP_JSON} — streamable
        # HTTP MCP uses JSON-RPC over HTTP, so JSONRPC is the right value.
        "interfaces": [
            {"protocolBinding": "JSONRPC", "url": MCP_SERVER_URL}
        ],
    }
    resp = requests.post(
        f"{BASE}/services",
        headers=_headers(),
        json=body,
        params={"serviceId": DISPLAY_NAME},
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        sys.exit(f"[error] create service -> {resp.status_code}: {resp.text}")
    op = resp.json()
    op_name = op.get("name", "")
    print(f"[register] create operation: {op_name}")
    # Poll the LRO; the response.name is the real Service resource.
    if not op.get("done"):
        import time
        for i in range(30):
            time.sleep(2)
            r = requests.get(f"https://agentregistry.googleapis.com/v1alpha/{op_name}", headers=_headers(), timeout=30)
            data = r.json()
            if data.get("done"):
                op = data
                break
    if op.get("error"):
        sys.exit(f"[error] op failed: {op['error']}")
    return op.get("response", {}).get("name") or op_name


def main() -> None:
    print(f"[register] parent={PARENT} display_name={DISPLAY_NAME} url={MCP_SERVER_URL}/mcp")
    existing = find_existing()
    if existing:
        print(f"[register] already registered: {existing}")
        resource = existing
    else:
        resource = create_service()
    print()
    print(f"[register] DONE — MCP_SERVICE_RESOURCE={resource}")
    print(f"[register] add to .env: MCP_SERVICE_RESOURCE={resource}")


if __name__ == "__main__":
    main()
