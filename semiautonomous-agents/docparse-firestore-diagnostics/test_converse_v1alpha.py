import google.auth
import google.auth.transport.requests
import requests
import json

def test_converse_v1alpha(query_text):
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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/conversations/-:converse"
    
    body = {
        "query": {
            "input": query_text
        },
        "summarySpec": {
            "summaryResultCount": 5
        }
    }
    
    print(f"\n======================================")
    print(f"Calling v1alpha converse with: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    test_converse_v1alpha("what is the metaverse?")
    test_converse_v1alpha("what is the multiverse?")
