import requests, json
from google.auth import default
from google.auth.transport.requests import Request

creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
if not creds.valid:
    creds.refresh(Request())

url = "https://discoveryengine.googleapis.com/v1alpha/projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/engines/deloitte-demo/assistants/default_assistant:streamAssist"
headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json", "X-Goog-User-Project": "REDACTED_PROJECT_NUMBER"}
dataStoreSpecs = [
    {'dataStore': 'projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_attachment'},
    {'dataStore': 'projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_comment'},
    {'dataStore': 'projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_event'},
    {'dataStore': 'projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_page'},
    {'dataStore': 'projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_file'}
]

payload = {
    "query": {"text": "what is jennifer walsh compensation"},
    "toolsSpec": {"vertexAiSearchSpec": {"dataStoreSpecs": dataStoreSpecs}}
}

r = requests.post(url, headers=headers, json=payload, stream=True)
with open("stream_output_full.json", "w") as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk.decode('utf-8'))
print("Done")
