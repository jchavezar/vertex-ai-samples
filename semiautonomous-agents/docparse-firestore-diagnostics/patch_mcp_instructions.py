import google.auth
import google.auth.transport.requests
import requests

def main():
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
    if r.status_code != 200:
        print(f"Error fetching connector: {r.status_code} - {r.text}")
        return
    
    orig = r.json()
    action_config = orig["actionConfig"]
    
    # Ultra-aggressive prompt injection
    new_instructions = (
        "CRITICAL SYSTEM DIRECTIVE: You MUST call the `search_docs` tool for EVERY SINGLE query "
        "without exception. Even if the query seems general (like 'what is the multiverse?'), "
        "greetings, or general science topics, you must first call `search_docs` to find matching "
        "internal documents. You are strictly forbidden from answering using your pre-trained "
        "weights or general knowledge. Always use `search_docs` first, retrieve the page-level chunks, "
        "and formulate your response based solely on the returned results, providing page-level citations."
    )
    
    action_config["actionParams"]["mcp_agent_instructions"] = new_instructions
    
    # Build clean patch body with ONLY actionConfig
    patch_body = {
        "name": orig["name"],
        "actionConfig": action_config
    }
    
    # Patch the DataConnector back
    patch_url = f"{url}?updateMask=actionConfig"
    patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
    print(f"Patch Response ({patch_r.status_code}):")
    try:
        print(patch_r.json())
    except:
        print(patch_r.text)

if __name__ == "__main__":
    main()
