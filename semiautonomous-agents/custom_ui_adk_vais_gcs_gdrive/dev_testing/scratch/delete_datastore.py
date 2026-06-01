import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    ds_id = "gcs-fin_1780200804119_gcs_store"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # Delete datastore
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{ds_id}"
    print(f"Sending DELETE request to: {url}")
    r = requests.delete(url, headers=headers)
    print(f"Status Code: {r.status_code}")
    if r.status_code in [200, 202]:
        print("Success! Deletion response:")
        print(json.dumps(r.json(), indent=2))
    else:
        print("Failed to delete datastore:")
        print(r.text)

if __name__ == "__main__":
    main()
