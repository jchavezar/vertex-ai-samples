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
    engine_id = "csearch-gdrive-acl_1780275206896"
    old_ds_id = "gcs-fin-acl_1780275401897"
    new_ds_id = f"gcs-fin-acl-v3"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # 1. Create the brand new GCS Datastore with ACLs enabled
    create_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores?dataStoreId={new_ds_id}"
    create_payload = {
        "displayName": "GCS Secure Financials ACL v3",
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "CONTENT_REQUIRED",
        "aclEnabled": True
    }
    
    print(f"--- 1. Creating New Data Store '{new_ds_id}' ---")
    r = requests.post(create_url, headers=headers, json=create_payload)
    print(f"Status Code: {r.status_code}")
    if r.status_code in [200, 201]:
        print("Success! Data store created:")
        print(json.dumps(r.json(), indent=2))
    elif r.status_code == 409:
        print("Data store already exists (409), continuing...")
    else:
        print("Failed to create data store:")
        print(r.text)
        return

    # 2. Update the Engine's Linked Datastores using PATCH
    patch_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}?updateMask=dataStoreIds"
    patch_payload = {
        "dataStoreIds": [
            "gdrive_1780275247923_google_drive",
            new_ds_id
        ]
    }
    print(f"\n--- 2. Updating Engine '{engine_id}' to link '{new_ds_id}' and unlink '{old_ds_id}' ---")
    print(f"PATCH {patch_url}")
    print(json.dumps(patch_payload, indent=2))
    
    r_patch = requests.patch(patch_url, headers=headers, json=patch_payload)
    print(f"Status Code: {r_patch.status_code}")
    if r_patch.status_code == 200:
        print("Success! Updated Engine details:")
        print(json.dumps(r_patch.json(), indent=2))
    else:
        print("Failed to patch engine:")
        print(r_patch.text)
        return

    # 3. Delete the old datastore resource to clean up the workspace
    delete_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{old_ds_id}"
    print(f"\n--- 3. Deleting Old Data Store Resource '{old_ds_id}' ---")
    r_del = requests.delete(delete_url, headers=headers)
    print(f"Status Code: {r_del.status_code}")
    if r_del.status_code in [200, 202]:
        print("Success! Old datastore resource deletion initiated.")
    else:
        print("Failed to delete old datastore resource:")
        print(r_del.text)

    # 5. Trigger Document Import from gs://vtxdemos-datasets-acl/metadata.jsonl with dataSchema='document'
    import_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{new_ds_id}/branches/0/documents:import"
    import_payload = {
        "gcsSource": {
            "inputUris": [
                "gs://vtxdemos-datasets-acl/metadata.jsonl"
            ],
            "dataSchema": "document"
        },
        "reconciliationMode": "INCREMENTAL"
    }
    print(f"\n--- 5. Triggering Clean Document Import on '{new_ds_id}' ---")
    r_import = requests.post(import_url, headers=headers, json=import_payload)
    print(f"Status Code: {r_import.status_code}")
    if r_import.status_code in [200, 202]:
        print("Success! Document import operation successfully initiated.")
        print(json.dumps(r_import.json(), indent=2))
    else:
        print("Failed to trigger document import:")
        print(r_import.text)

if __name__ == "__main__":
    main()
