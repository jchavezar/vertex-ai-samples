"""Register the Custom Firestore RAG MCP Server as a custom MCP data store in Gemini Enterprise.

Uses Google Discovery Engine v1alpha APIs to configure a Custom BYO_MCP server so that Gemini
Enterprise can leverage search_docs to ground PDF results.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import google.auth
import google.auth.transport.requests
import requests

# ---- Load .env from eval or parent directory if present -------------------
_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE / ".env", _HERE.parent / "eval" / ".env", _HERE.parent / ".env"):
    if _candidate.exists():
        for line in _candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "docparse-testing")
COLLECTION_ID = os.environ.get("GE_COLLECTION_ID", "default_collection")
LOCATION = os.environ.get("GE_LOCATION", "global")

DEFAULT_DATASTORE_ID = f"docparse-firestore-mcp-{int(time.time())}"
DATASTORE_ID = os.environ.get("DATASTORE_ID", DEFAULT_DATASTORE_ID)
COLLECTION_DISPLAY_NAME = os.environ.get(
    "COLLECTION_DISPLAY_NAME", "Firestore RAG MCP (Docparse)"
)

# Your deployed Cloud Run service URL
MCP_SERVICE_URL = os.environ.get(
    "MCP_SERVICE_URL",
    "https://docparse-firestore-mcp-254356041555.us-central1.run.app",
).rstrip("/")
INSTANCE_URI = os.environ.get("INSTANCE_URI", f"{MCP_SERVICE_URL}/mcp")


def _gcp_token() -> str:
    """Acquires a Google Cloud access token with Discovery Engine Admin permission."""
    acct = os.environ.get("GCLOUD_ACCOUNT")
    if acct:
        import subprocess
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token", "--account", acct],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token  # type: ignore[return-value]


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_gcp_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base_url() -> str:
    return (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{LOCATION}"
    )


def _data_connector() -> dict:
    return {
        "dataSource": "custom_mcp",
        "params": {"oauth_access_token": "placeholder-not-used-by-byo-mcp"},
        "connectorModes": ["ACTIONS", "FEDERATED"],
        "bapConfig": {"supportedConnectorModes": ["ACTIONS"]},
        "entities": [{"entityName": "mcp_data"}],
        "actionConfig": {
            "isActionConfigured": True,
            "createBapConnection": True,
            "actionParams": {
                "instance_uri": INSTANCE_URI,
                "auth_type": "OIDC",  # Standard OIDC Bearer tokens for Cloud Run
                "mcp_server_source": "BYO_MCP",
                "registry_mcp_server_name": "",
                "mcp_server_description": (
                    "Firestore-backed RAG system for Docparse. Exposes search_docs tool "
                    "which performs vector search over page-level markdown chunks from "
                    "extracted PDFs and returns verified original PDF HTTPS links and page-positions."
                ),
                "mcp_agent_instructions": (
                    "For any question requiring reports or documents, call `search_docs` with the "
                    "user's query verbatim. The tool returns matching text, page numbers, GCS URIs, "
                    "and HTTPS grounding URLs. Always cite the exact page number and use the HTTPS grounding URLs "
                    "to provide high-fidelity citations back to the original PDF."
                ),
            },
        },
    }


def _entity_ds_name(datastore_id: str) -> str:
    return (
        f"projects/{GE_PROJECT_NUMBER}/locations/{LOCATION}/collections/"
        f"{COLLECTION_ID}/dataStores/{datastore_id}_mcp_data"
    )


def _engine_url() -> str:
    return (
        f"{_base_url()}/collections/{COLLECTION_ID}/engines/{GE_ENGINE_ID}"
    )


def _get_engine() -> dict:
    resp = requests.get(_engine_url(), headers=_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def _get_datastore(name: str) -> dict | None:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{name}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def _wait_lro(op_name: str, timeout_s: int = 180) -> dict:
    op_url = f"https://discoveryengine.googleapis.com/v1alpha/{op_name}"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = requests.get(op_url, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            body = resp.json()
            if body.get("done"):
                if "error" in body:
                    raise RuntimeError(f"LRO failed: {body['error']}")
                return body
        elif resp.status_code == 404:
            pass
        time.sleep(5)
    raise TimeoutError(f"LRO {op_name} timed out after {timeout_s}s")


def main():
    print(f"[*] Starting Custom MCP Data Store Registration")
    print(f"    GCP Project ID:     {GE_PROJECT_ID}")
    print(f"    GCP Project Number: {GE_PROJECT_NUMBER}")
    print(f"    Engine ID:          {GE_ENGINE_ID}")
    print(f"    Datastore ID:       {DATASTORE_ID}")
    print(f"    Instance URI:       {INSTANCE_URI}")

    # Check that engine exists
    try:
        engine = _get_engine()
        print(f"[+] Found Gemini Enterprise Engine: '{GE_ENGINE_ID}'")
    except Exception as e:
        print(f"[!] Could not find Engine '{GE_ENGINE_ID}': {e}")
        sys.exit(1)

    # 1. Create Datastore
    ds_url = f"{_base_url()}/collections/{COLLECTION_ID}/dataStores?dataStoreId={DATASTORE_ID}"
    ds_body = {
        "displayName": COLLECTION_DISPLAY_NAME,
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_CHAT"],
        "contentConfig": "CONTENT_CONFIG_DATA_CONNECTOR",
    }
    
    print(f"[*] Creating custom datastore '{DATASTORE_ID}'...")
    resp = requests.post(ds_url, headers=_headers(), json=ds_body, timeout=30)
    if resp.status_code == 409:
        print(f"[+] Datastore '{DATASTORE_ID}' already exists.")
    else:
        resp.raise_for_status()
        lro = resp.json()
        print(f"[*] Waiting for Datastore creation LRO to complete...")
        _wait_lro(lro["name"])
        print(f"[+] Datastore created successfully.")

    # 2. Configure Data Connector
    connector_url = f"{_base_url()}/collections/{COLLECTION_ID}/dataStores/{DATASTORE_ID}/dataConnector"
    connector_body = _data_connector()

    print(f"[*] Configuring Data Connector for '{DATASTORE_ID}'...")
    resp = requests.post(connector_url, headers=_headers(), json=connector_body, timeout=30)
    if resp.status_code == 409:
         print(f"[*] Data connector already configured, patching instead...")
         patch_url = f"{connector_url}?update_mask=actionConfig"
         resp = requests.patch(patch_url, headers=_headers(), json=connector_body, timeout=30)
         resp.raise_for_status()
         lro = resp.json()
    else:
         resp.raise_for_status()
         lro = resp.json()

    print(f"[*] Waiting for Data Connector configuration LRO to complete...")
    _wait_lro(lro["name"])
    print(f"[+] Data Connector configured successfully.")

    # 3. Add Datastore to Gemini Enterprise Engine
    sub_ds_name = _entity_ds_name(DATASTORE_ID)
    current_ds_names = engine.get("dataStoreIds", [])

    if sub_ds_name in current_ds_names:
        print(f"[+] Datastore already attached to Engine.")
    else:
        current_ds_names.append(sub_ds_name)
        patch_engine_body = {"dataStoreIds": current_ds_names}
        patch_engine_url = f"{_engine_url()}?updateMask=dataStoreIds"
        print(f"[*] Attaching datastore entity to Engine '{GE_ENGINE_ID}'...")
        resp = requests.patch(patch_engine_url, headers=_headers(), json=patch_engine_body, timeout=30)
        resp.raise_for_status()
        lro = resp.json()
        print(f"[*] Waiting for Engine patch LRO to complete...")
        _wait_lro(lro["name"])
        print(f"[+] Datastore attached to Engine successfully.")

    print(f"\n[+] Registration finished!")
    print(f"    Go to the Gemini Enterprise Admin Console to authorize and activate.")
    print(f"    Data Store View: https://console.cloud.google.com/gen-app-builder/engines/{GE_ENGINE_ID}/data-stores?project={GE_PROJECT_ID}")


if __name__ == "__main__":
    main()
