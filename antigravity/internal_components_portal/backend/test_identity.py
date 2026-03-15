import requests
import json
import os
import google.auth
from google.auth.transport.requests import Request

def get_gcp_token():
    credentials, _ = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:streamAnswer"
headers = {
    "Authorization": f"Bearer {get_gcp_token()}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

payload = {
    "query": { "text": "What is Enterprise Shield?" },
    "answerGenerationSpec": {
        "modelSpec": { "modelVersion": "stable" },
        "includeCitations": True,
        "ignoreNonAnswerSeekingQuery": False,
        "ignoreLowRelevantContent": False,
        "ignoreAdversarialQuery": True
    }
}

resp = requests.post(url, headers=headers, json=payload, stream=True)
for line in resp.iter_lines():
    if line:
        text = line.decode('utf-8')
        print(text)

