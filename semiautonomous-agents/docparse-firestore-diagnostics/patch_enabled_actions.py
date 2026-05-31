import google.auth
import google.auth.transport.requests
import requests
import json

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    connector_id = "docparse-firestore-mcp-1780165632"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # 1. Fetch current connector
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error fetching connector: {r.status_code} - {r.text}")
        return
        
    orig = r.json()
    bap_config = orig.get("bapConfig", {})
    
    # Update bapConfig to include search and fetch
    bap_config["enabledActions"] = ["search_docs", "list_documents", "search", "fetch"]
    
    patch_body = {
        "name": orig["name"],
        "bapConfig": bap_config
    }
    
    patch_url = f"{url}?updateMask=bapConfig"
    print("Patching connector bapConfig.enabledActions...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        print(json.dumps(patch_r.json(), indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
