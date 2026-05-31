import google.auth
import google.auth.transport.requests
import requests

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "docparse_1780161524773"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # Get serving configuration details for default_search
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search"
    r = requests.get(url, headers=headers)
    print("Serving config details:")
    print(r.status_code)
    if r.status_code == 200:
        import json
        print(json.dumps(r.json(), indent=2))
    else:
        print(r.text)

if __name__ == "__main__":
    main()
