import google.auth
import google.auth.transport.requests
import requests

def test_patch(mask):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    connector_id = "docparse-firestore-mcp-1780162342"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # 1. Fetch current connector config
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/{connector_id}/dataConnector"
    r = requests.get(url, headers=headers)
    orig = r.json()
    action_config = orig["actionConfig"]
    
    new_instructions = (
        "CRITICAL SYSTEM DIRECTIVE: You MUST call the `search_docs` tool for EVERY SINGLE query "
        "without exception. Even if the query seems general (like 'what is the multiverse?'), "
        "greetings, or general science topics, you must first call `search_docs` to find matching "
        "internal documents. You are strictly forbidden from answering using your pre-trained "
        "weights or general knowledge. Always use `search_docs` first, retrieve the page-level chunks, "
        "and formulate your response based solely on the returned results, providing page-level citations."
    )
    
    action_config["actionParams"]["mcp_agent_instructions"] = new_instructions
    
    patch_body = {
        "name": orig["name"],
        "actionConfig": action_config
    }
    
    patch_url = f"{url}?updateMask={mask}"
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Mask '{mask}' -> Status {patch_r.status_code}")
    print(patch_r.text)

def main():
    test_patch("action_config")
    test_patch("actionConfig.actionParams.mcp_agent_instructions")

if __name__ == "__main__":
    main()
