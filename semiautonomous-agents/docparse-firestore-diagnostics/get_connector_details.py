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
    
    # Fetch DataConnector
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/docparse-firestore-mcp-1780165632/dataConnector"
    r = requests.get(url, headers=headers)
    print(f"DataConnector response ({r.status_code}):")
    try:
        print(r.json())
    except:
        print(r.text)

if __name__ == "__main__":
    main()
