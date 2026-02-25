import os
import requests
import json
import google.auth
import google.auth.transport.requests

PROJECT_NUMBER = "254356041555"
ENGINE_ID = "agentspace-testing_1748446185255"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token

url_stream = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
    
payload = {
    "query": {"text": "What is the main topic of the documents?"},
    "session": "-",
    # Let's see if we can pass answerGenerationSpec to StreamAssist
    "answerGenerationSpec": {
        "ignoreLowRelevantContent": False
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

response = requests.post(url_stream, json=payload, headers=headers)
print(response.status_code)
if response.status_code != 200:
    print(response.text)
