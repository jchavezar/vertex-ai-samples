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
    
    # Discovery Engine AnswerQuery endpoint
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/sessions/-/answerQuery"
    
    body = {
        "query": {
            "queryDescription": "User query",
            "textPrompt": query_text
        },
        "answerSpec": {
            "searchSpec": {
                "searchParams": {
                    "maxReturnResults": 5
                }
            }
        }
    }
    
    print(f"\n======================================")
    print(f"Sending Query to Discovery Engine API: '{query_text}'")
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
    
    # Extract citations/steps/grounding if any
    steps = resp_data.get("answer", {}).get("steps", [])
    print(f"\nSteps executed: {len(steps)}")
    for i, step in enumerate(steps):
        print(f"  Step {i+1} Type: {step.get('state', 'Unknown')}")
        actions = step.get("actions", [])
        for action in actions:
            # Check for tool call
            tool_call = action.get("toolCall", {})
            if tool_call:
                print(f"    Tool Call: {tool_call.get('tool', 'unknown')} with args: {tool_call.get('args', {})}")
            tool_use = action.get("toolUse", {})
            if tool_use:
                print(f"    Tool Use: {tool_use.get('tool', 'unknown')} output size: {len(str(tool_use.get('output', '')))}")
                
    # Extract references
    references = resp_data.get("answer", {}).get("references", [])
    print(f"\nReferences/Citations: {len(references)}")
    for ref in references:
        print(f"  - Title: {ref.get('title', 'Unknown')}, URI: {ref.get('uri', 'None')}")

def main():
    # Test 1: Metaverse (Should find it in Accenture PDF and answer with citations)
    test_query("what is the metaverse?")
    
    # Test 2: General/Multiverse (Should be refused because it's not in the PDF!)
    test_query("what is the multiverse?")

if __name__ == "__main__":
    main()
