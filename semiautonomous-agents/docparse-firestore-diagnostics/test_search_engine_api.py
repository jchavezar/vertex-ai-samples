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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
    
    body = {
        "query": {
            "text": query_text
        }
    }
    
    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
        return
        
    resp_data = r.json()
    print(json.dumps(resp_data, indent=2))

if __name__ == "__main__":
    test_query("what is the metaverse?")
