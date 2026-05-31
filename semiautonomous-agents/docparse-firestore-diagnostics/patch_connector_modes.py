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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    
    patch_body = {
        "name": f"projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector",
        "connectorModes": ["ACTIONS", "FEDERATED"],
        "refreshInterval": "10800s" # 3 hours minimum
    }
    
    patch_url = f"{url}?updateMask=connectorModes,refreshInterval"
    print("Patching connectorModes and refreshInterval...")
    r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Response ({r.status_code}):")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)

if __name__ == "__main__":
    main()
