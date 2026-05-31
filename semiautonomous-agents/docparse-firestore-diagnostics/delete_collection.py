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
    
    # Let's delete the collection itself
    collection_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/docparse-firestore-mcp-1780162342"
    print("Deleting older collection docparse-firestore-mcp-1780162342...")
    r = requests.delete(collection_url, headers=headers)
    print(f"Delete Collection Response ({r.status_code}): {r.text}")

if __name__ == "__main__":
    main()
