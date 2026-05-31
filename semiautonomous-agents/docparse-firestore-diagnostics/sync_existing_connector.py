import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    connector_id = "docparse-firestore-mcp-1780165632"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # POST to dataConnector:sync to force it to pull our updated tool schemas
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector:sync"
    print(f"Triggering sync on existing connector {connector_id} at {url}...")
    r = requests.post(url, headers=headers, json={})
    print(f"Sync response ({r.status_code}):")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)

if __name__ == "__main__":
    main()
