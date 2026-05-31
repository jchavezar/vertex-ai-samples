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
    
    # List data stores
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores"
    r = requests.get(url, headers=headers)
    print("Listing all Data Stores in default_collection:")
    if r.status_code == 200:
        datastores = r.json().get("dataStores", [])
        for ds in datastores:
            name = ds.get("name", "")
            ds_id = name.split("/")[-1]
            if "docparse" in ds_id:
                print(f"Found: {ds_id}")
    else:
        print(f"Error: {r.status_code} - {r.text}")

    # List all collections/dataconnectors if any
    print("\nListing data connectors under docparse-firestore-mcp-1780165632:")
    connector_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/docparse-firestore-mcp-1780165632/dataConnector"
    r_conn = requests.get(connector_url, headers=headers)
    print(f"docparse-firestore-mcp-1780165632 dataConnector status: {r_conn.status_code}")
    if r_conn.status_code == 200:
        print(r_conn.json())

    # Try for docparse-firestore-mcp-1780162342
    print("\nListing data connectors under docparse-firestore-mcp-1780162342:")
    connector_url2 = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/docparse-firestore-mcp-1780162342/dataConnector"
    r_conn2 = requests.get(connector_url2, headers=headers)
    print(f"docparse-firestore-mcp-1780162342 dataConnector status: {r_conn2.status_code}")

if __name__ == "__main__":
    main()
