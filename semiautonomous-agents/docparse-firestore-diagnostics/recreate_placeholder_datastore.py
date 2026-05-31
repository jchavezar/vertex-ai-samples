import google.auth
import google.auth.transport.requests
import requests

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    ds_id = "docparse-firestore-mcp-1780162063"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # Create an empty datastore placeholder
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores?dataStoreId={ds_id}"
    body = {
        "displayName": "docparse-firestore-mcp-1780162063",
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "NO_CONTENT"
    }
    
    print(f"Creating placeholder datastore {ds_id} to satisfy propagating engine cache...")
    r = requests.post(url, headers=headers, json=body)
    print(f"Response ({r.status_code}): {r.text}")

if __name__ == "__main__":
    main()
