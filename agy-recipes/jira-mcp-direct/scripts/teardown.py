# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "requests",
# ]
# ///
"""
Teardown script for Atlassian Jira MCP Direct integration recipe.
Deletes all registered datastores in GE, detaches them from the engine,
and deletes the deployed Cloud Run service.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
import requests
import google.auth
import google.auth.transport.requests

_HERE = Path(__file__).resolve().parent
RESOURCE_FILE = _HERE.parent / "last_setup_resources.json"

def get_gcp_headers(project_id):
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": project_id
    }

def delete_datastore(project_number, location, datastore_id, project_id):
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project_number}/locations/{location}/"
        f"collections/{datastore_id}"
    )
    print(f"[*] Deleting datastore connection collection '{datastore_id}'...")
    resp = requests.delete(url, headers=get_gcp_headers(project_id), timeout=60)
    if resp.status_code in (200, 202, 204):
        print(f"[+] Datastore collection '{datastore_id}' deleted successfully.")
    elif resp.status_code == 404:
        print(f"[*] Datastore collection '{datastore_id}' not found (already deleted).")
    else:
        print(f"[!] Failed to delete datastore collection '{datastore_id}': {resp.text}")

def detach_from_engine(project_number, location, engine_id, datastore_short_ids, project_id):
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project_number}/locations/{location}/"
        f"collections/default_collection/engines/{engine_id}"
    )
    print(f"[*] Detaching datastores {datastore_short_ids} from engine '{engine_id}'...")
    try:
        r = requests.get(url, headers=get_gcp_headers(project_id), timeout=30)
        if r.status_code == 404:
            print(f"[*] Engine '{engine_id}' not found.")
            return
        r.raise_for_status()
        engine_data = r.json()
        current_ids = list(engine_data.get("dataStoreIds", []))
        
        updated_ids = [ds_id for ds_id in current_ids if ds_id not in datastore_short_ids]
        
        patch_url = f"{url}?updateMask=dataStoreIds"
        r_patch = requests.patch(patch_url, headers=get_gcp_headers(project_id), json={"dataStoreIds": updated_ids}, timeout=30)
        if r_patch.status_code == 200:
            print("[+] Engine updated/detached successfully.")
        else:
            print(f"[!] Engine detach failed: {r_patch.text}.")
    except Exception as e:
        print(f"[!] Failed to detach datastores: {e}")

def main():
    print("====================================================")
    print("  Jira MCP Direct Teardown Execution")
    print("====================================================")

    if not RESOURCE_FILE.exists():
        print(f"[!] Tracker file {RESOURCE_FILE} not found. Nothing to tear down.")
        sys.exit(0)

    try:
        with open(RESOURCE_FILE, "r") as f:
            resources = json.load(f)
    except Exception as e:
        print(f"[!] Error reading tracker file: {e}")
        sys.exit(1)

    project_id = resources.get("project_id", "vtxdemos")
    project_number = resources.get("project_number", "254356041555")
    location = resources.get("location", "global")
    engine_id = resources.get("engine_id")
    cloud_run_service = resources.get("cloud_run_service")
    cloud_run_region = resources.get("cloud_run_region", "us-central1")
    datastore_rovo_id = resources.get("datastore_rovo_id")
    datastore_custom_id = resources.get("datastore_custom_id")

    # 1. Detach from Engine
    if engine_id and (datastore_rovo_id or datastore_custom_id):
        short_ids = []
        if datastore_rovo_id:
            short_ids.append(f"{datastore_rovo_id}_mcp_data")
        if datastore_custom_id:
            short_ids.append(f"{datastore_custom_id}_mcp_data")
        detach_from_engine(project_number, location, engine_id, short_ids, project_id)

    # 2. Delete Datastore Collections in GE
    if datastore_rovo_id:
        delete_datastore(project_number, location, datastore_rovo_id, project_id)
    if datastore_custom_id:
        delete_datastore(project_number, location, datastore_custom_id, project_id)

    # 3. Delete Cloud Run Service
    if cloud_run_service:
        print(f"[*] Deleting Cloud Run service '{cloud_run_service}'...")
        delete_cmd = [
            "gcloud", "run", "services", "delete", cloud_run_service,
            "--region", cloud_run_region,
            "--project", project_id,
            "--quiet"
        ]
        print(f"[*] Running: {' '.join(delete_cmd)}")
        res = subprocess.run(delete_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Cloud Run service '{cloud_run_service}' deleted successfully.")
        else:
            print(f"[!] Cloud Run deletion failed: {res.stderr}")

    # Remove tracker file
    try:
        RESOURCE_FILE.unlink()
        print(f"[+] Tracker file {RESOURCE_FILE} deleted.")
    except Exception as e:
        print(f"[!] Failed to delete tracker file: {e}")

    print("[+] Teardown execution complete.")
    print("====================================================")

if __name__ == "__main__":
    main()
