import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "csearch-gdrive_1780200758152"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # We only keep the g-drive-connector_1779830697777_google_drive datastore in the list.
    payload = {
        "dataStoreIds": [
            "g-drive-connector_1779830697777_google_drive"
        ]
    }
    
    # Send PATCH request to update the engine
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}?updateMask=dataStoreIds"
    print(f"Sending PATCH request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    r = requests.patch(url, headers=headers, json=payload)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("Success! Updated Engine details:")
        print(json.dumps(r.json(), indent=2))
    else:
        print("Failed to patch engine:")
        print(r.text)

if __name__ == "__main__":
    main()
