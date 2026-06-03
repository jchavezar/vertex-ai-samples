# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-storage",
#     "requests",
#     "google-auth",
#     "pyopenssl",
# ]
# ///
"""
Teardown script for WIF + GCS + Gemini Enterprise recipe.
Loads configuration from last_setup_resources.json,
deletes the Engine, deletes the Data Store, and deletes the GCS bucket.
"""
import os
import sys
import json
import time
import requests
import google.auth
import google.auth.transport.requests
from google.cloud import storage

# Configurations
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
PROJECT_NUMBER = os.environ.get("GCP_PROJECT_NUMBER", "254356041555")
LOCATION = os.environ.get("GCP_LOCATION", "global")
RESOURCE_FILE = "last_setup_resources.json"

def get_gcp_headers():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID
    }

def get_storage_client():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return storage.Client(credentials=creds, project=PROJECT_ID)

def load_resources():
    if not os.path.exists(RESOURCE_FILE):
        print(f"[!] {RESOURCE_FILE} not found. Cannot proceed with automatic teardown.")
        return None
    try:
        with open(RESOURCE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load resources file: {e}")
        return None

def wait_for_lro(op_name, timeout_s=600):
    """Poll an LRO until complete."""
    headers = get_gcp_headers()
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        op_url = f"https://discoveryengine.googleapis.com/v1alpha/{op_name}"
        op_resp = requests.get(op_url, headers=headers, timeout=30)
        if op_resp.status_code == 200:
            body = op_resp.json()
            if body.get("done"):
                if "error" in body:
                    print(f"  [!] LRO failed: {body['error']}")
                    return False
                return True
        else:
            if op_resp.status_code == 404:
                print("  [+] LRO returned 404. Assuming resource deletion succeeded.")
                return True
            print(f"  [!] LRO poll failed ({op_resp.status_code}): {op_resp.text[:200]}")
        time.sleep(10)
    print("  [!] LRO timeout reached.")
    return False

def delete_engine(engine_id):
    print(f"[*] Deleting Discovery Engine App (Engine): {engine_id}...")
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{engine_id}"
    
    resp = requests.delete(url, headers=headers, timeout=30)
    if resp.status_code not in (200, 202, 204):
        print(f"[!] Engine deletion failed to start ({resp.status_code}): {resp.text}")
        return False
        
    op = resp.json().get("name", "")
    print(f"[+] Engine deletion LRO started: {op}")
    
    print("[*] Waiting for Engine deletion to complete...")
    if wait_for_lro(op):
        print(f"[+] Engine deleted successfully: {engine_id}")
        return True
    return False

def delete_data_store(datastore_id):
    print(f"[*] Deleting Discovery Engine Data Store: {datastore_id}...")
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{datastore_id}"
    
    resp = requests.delete(url, headers=headers, timeout=30)
    if resp.status_code in (200, 204):
        print(f"[+] Data Store deleted successfully: {datastore_id}")
        return True
        
    # Sometimes it returns an LRO
    if resp.status_code == 202:
        op = resp.json().get("name", "")
        print(f"[+] Data Store deletion LRO started: {op}")
        if wait_for_lro(op):
            print(f"[+] Data Store deleted successfully: {datastore_id}")
            return True
        return False
        
    print(f"[!] Failed to delete Data Store ({resp.status_code}): {resp.text}")
    return False

def delete_gcs_bucket(bucket_name):
    print(f"[*] Deleting GCS bucket gs://{bucket_name} and all its contents...")
    client = get_storage_client()
    try:
        bucket = client.get_bucket(bucket_name)
        # Delete all blobs first
        blobs = list(bucket.list_blobs())
        for b in blobs:
            print(f"  Deleting blob: {b.name}")
            b.delete()
        # Delete bucket
        bucket.delete()
        print(f"[+] Bucket gs://{bucket_name} deleted successfully.")
        return True
    except Exception as e:
        print(f"[!] Failed to delete bucket: {e}")
        return False

def main():
    print("====================================================")
    print("  GCP WIF + GCS + Discovery Engine Teardown Script")
    print("====================================================")
    
    resources = load_resources()
    if not resources:
        sys.exit(1)
        
    bucket_name = resources.get("bucket_name")
    datastore_id = resources.get("datastore_id")
    engine_id = resources.get("engine_id")
    
    if not engine_id or not datastore_id or not bucket_name:
        print("[!] Invalid resources file format. Aborting.")
        sys.exit(1)
        
    # Run teardown steps
    delete_engine_ok = delete_engine(engine_id)
    # Even if engine deletion fails, attempt to delete the datastore and bucket
    delete_ds_ok = delete_data_store(datastore_id)
    delete_bucket_ok = delete_gcs_bucket(bucket_name)
    
    if delete_engine_ok and delete_ds_ok and delete_bucket_ok:
        print("\n====================================================")
        print("  TEARDOWN COMPLETED SUCCESSFULLY!")
        print("====================================================")
        if os.path.exists(RESOURCE_FILE):
            os.remove(RESOURCE_FILE)
            print(f"[*] Removed {RESOURCE_FILE}")
        sys.exit(0)
    else:
        print("\n[!] Teardown completed with errors. Some resources may not have been cleaned up.")
        sys.exit(1)

if __name__ == "__main__":
    main()
