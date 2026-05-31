import google.auth
import google.auth.transport.requests
import requests
import json

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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant"
    
    body = {
        "name": f"projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant",
        "googleSearchGroundingEnabled": False,
        "webGroundingType": "WEB_GROUNDING_TYPE_UNSPECIFIED"
    }
    
    patch_url = f"{url}?update_mask=googleSearchGroundingEnabled,webGroundingType"
    print("Patching assistant to disable googleSearchGroundingEnabled...")
    r = requests.patch(patch_url, headers=headers, json=body)
    print(f"Response Status: {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)

if __name__ == "__main__":
    main()
