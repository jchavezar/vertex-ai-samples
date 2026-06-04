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
Setup script for WIF + GCS + Gemini Enterprise recipe.
Creates a GCS bucket, uploads a PDF, creates a Data Store,
imports the PDF, and dynamically creates a new search Engine linking the Data Store.
"""
import os
import sys
import time
import requests
import google.auth
import google.auth.transport.requests
from google.cloud import storage

# Load .env file dynamically if present
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

# Configurations
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
PROJECT_NUMBER = os.environ.get("GCP_PROJECT_NUMBER", "254356041555")
LOCATION = os.environ.get("GCP_LOCATION", "global")

# Dynamically generate unique IDs for this run
TIMESTAMP = int(time.time())
DATA_STORE_ID = f"wif-gcs-ds-jesus-{TIMESTAMP}"
ENGINE_ID = f"wif-gcs-eng-jesus-{TIMESTAMP}"
BUCKET_NAME = f"vtxdemos-wif-gcs-jesus-{TIMESTAMP}"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")

# Helper to get credentials and headers
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

def find_pdf_to_upload():
    print(f"[*] Searching for PDF in {DOWNLOADS_DIR}...")
    if not os.path.exists(DOWNLOADS_DIR):
        print(f"[!] Downloads directory not found at {DOWNLOADS_DIR}")
        return None
    
    # Look for common 10k or earnings PDFs first to have good content
    candidates = [
        "10k-files_amzn-10k.pdf",
        "10k-files_goog-10-k-2024.pdf",
        "10k-files_microsoft-10k.pdf",
        "AMZN-Q1-2026-Earnings-Release.pdf"
    ]
    for c in candidates:
        full_path = os.path.join(DOWNLOADS_DIR, c)
        if os.path.exists(full_path):
            print(f"[+] Found ideal PDF: {c}")
            return full_path
            
    # Fallback to any pdf
    for f in os.listdir(DOWNLOADS_DIR):
        if f.endswith(".pdf") and not f.startswith("."):
            full_path = os.path.join(DOWNLOADS_DIR, f)
            print(f"[+] Found PDF fallback: {f}")
            return full_path
            
    return None

def create_gcs_bucket():
    print(f"[*] Creating GCS bucket: gs://{BUCKET_NAME} in region us-central1...")
    client = get_storage_client()
    try:
        bucket = client.bucket(BUCKET_NAME)
        bucket.storage_class = "STANDARD"
        new_bucket = client.create_bucket(bucket, location="us-central1")
        print(f"[+] Bucket created successfully: {new_bucket.name}")
        return True
    except Exception as e:
        print(f"[!] Failed to create bucket: {e}")
        return False

def upload_pdf_to_bucket(pdf_path):
    print(f"[*] Uploading {pdf_path} to gs://{BUCKET_NAME}...")
    client = get_storage_client()
    try:
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(os.path.basename(pdf_path))
        blob.upload_from_filename(pdf_path)
        print(f"[+] PDF uploaded successfully: {blob.name}")
        return blob.name
    except Exception as e:
        print(f"[!] Failed to upload PDF: {e}")
        return None

def create_data_store():
    print(f"[*] Creating Discovery Engine Data Store: {DATA_STORE_ID}...")
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores?dataStoreId={DATA_STORE_ID}"
    
    payload = {
        "displayName": f"WIF GCS Test Jesus ({DATA_STORE_ID})",
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "CONTENT_REQUIRED"
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code in (200, 201):
        print(f"[+] Data Store created successfully: {DATA_STORE_ID}")
        return True
    else:
        print(f"[!] Failed to create Data Store ({resp.status_code}): {resp.text}")
        return False

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
                # Check for import operation specific failures in response
                response_data = body.get("response", {})
                error_samples = response_data.get("errorSamples", [])
                if error_samples:
                    print(f"  [!] LRO completed with errors:")
                    for err in error_samples:
                        print(f"    * {err.get('message')}")
                    return False
                return True
        else:
            print(f"  [!] LRO poll failed ({op_resp.status_code}): {op_resp.text[:200]}")
        time.sleep(10)
    print("  [!] LRO timeout reached.")
    return False

def import_gcs_to_datastore(file_name):
    print(f"[*] Importing gs://{BUCKET_NAME}/{file_name} into Data Store...")
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}/branches/0/documents:import"
    
    payload = {
        "gcsSource": {
            "inputUris": [f"gs://{BUCKET_NAME}/{file_name}"],
            "dataSchema": "content"
        },
        "reconciliationMode": "INCREMENTAL"
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"[!] Import failed to start ({resp.status_code}): {resp.text}")
        return False
        
    op = resp.json().get("name", "")
    print(f"[+] Import LRO started: {op}")
    
    print("[*] Waiting for import operation to complete...")
    if wait_for_lro(op):
        print("[+] Import completed successfully!")
        return True
    return False

def check_engine_exists(engine_id):
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{engine_id}"
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.status_code == 200

def create_engine():
    print(f"[*] Creating Discovery Engine App (Engine): {ENGINE_ID}...")
    headers = get_gcp_headers()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines?engineId={ENGINE_ID}"
    
    # Create the search engine and link the datastore in one shot
    payload = {
        "displayName": f"WIF GCS Test Engine Jesus ({ENGINE_ID})",
        "solutionType": "SOLUTION_TYPE_SEARCH",
        "searchEngineConfig": {
            "searchTier": "SEARCH_TIER_ENTERPRISE",
            "searchAddOns": ["SEARCH_ADD_ON_LLM"],
            "requiredSubscriptionTier": "SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT"
        },
        "industryVertical": "GENERIC",
        "appType": "APP_TYPE_INTRANET",
        "dataStoreIds": [DATA_STORE_ID]
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code not in (200, 201, 202):
        print(f"[!] Engine creation failed to start ({resp.status_code}): {resp.text}")
        return False
        
    print("[*] Waiting for Engine creation to complete...")
    deadline = time.time() + 180
    while time.time() < deadline:
        if check_engine_exists(ENGINE_ID):
            print(f"[+] Engine created successfully: {ENGINE_ID}")
            return True
        time.sleep(10)
        
    print("[!] Timeout waiting for engine creation.")
    return False

def main():
    print("====================================================")
    print("  GCP WIF + GCS + Discovery Engine Setup Script")
    print("====================================================")
    print(f"  Project ID:     {PROJECT_ID}")
    print(f"  Project Number: {PROJECT_NUMBER}")
    print(f"  Location:       {LOCATION}")
    print(f"  New Engine ID:  {ENGINE_ID}")
    print(f"  New Data Store: {DATA_STORE_ID}")
    print("====================================================")
    
    pdf_path = find_pdf_to_upload()
    if not pdf_path:
        print("[!] No PDF found in ~/Downloads to upload. Aborting.")
        sys.exit(1)
        
    if not create_gcs_bucket():
        sys.exit(1)
        
    file_name = upload_pdf_to_bucket(pdf_path)
    if not file_name:
        sys.exit(1)
        
    if not create_data_store():
        sys.exit(1)
        
    if not import_gcs_to_datastore(file_name):
        sys.exit(1)
        
    if not create_engine():
        sys.exit(1)
        
    print("\n====================================================")
    print("  SETUP COMPLETED SUCCESSFULLY!")
    print("====================================================")
    print(f"  Bucket name:    gs://{BUCKET_NAME}")
    print(f"  Data Store ID:  {DATA_STORE_ID}")
    print(f"  Engine ID:      {ENGINE_ID}")
    print("====================================================")
    
    # Save the generated resource names to a local temp file for teardown
    with open("last_setup_resources.json", "w") as f:
        import json
        json.dump({
            "bucket_name": BUCKET_NAME,
            "datastore_id": DATA_STORE_ID,
            "engine_id": ENGINE_ID
        }, f, indent=2)
    print("[*] Resource configuration saved to last_setup_resources.json for teardown.")

if __name__ == "__main__":
    main()
