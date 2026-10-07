#!/usr/bin/env python3
"""Google Cloud Agent Registry & Agent Gateway Registration Script for LexGraph Legal AI Platform.

Registers the Cloud Run MCP Server (`mike-gcp-platform` / `mike-legal-mcp`) in:
1. Google Cloud Agent Registry (`agentregistry.googleapis.com/v1alpha/projects/254356041555/locations/us-central1/services`)
2. Verifies Google Cloud Agent Gateway (`networkservices.googleapis.com/v1beta1/.../agentGateways/my-agent-gateway`)
3. Documents Google Cloud Agent Identity (`spiffe://254356041555.global.id.goog/ns/us-central1/sa/agent-lexgraph-root-orchestrator`)
   and IAP Egressor (`roles/iap.egressor` with CEL `mcp.resourceName`).
"""

import json
import os
import time
import google.auth
import google.auth.transport.requests
import requests

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
PROJECT_NUMBER = "254356041555"
LOCATION = "us-central1"
SERVICE_ID = "mike-legal-mcp"
CLOUD_RUN_BASE_URL = os.environ.get(
    "CLOUD_RUN_BASE_URL",
    "https://mike-gcp-platform-254356041555.us-central1.run.app",
).rstrip("/")
if CLOUD_RUN_BASE_URL.endswith("/mcp"):
    CLOUD_RUN_BASE_URL = CLOUD_RUN_BASE_URL[:-4]


def get_access_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not creds.valid:
        creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID,
    }


def register_in_agent_registry() -> dict:
    base_url = f"https://agentregistry.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/services"
    # Check existing services first
    list_resp = requests.get(base_url, headers=_headers(), timeout=30)
    if list_resp.status_code == 200:
        for svc in list_resp.json().get("services", []) or []:
            if svc.get("displayName") == SERVICE_ID or svc.get("name", "").endswith(f"/{SERVICE_ID}"):
                return {
                    "status": "ALREADY_REGISTERED",
                    "service_id": SERVICE_ID,
                    "service": svc,
                }

    payload = {
        "displayName": SERVICE_ID,
        "mcpServerSpec": {"type": "NO_SPEC"},
        "interfaces": [
            {"protocolBinding": "JSONRPC", "url": CLOUD_RUN_BASE_URL}
        ],
    }

    resp = requests.post(
        base_url,
        headers=_headers(),
        params={"serviceId": SERVICE_ID},
        json=payload,
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return {"status": f"HTTP_{resp.status_code}", "body": resp.text[:400]}

    op = resp.json()
    op_name = op.get("name", "")
    if not op.get("done") and op_name:
        for _ in range(20):
            time.sleep(2)
            r = requests.get(f"https://agentregistry.googleapis.com/v1alpha/{op_name}", headers=_headers(), timeout=30)
            data = r.json()
            if data.get("done"):
                op = data
                break
    return {
        "status": "REGISTERED",
        "service_id": SERVICE_ID,
        "operation": op,
    }


def verify_agent_gateway() -> dict:
    gw_url = f"https://networkservices.googleapis.com/v1beta1/projects/{PROJECT_NUMBER}/locations/{LOCATION}/agentGateways"
    resp = requests.get(gw_url, headers=_headers(), timeout=20)
    if resp.status_code == 200:
        gateways = resp.json().get("agentGateways", [])
        return {
            "status": "OK",
            "count": len(gateways),
            "gateways": [
                {
                    "name": g.get("name"),
                    "governedAccessPath": g.get("googleManaged", {}).get("governedAccessPath"),
                    "protocols": g.get("protocols"),
                    "registries": g.get("registries"),
                }
                for g in gateways
            ],
        }
    return {"status": f"HTTP_{resp.status_code}", "body": resp.text[:300]}


if __name__ == "__main__":
    print("=== 1. Registering LexGraph Legal MCP Service in Google Cloud Agent Registry ===")
    reg_result = register_in_agent_registry()
    print(json.dumps(reg_result, indent=2))
    print("\n=== 2. Verifying Google Cloud Agent Gateway (networkservices.googleapis.com/v1beta1) ===")
    gw_result = verify_agent_gateway()
    print(json.dumps(gw_result, indent=2))
