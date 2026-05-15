#!/usr/bin/env python3
"""Register the Jira MCP server in Agent Registry for governance and reuse.

This is OPTIONAL. The agent works without registry registration. Benefits:
- Agent Gateway can enforce IAP on MCP calls
- Other agents can discover and reuse the MCP server
- Centralized governance of tool access

Prerequisites:
- Cloud Run MCP server deployed
- Agent Registry API enabled
- Owner role on the project

Usage:
    MCP_SERVER_URL=https://jira-mcp-server-254356041555.us-central1.run.app python register_mcp_in_registry.py
"""

import os
import sys
import subprocess
import google.auth
import google.auth.transport.requests
import requests

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
MCP_SERVER_URL = os.environ["MCP_SERVER_URL"].rstrip("/")
DISPLAY_NAME = os.environ.get("MCP_SERVICE_DISPLAY_NAME", "jira-mcp")

# Strip /sse or /mcp suffix if present
if MCP_SERVER_URL.endswith("/sse") or MCP_SERVER_URL.endswith("/mcp"):
    MCP_SERVER_URL = MCP_SERVER_URL.rsplit("/", 1)[0]

# Get project number
PROJECT_NUMBER = os.environ.get("GOOGLE_CLOUD_PROJECT_NUMBER")
if not PROJECT_NUMBER:
    PROJECT_NUMBER = subprocess.check_output(
        ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
        text=True,
    ).strip()

PARENT = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
BASE = f"https://agentregistry.googleapis.com/v1alpha/{PARENT}"


def get_headers():
    """Get auth headers."""
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID,
    }


def find_existing():
    """Check if service already registered."""
    resp = requests.get(f"{BASE}/services", headers=get_headers(), timeout=30)
    if resp.status_code != 200:
        print(f"Warning: list services -> {resp.status_code}")
        return None

    for svc in resp.json().get("services", []) or []:
        if svc.get("displayName") == DISPLAY_NAME:
            return svc.get("name")
    return None


def create_service():
    """Register MCP server in Agent Registry."""
    body = {
        "displayName": DISPLAY_NAME,
        "mcpServerSpec": {"type": "NO_SPEC"},  # No tool spec validation
        "interfaces": [
            {
                "protocolBinding": "JSONRPC",  # MCP uses JSON-RPC over HTTP
                "url": MCP_SERVER_URL
            }
        ],
    }

    resp = requests.post(
        f"{BASE}/services",
        headers=get_headers(),
        json=body,
        params={"serviceId": DISPLAY_NAME},
        timeout=60,
    )

    if resp.status_code not in (200, 201):
        sys.exit(f"Error: create service -> {resp.status_code}: {resp.text}")

    op = resp.json()
    op_name = op.get("name", "")
    print(f"Creating service (LRO): {op_name}")

    # Poll until done
    if not op.get("done"):
        import time
        for i in range(30):
            time.sleep(2)
            r = requests.get(
                f"https://agentregistry.googleapis.com/v1alpha/{op_name}",
                headers=get_headers(),
                timeout=30
            )
            data = r.json()
            if data.get("done"):
                op = data
                break

    if op.get("error"):
        sys.exit(f"Error: operation failed: {op['error']}")

    return op.get("response", {}).get("name") or op_name


def main():
    print(f"Registering Jira MCP server in Agent Registry")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Location: {LOCATION}")
    print(f"  Display name: {DISPLAY_NAME}")
    print(f"  MCP URL: {MCP_SERVER_URL}")
    print()

    existing = find_existing()
    if existing:
        print(f"✓ Already registered: {existing}")
        resource = existing
    else:
        print("Registering new service...")
        resource = create_service()
        print(f"✓ Created: {resource}")

    print()
    print("=" * 60)
    print("REGISTRATION COMPLETE")
    print("=" * 60)
    print()
    print(f"MCP_SERVICE_RESOURCE={resource}")
    print()
    print("Add this to your .env file.")
    print()
    print("Benefits:")
    print("  - Agent Gateway can enforce IAP on tool calls")
    print("  - Other agents can discover this MCP server")
    print("  - Centralized governance")
    print()
    print("Next: Deploy your agent with agent_gateway_config binding.")


if __name__ == "__main__":
    if "MCP_SERVER_URL" not in os.environ:
        sys.exit("Error: MCP_SERVER_URL environment variable required")
    main()
