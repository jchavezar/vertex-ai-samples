import subprocess
import requests
import json
import sys

token_cmd = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
token = token_cmd.stdout.strip()
PROJECT_NUMBER = "440133963879"
ENGINE_ID = "deloitte-demo" 

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

asst_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants"
resp = requests.get(asst_url, headers=headers)
asst_name = resp.json().get('assistants', [{}])[0].get('name')

url = f"https://discoveryengine.googleapis.com/v1alpha/{asst_name}:streamAssist"

data = {
    "query": { "text": "What are the latest sharepoint files?" },
    "toolsSpec": {
        "vertexAiSearchSpec": {
             "dataStoreSpecs": [
                 {"dataStore": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_file"}
             ]
         }
    }
}

response = requests.post(url, headers=headers, json=data)

try:
    for line in response.text.split('\n'):
        if line.strip():
            print(line[:250])
except Exception:
    print(response.text)

