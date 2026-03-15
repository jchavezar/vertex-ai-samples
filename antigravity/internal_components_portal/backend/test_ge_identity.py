import requests
import json
import google.auth
from google.auth.transport.requests import Request
import os

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

try:
    credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not credentials.valid:
        credentials.refresh(Request())
    token = credentials.token
except Exception as e:
    print(f"Auth error: {e}")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

# 1. Fetch data store specs
ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
ds_resp = requests.get(ds_url, headers=headers)
print("Widget response code:", ds_resp.status_code)

collections = ds_resp.json().get('collectionComponents', [{}])
dataStoreSpecs = [
    {'dataStore': r['name']}
    for r in collections[0].get('dataStoreComponents', [])
]

print("Fetched DataStores:", dataStoreSpecs)

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

payload = {
    "query": { "text": "What is the salary of a cfo?" },
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": dataStoreSpecs
        }
    }
}

print(f"\n--- Testing toolsSpec ---")
response = requests.post(url, headers=headers, json=payload, stream=True)
print("STATUS CODE:", response.status_code)
if response.status_code != 200:
    try:
         print("ERROR:", response.json())
    except:
         print("ERROR:", response.text)
else:
    print("SUCCESS! Output:")
    for chunk in response.iter_content(chunk_size=2048):
        if chunk:
            print(chunk.decode('utf-8'))


