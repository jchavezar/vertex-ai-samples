import google.auth
import google.auth.transport.requests
import requests
import json

def test_converse(query_text):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "docparse_1780161524773"
    collection_id = "default_collection"
    location = "global"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    url = f"https://discoveryengine.googleapis.com/v1/projects/{proj_num}/locations/{location}/collections/{collection_id}/engines/{engine_id}/conversations/-:converse"
    
    body = {
        "query": {
            "input": query_text
        },
        "summarySpec": {
            "summaryResultCount": 5,
            "ignoreAdversarialQuery": True,
            "ignoreNonSummarySeekingQuery": True,
            "ignoreLowRelevantContent": True,
            "ignoreJailBreakingQuery": True
        }
    }
    
    print(f"\n======================================")
    print(f"Sending :converse Query with summarySpec options: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    resp_data = r.json()
    print(json.dumps(resp_data, indent=2))

if __name__ == "__main__":
    test_converse("what is the metaverse?")
    test_converse("what is the multiverse?")
