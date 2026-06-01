import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    ds_id = "gcs-fin-acl"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    import_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{ds_id}/branches/0/documents:import"
    
    # We change dataSchema to "document" to match standard Discovery Engine Document schema
    import_payload = {
        "gcsSource": {
            "inputUris": [
                "gs://vtxdemos-datasets-acl/metadata.jsonl"
            ],
            "dataSchema": "document"
        },
        "reconciliationMode": "INCREMENTAL"
    }
    
    print(f"Triggering GCS Import with dataSchema='document' on '{ds_id}'...")
    print(f"POST {import_url}")
    print(json.dumps(import_payload, indent=2))
    
    r = requests.post(import_url, headers=headers, json=import_payload)
    print(f"Status Code: {r.status_code}")
    if r.status_code in [200, 202]:
        print("Import successfully initiated! Long Running Operation details:")
        print(json.dumps(r.json(), indent=2))
    else:
        print("Failed to trigger import:")
        print(r.text)

if __name__ == "__main__":
    main()
