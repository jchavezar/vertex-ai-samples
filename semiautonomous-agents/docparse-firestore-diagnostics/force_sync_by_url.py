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
    current_uri = orig["params"]["instance_uri"]
    
    # Determine new URI version suffix
    if "?v=" in current_uri:
        base_uri, current_version = current_uri.split("?v=")
        new_version = int(current_version) + 1
    else:
        base_uri = current_uri
        new_version = 2
        
    new_uri = f"{base_uri}?v={new_version}"
    print(f"Updating instance_uri from '{current_uri}' to '{new_uri}' to force fresh tool sync...")
    
    # Build patch payload with only instance_uri fields to bypass OAuth validation
    patch_body = {
        "name": orig["name"],
        "params": {
            "instance_uri": new_uri
        },
        "actionConfig": {
            "actionParams": {
                "instance_uri": new_uri
            }
        }
    }
    
    # Patch the DataConnector with targeted update masks
    patch_url = f"{url}?updateMask=params.instance_uri,actionConfig.actionParams.instance_uri"
    print("Sending patch request...")
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        res = patch_r.json()
        if patch_r.status_code == 200:
            print("Force sync successful! Current dynamic tools list:")
            print(json.dumps(res.get("dynamicTools"), indent=2))
        else:
            print("Error Response Body:")
            print(json.dumps(res, indent=2))
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
