import os
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

# Configuration
PROJECT_NUMBER = "440133963879"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

def get_token():
    credentials, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = Request()
    credentials.refresh(auth_req)
    return credentials.token

def test_diag(query):
    token = get_token()
    # Testing v1beta streamAnswer with aggressive settings to force an answer
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_config:streamAnswer"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    
    payload = {
        "query": {"text": query},
        "answerGenerationSpec": {
            "includeCitations": True,
            "ignoreLowRelevantContent": False,
            "ignoreNonAnswerSeekingQuery": False
        }
    }
    
    print(f"Calling: {url}")
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return

    for line in response.iter_lines():
        if line:
            print(f"Raw line: {line.decode('utf-8')[:100]}...")
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                print(f"Packet: {decoded[6:]}")
            elif decoded.strip():
                try:
                    # Try to parse if it's raw JSON (not SSE)
                    print(f"Attempting non-SSE JSON parse: {json.loads(decoded)}")
                except:
                    pass

def test_assist(query):
    token = get_token()
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    payload = {"query": {"text": query}}
    print(f"\n--- Testing Assist: {query} ---")
    response = requests.post(url, headers=headers, json=payload, stream=True)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return
    for line in response.iter_lines():
        if line:
            print(f"Assist Packet: {line.decode('utf-8')[:100]}")

if __name__ == "__main__":
    test_diag("tell me about deloitte")
    test_assist("tell me about deloitte")
