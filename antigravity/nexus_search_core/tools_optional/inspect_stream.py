import requests
import json

# Constants
TOKEN = "YOUR_TOKEN_HERE"
URL = "https://discoveryengine.googleapis.com/v1alpha/projects/440133963879/locations/global/collections/default_collection/engines/deloitte-demo/assistants/default_assistant:streamAssist"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

p = { "query": { "text": "what is the salary of a COO?" } }
response = requests.post(URL, headers=headers, json=p, stream=True)
print(f"Status: {response.status_code}")
content = ""
for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        content += chunk.decode('utf-8')
        if "}" in content: # Just get the first object
            break
print(f"CONTENT: {content[:1000]}")
