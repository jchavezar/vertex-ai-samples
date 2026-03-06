import subprocess
import requests
import json
import sys

# Get token
token_cmd = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
token = token_cmd.stdout.strip()

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
ENGINE_ID = "deloitte-demo" 
DATA_STORE_ID = "5817ee80-82a4-49e3-a19c-2cedc73a6300"
DATA_STORE_NAME = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Get assistant
assistants_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants"
print(f"GET {assistants_url}")
resp = requests.get(assistants_url, headers=headers)
if not resp.ok:
    print("Failed to get assistants", resp.text)
    sys.exit(1)

asst_name = resp.json().get('assistants', [{}])[0].get('name')
if not asst_name:
    print("No assistant found")
    sys.exit(1)

print(f"Found assistant: {asst_name}")

url = f"https://discoveryengine.googleapis.com/v1alpha/{asst_name}:streamAssist"

data = {
    "query": {
        "text": "What are the latest documents?",
    },
    "toolsSpec": {
        "vertexAiSearchSpec": {
             "dataStoreSpecs": [{"dataStore": DATA_STORE_NAME}]
         }
    }
}

print(f"POSTing to {url}")
response = requests.post(url, headers=headers, json=data)

try:
    for line in response.text.split('\n'):
        if line.strip():
            print(line[:250])
except Exception:
    print(response.text)

