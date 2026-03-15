import requests
import google.auth
from google.auth.transport.requests import Request
import json

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
if not credentials.valid:
    credentials.refresh(Request())
token = credentials.token

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:streamAnswer"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}
payload = {
    "query": { "text": "What are the features of Vertex AI?" },
    "userPseudoId": "admin@example.com",
    "answerGenerationSpec": {
        "modelSpec": { "modelVersion": "stable" },
        "includeCitations": True
    }
}
resp = requests.post(url, headers=headers, json=payload, stream=True)
print("STATUS", resp.status_code)
for line in resp.iter_lines():
    print("LINE:", line.decode('utf-8'))

