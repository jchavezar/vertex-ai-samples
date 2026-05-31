import google.auth
import google.auth.transport.requests
import requests

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    # Use Project Number
    proj_num = "254356041555"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines"
    r = requests.get(url, headers=headers)
    print("Engines list response:")
    print(r.status_code)
    try:
        data = r.json()
        for engine in data.get("engines", []):
            print(f"Engine: {engine['displayName']} (ID: {engine['name'].split('/')[-1]})")
            print(f"  Data Stores: {engine.get('dataStoreIds', [])}")
            print(f"  Common Config: {engine.get('commonConfig', {})}")
    except Exception as e:
        print(r.text)

if __name__ == "__main__":
    main()
