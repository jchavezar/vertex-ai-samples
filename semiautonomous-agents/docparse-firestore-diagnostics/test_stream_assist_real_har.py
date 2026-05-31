import google.auth
import google.auth.transport.requests
import requests
import json

def test_stream_assist_real(query_text):
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
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/{assistant_id}:streamAssist"
    
    # Matching HAR request exactly
    body = {
        "query": {
            "parts": [
                {
                    "text": query_text
                }
            ]
        },
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {},
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {}
        },
        "assistSkippingMode": "REQUEST_ASSIST",
        "languageCode": "en-US",
        "userMetadata": {
            "timeZone": "America/New_York"
        }
    }
    
    print(f"\n======================================")
    print(f"Calling v1alpha streamAssist with exact HAR body for: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body, stream=True)
    print(f"Response Status: {r.status_code}")
    if r.status_code == 200:
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
    else:
        print(r.text)

if __name__ == "__main__":
    test_stream_assist_real("what is the metaverse")
