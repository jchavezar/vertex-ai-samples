import time
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

base = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023/assistants/default_assistant"

payload_wf = {
    "query": {"text": "Start the workflow: Miami-Dade"},
    "agentsSpec": {"agentSpecs": [{"agentId": "9292006299939784738"}]},
}
r_wf = requests.post(f"{base}:streamAssist", headers=headers, json=payload_wf)
print("Workflow raw response:\n", r_wf.text[:2500])
