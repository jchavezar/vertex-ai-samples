import google.auth
import google.auth.transport.requests
import requests
import json

def test_agent_converse(agent_id, query_text):
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
    
    if agent_id:
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/{agent_id}/conversations/-:converse"
    else:
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/conversations/-:converse"
        
    body = {
        "query": {
            "input": query_text
        }
    }
    
    print(f"\n======================================")
    print(f"Endpoint: {url}")
    print(f"Sending Query: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    resp_data = r.json()
    print(json.dumps(resp_data, indent=2))

if __name__ == "__main__":
    # Test assistant-level converse
    test_agent_converse(None, "what is the metaverse?")
    # Test agent-level (deep_research) converse
    test_agent_converse("deep_research", "what is the metaverse?")
