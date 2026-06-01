import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    op_name = "projects/254356041555/locations/global/collections/default_collection/dataStores/gcs-fin-acl-v3/branches/0/operations/import-documents-15376308696474698142"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/{op_name}"
    print(f"GET {url}")
    
    r = requests.get(url, headers=headers)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r.text)

if __name__ == "__main__":
    main()
