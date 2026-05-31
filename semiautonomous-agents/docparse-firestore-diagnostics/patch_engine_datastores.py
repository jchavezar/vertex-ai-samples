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
    
    # Let's get current engine configuration
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/docparse_1780161524773"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching engine: {r.status_code} - {r.text}")
        return
    
    orig = r.json()
    print("Original dataStoreIds:", orig.get("dataStoreIds", []))
    
    # Add our target dataStore docparse-firestore-mcp-1780165632_mcp_data
    new_ids = list(orig.get("dataStoreIds", []))
    target_id = "docparse-firestore-mcp-1780165632_mcp_data"
    if target_id not in new_ids:
        new_ids.append(target_id)
        
    patch_body = {
        "name": orig["name"],
        "displayName": orig["displayName"],
        "dataStoreIds": new_ids
    }
    
    # Try patching dataStoreIds
    patch_url = f"{url}?updateMask=dataStoreIds"
    print(f"Patching engine at {patch_url} with dataStoreIds: {new_ids}")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        print(patch_r.json())
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
