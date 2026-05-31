import google.auth
import google.auth.transport.requests
import requests
import json

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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/docparse_1780161524773"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching engine: {r.status_code} - {r.text}")
        return
    
    orig = r.json()
    print("Original dataStoreIds:", orig.get("dataStoreIds", []))
    
    # Replace single datastore with our newly created one that has the updated schema
    new_ids = ["docparse-firestore-mcp-1780180696_mcp_data"]
    
    patch_body = {
        "name": orig["name"],
        "displayName": orig["displayName"],
        "dataStoreIds": new_ids
    }
    
    patch_url = f"{url}?updateMask=dataStoreIds"
    print(f"Replacing engine datastores with exactly: {new_ids}")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Replace Response ({patch_r.status_code}):")
    try:
        print(json.dumps(patch_r.json(), indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
