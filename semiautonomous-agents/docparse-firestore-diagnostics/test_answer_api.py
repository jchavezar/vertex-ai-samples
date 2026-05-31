import google.auth
import google.auth.transport.requests
import requests
import json

def test_query(query_text):
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
    
    # Correct :answer serving config URL
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_serving_config:answer"
    
    body = {
        "query": {
            "text": query_text
        }
    }
    
    print(f"\n======================================")
    print(f"Sending :answer Query to Discovery Engine API: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    resp_data = r.json()
    
    # Extract response answer text
    answer = resp_data.get("answer", {})
    answer_text = answer.get("answerText", "No answer text returned.")
    print("\nAnswer Text:")
    print(answer_text)
    
    # Extract steps/grounding
    steps = answer.get("steps", [])
    print(f"\nSteps executed: {len(steps)}")
    for i, step in enumerate(steps):
        print(f"  Step {i+1} Type: {step.get('state', 'Unknown')}")
        actions = step.get("actions", [])
        for action in actions:
            tool_call = action.get("toolCall", {})
            if tool_call:
                print(f"    Tool Call: {tool_call.get('tool', 'unknown')} with args: {tool_call.get('args', {})}")
            tool_use = action.get("toolUse", {})
            if tool_use:
                print(f"    Tool Use: {tool_use.get('tool', 'unknown')} output: {tool_use.get('output', {})}")

if __name__ == "__main__":
    test_query("what is the metaverse?")
    test_query("what is the multiverse?")
