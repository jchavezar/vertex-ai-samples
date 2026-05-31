import google.auth
import google.auth.transport.requests
import requests
import json

def test_stream_answer(query_text):
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
    
    # streamAnswer URL
    url = f"https://global-discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:streamAnswer"
    
    payload = {
        "query": { "text": query_text },
        "relatedQuestionsSpec": { "enable": True },
        "answerGenerationSpec": {
            "modelSpec": { "modelVersion": "stable" },
            "includeCitations": True
        }
    }
    
    print(f"\n======================================")
    print(f"Calling streamAnswer with: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=payload, stream=True)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(decoded_line)

if __name__ == "__main__":
    test_stream_answer("what is the metaverse?")
    test_stream_answer("what is the multiverse?")
