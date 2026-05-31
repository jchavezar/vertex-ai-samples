import google.auth
import google.auth.transport.requests
import requests
import json

def test_assistant_converse(query_text):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "docparse_1780161524773"
    assistant_id = "default_assistant"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # Notice that in gemini-api.js, it uses us-discoveryengine.googleapis.com and location is global
    locations = ["global"]
    for loc in locations:
        url = f"https://us-discoveryengine.googleapis.com/v1/projects/{proj_num}/locations/{loc}/collections/default_collection/engines/{engine_id}/assistants/{assistant_id}:converse"
        
        # Notice that in gemini-api.js, it uses query: { text: query_text }
        body = {
            "query": {
                "text": query_text
            },
            "session": f"session-{loc}-{int(google.auth.transport.requests.Request().session is not None)}"
        }
        
        print(f"\n======================================")
        print(f"Calling: {url}")
        print(f"Payload: {json.dumps(body)}")
        print(f"======================================")
        
        r = requests.post(url, headers=headers, json=body)
        print(f"Response Status ({loc}): {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
            break
        else:
            print(r.text)

if __name__ == "__main__":
    test_assistant_converse("what is the metaverse?")
    test_assistant_converse("what is the multiverse?")
