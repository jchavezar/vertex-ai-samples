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
    
    # List both datastores
    for ds_id in ["docparse-firestore-mcp-1780162063", "docparse-firestore-mcp-1780162342_mcp_data"]:
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{ds_id}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            d = r.json()
            print(f"Datastore: {ds_id}")
            print(f"  Display Name: {d.get('displayName')}")
            print(f"  Connector Name: {d.get('connectorName')}")
        else:
            print(f"Failed to fetch {ds_id}: {r.status_code}")

if __name__ == "__main__":
    main()
