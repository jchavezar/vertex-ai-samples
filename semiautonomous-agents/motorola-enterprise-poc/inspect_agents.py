import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

creds, _ = default()
creds.refresh(Request())
headers = {
    "Authorization": f"Bearer {creds.token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": "vtxdemos",
}

base = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023/assistants/default_assistant/agents"

print("=== BASIC AGENT JSON (8517176328388284078) ===")
r1 = requests.get(f"{base}/8517176328388284078", headers=headers)
print(json.dumps(r1.json(), indent=2)[:2000])

print("\n=== WORKFLOW AGENT JSON (9292006299939784738) ===")
r2 = requests.get(f"{base}/9292006299939784738", headers=headers)
print(json.dumps(r2.json(), indent=2)[:2000])
