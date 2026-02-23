
import requests
import google.auth
import google.auth.transport.requests
import time
import json

# Configuration
PROJECT_NUMBER = "254356041555"
ENGINE_ID = "agentspace-testing_1748446185255"
LOCATION = "global"
COLLECTION = "default_collection"

# Authenticate
credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token

headers = {
    "Authorization": f"Bearer {access_token}",
    "X-Goog-User-Project": PROJECT_NUMBER,
    "Content-Type": "application/json"
}

def list_agents():
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE_ID}/assistants/default_assistant/agents"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error listing agents: {resp.text}")
        return []
    result = resp.json().get("agents", [])
    print(f"Listed {len(result)} agents.")
    return result

def delete_agent(agent_name):
    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?force=true"
    print(f"Deleting: {url}")
    resp = requests.delete(url, headers=headers)
    
    if resp.status_code in [200, 204]:
        print(f"Successfully deleted {agent_name}")
        return True
    else:
        print(f"Failed to delete {agent_name}: {resp.text}")
        return False

def main():
    print("--- Starting Cleanup of GE Agents ---")
    
    # 1. Fetch Agents
    agents = list_agents()
    
    deleted_count = 0
    
    for agent in agents:
        display_name = agent.get("displayName", "")
        name = agent.get("name", "")
        
        # We target duplicates and specific test agents
        # Matches 'GEMINIPayloadInterceptor' (exact or partial)
        should_delete = "GEMINIPayloadInterceptor" in display_name or \
                        "GE Agent" in display_name or \
                        "Test Agent" in display_name

        if should_delete:
            print(f"IDENTIFIED FOR DELETION: {display_name} ({name})")
            if delete_agent(name):
                deleted_count += 1
                time.sleep(0.5) 
                
    print(f"--- Cleanup Complete. Deleted {deleted_count} agents. ---")

if __name__ == "__main__":
    main()
