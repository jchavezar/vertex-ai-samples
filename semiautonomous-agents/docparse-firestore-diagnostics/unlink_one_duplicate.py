import google.auth
import google.auth.transport.requests
import requests

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
    
    # 1. Patch engine to keep exactly 2 datastores: the original one and the new active one
    engine_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/docparse_1780161524773"
    r = requests.get(engine_url, headers=headers)
    if r.status_code == 200:
        orig = r.json()
        new_ids = ["docparse-firestore-mcp-1780162063", "docparse-firestore-mcp-1780165632_mcp_data"]
        patch_body = {
            "name": orig["name"],
            "displayName": orig["displayName"],
            "dataStoreIds": new_ids
        }
        patch_url = f"{engine_url}?updateMask=dataStoreIds"
        print(f"Unlinking docparse-firestore-mcp-1780162342_mcp_data... setting to {new_ids}")
        patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
        print(f"Engine Patch Response ({patch_r.status_code}): {patch_r.text}")
    else:
        print(f"Error fetching engine: {r.status_code} - {r.text}")

    # 2. Try deleting the unlinked datastore docparse-firestore-mcp-1780162342_mcp_data
    ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/docparse-firestore-mcp-1780162342_mcp_data"
    print("\nDeleting older datastore docparse-firestore-mcp-1780162342_mcp_data...")
    del_ds_r = requests.delete(ds_url, headers=headers)
    print(f"Delete Datastore Response ({del_ds_r.status_code}): {del_ds_r.text}")

if __name__ == "__main__":
    main()
