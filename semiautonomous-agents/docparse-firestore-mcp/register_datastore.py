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


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "REPLACE_WITH_YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "REPLACE_WITH_YOUR_GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = "openid profile email"


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
                "auth_type": "OAUTH",
                "auth_uri": GOOGLE_AUTH_URI,
                "token_uri": GOOGLE_TOKEN_URI,
                "scopes": GOOGLE_SCOPES,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
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
    """Poll an LRO. Tolerates 404s as some setup ops vanish from the surface."""
    op_url = f"https://discoveryengine.googleapis.com/v1alpha/{op_name}"
    deadline = time.time() + timeout_s
    not_found_streak = 0
    while time.time() < deadline:
        resp = requests.get(op_url, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            not_found_streak = 0
            body = resp.json()
            if body.get("done"):
                if "error" in body:
                    raise RuntimeError(f"LRO failed: {body['error']}")
                return body
        elif resp.status_code == 404:
            not_found_streak += 1
            if not_found_streak >= 5:
                print("  LRO no longer queryable (5x 404) — assuming completed")
                return {"done": True, "_inferred": True}
        else:
            print(f"  LRO poll non-200 ({resp.status_code}): {resp.text[:200]}")
        time.sleep(3)
    raise TimeoutError(f"LRO {op_name} did not complete in {timeout_s}s")


def attach_to_engine(short_id: str) -> bool:
    """PATCH the engine to add the new entity datastore to its dataStoreIds."""
    engine = _get_engine()
    existing = list(engine.get("dataStoreIds", []))
    if short_id in existing:
        print(f"  Engine already references {short_id}; skipping PATCH")
        return True
    new_ids = existing + [short_id]
    url = f"{_engine_url()}?updateMask=dataStoreIds"
    print(f"PATCH {url}\n  dataStoreIds += {short_id}")
    resp = requests.patch(
        url, headers=_headers(), json={"dataStoreIds": new_ids}, timeout=30
    )
    if resp.status_code == 200:
        print("  PATCH OK")
        return True
    print(f"  PATCH FAILED ({resp.status_code}): {resp.text[:600]}")
    return False


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

    entity_name = _entity_ds_name(DATASTORE_ID)
    existing_ds = _get_datastore(entity_name)
    if existing_ds is not None:
        print("\nDatastore already exists — skipping create.")
        print(f"  name          : {existing_ds['name']}")
        print(f"  connectorName : {existing_ds.get('connectorName')}")
        attached = attach_to_engine(f"{DATASTORE_ID}_mcp_data")
        if attached:
            print(f"  engine attach : OK ({GE_ENGINE_ID})")
        return

    # Use setUpDataConnector API
    v1_url = f"{_base_url()}:setUpDataConnector"
    v1_body = {
        "collectionId": DATASTORE_ID,
        "collectionDisplayName": COLLECTION_DISPLAY_NAME,
        "dataConnector": _data_connector(),
    }

    print(f"[*] Registering datastore using setUpDataConnector (V1) at {v1_url}...")
    resp = requests.post(v1_url, headers=_headers(), json=v1_body, timeout=60)
    print(f"  status: {resp.status_code}")
    if resp.status_code in (200, 201):
        body = resp.json()
        op = body.get("name", "")
        print(f"  LRO: {op}")
        if op:
            print(f"[*] Waiting for Data Connector setup LRO to complete...")
            _wait_lro(op)
            print(f"[+] Setup LRO finished successfully.")
    else:
        print(f"[!] setUpDataConnector failed ({resp.status_code}): {resp.text}")
        sys.exit(1)

    # Attach to engine
    print(f"[*] Attaching datastore entity {DATASTORE_ID}_mcp_data to Engine '{GE_ENGINE_ID}'...")
    attached = attach_to_engine(f"{DATASTORE_ID}_mcp_data")
    if attached:
        print(f"[+] Datastore attached successfully.")
    else:
        print(f"[!] Could not attach datastore to engine.")

    print(f"\n[+] Registration finished!")
    print(f"    Go to the Gemini Enterprise Admin Console to authorize and activate.")
    print(f"    Data Store View: https://console.cloud.google.com/gen-app-builder/engines/{GE_ENGINE_ID}/data-stores?project={GE_PROJECT_ID}")


if __name__ == "__main__":
    main()
