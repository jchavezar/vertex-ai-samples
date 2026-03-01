import requests
import json
import os
import subprocess

# Get token
def get_token():
    return subprocess.check_output("gcloud auth print-access-token", shell=True).decode().strip()

TOKEN = get_token()
PROJECT_NUMBER = "440133963879"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"
ASSISTANT_ID = "default_assistant"

URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}:streamAssist"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

# Payload with MINIMAL fields to ensure success first
payload = {
    "query": { "text": "salary of Michael James Thornton" }
}

print(f"Testing URL: {URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(URL, headers=headers, json=payload, stream=True)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("Capturing first few packets...")
    for line in response.iter_lines():
        if line:
            print(f"Packet: {line.decode()}")
            break
else:
    print(f"Error: {response.text}")
