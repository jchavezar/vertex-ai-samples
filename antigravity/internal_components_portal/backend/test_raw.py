import requests, json
import google.auth
from google.auth.transport.requests import Request

creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
if not creds.valid:
    creds.refresh(Request())
token = creds.token

PROJECT_NUMBER = "440133963879"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {
  "query": { "text": "what is jennifer walsh compensation" },
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {"dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/deloitte-sharepoint_attachment"},
        {"dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/deloitte-sharepoint_comment"},
        {"dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/deloitte-sharepoint_event"}
      ]
    }
  }
}

with requests.post(url, headers=headers, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode('utf-8'))
