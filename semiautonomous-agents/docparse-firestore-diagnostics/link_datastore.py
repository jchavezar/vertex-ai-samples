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
    
    # Try calling the API to link/create a dataStore connection to engine
    # POST https://discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/global/collections/default_collection/engines/{engine}/dataStores
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/docparse_1780161524773/dataStores"
    body = {
        "dataStore": "projects/254356041555/locations/global/collections/default_collection/dataStores/docparse-firestore-mcp-1780165632_mcp_data"
    }
    
    print("Trying to link data store to engine...")
    r = requests.post(url, headers=headers, json=body)
    print(f"Response ({r.status_code}):")
    try:
        print(r.json())
    except:
        print(r.text)

if __name__ == "__main__":
    main()
