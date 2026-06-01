import google.auth
import google.auth.transport.requests
import requests
import json
import time

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
    
    # 1. Create the new GCS Data Store with ACLs enabled
    create_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores?dataStoreId={ds_id}"
    create_payload = {
        "displayName": "GCS Secure Financials ACL",
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "CONTENT_REQUIRED",
        "aclEnabled": True
    }
    
    print(f"--- 1. Creating Data Store '{ds_id}' ---")
    print(f"POST {create_url}")
    print(json.dumps(create_payload, indent=2))
    
    r = requests.post(create_url, headers=headers, json=create_payload)
    print(f"Status Code: {r.status_code}")
    if r.status_code in [200, 201]:
        print("Success! Data store created:")
        print(json.dumps(r.json(), indent=2))
    elif r.status_code == 409:
        print("Data store already exists (409), continuing to import...")
    else:
        print("Failed to create data store:")
        print(r.text)
        return
        
    # 2. Trigger the import from gs://vtxdemos-datasets-acl/metadata.jsonl
    import_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{ds_id}/branches/0/documents:import"
    import_payload = {
        "gcsSource": {
            "inputUris": [
                "gs://vtxdemos-datasets-acl/metadata.jsonl"
            ],
            "dataSchema": "custom"
        },
        "reconciliationMode": "INCREMENTAL"
    }
    
    print(f"\n--- 2. Triggering Document Import ---")
    print(f"POST {import_url}")
    print(json.dumps(import_payload, indent=2))
    
    r_import = requests.post(import_url, headers=headers, json=import_payload)
    print(f"Status Code: {r_import.status_code}")
    if r_import.status_code in [200, 202]:
        print("Import successfully initiated! Long Running Operation details:")
        print(json.dumps(r_import.json(), indent=2))
    else:
        print("Failed to initiate import:")
        print(r_import.text)

if __name__ == "__main__":
    main()
