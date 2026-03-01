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

payload = {
    "query": { "text": "salary of Michael James Thornton" }
}

print(f"Testing URL: {URL}")

response = requests.post(URL, headers=headers, json=payload, stream=True)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            decoded = line.decode()
            try:
                # The response can be a list of objects or a single object
                if decoded.startswith("["):
                    parsed = json.loads(decoded)
                    # Discovery Engine often returns a list of objects in one chunk
                    for item in parsed:
                        print(f"Packet: {json.dumps(item, indent=2)}")
                else:
                    print(f"Packet: {decoded}")
            except Exception as e:
                print(f"Raw Packet: {decoded}")
else:
    print(f"Error: {response.text}")
