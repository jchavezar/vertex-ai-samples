import google.auth
import google.auth.transport.requests
import requests
import time

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    engine_id = "docparse_1780161524773"
    engine_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}"
    
    # 1. Delete the old engine
    print(f"Deleting engine {engine_id}...")
    del_r = requests.delete(engine_url, headers=headers)
    print(f"Delete Engine Response ({del_r.status_code}): {del_r.text}")
    
    # Wait for deletion to propagate if asynchronous
    time.sleep(5)
    
    # 2. Create the clean engine with ONLY 1 datastore linked
    create_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines?engineId={engine_id}"
    create_body = {
        "displayName": "docparse",
        "solutionType": "SOLUTION_TYPE_SEARCH",
        "searchEngineConfig": {
            "searchTier": "SEARCH_TIER_ENTERPRISE",
            "searchAddOns": ["SEARCH_ADD_ON_LLM"]
        },
        "industryVertical": "GENERIC",
        "dataStoreIds": ["docparse-firestore-mcp-1780165632_mcp_data"],
        "appType": "APP_TYPE_INTRANET"
    }
    
    print(f"\nCreating clean engine {engine_id} linking ONLY docparse-firestore-mcp-1780165632_mcp_data...")
    create_r = requests.post(create_url, headers=headers, json=create_body)
    print(f"Create Engine Response ({create_r.status_code}): {create_r.text}")
    
    # 3. Now that the old engine is gone, delete the unused datastore docparse-firestore-mcp-1780162063
    time.sleep(3)
    ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/docparse-firestore-mcp-1780162063"
    print("\nDeleting now-unlinked duplicate/unknown datastore docparse-firestore-mcp-1780162063...")
    del_ds_r = requests.delete(ds_url, headers=headers)
    print(f"Delete Datastore Response ({del_ds_r.status_code}): {del_ds_r.text}")

if __name__ == "__main__":
    main()
