import google.auth
import google.auth.transport.requests
import requests
import json
import os
import vertexai
from vertexai import agent_engines
import inspect

# Check SDK method signature
try:
    print("Delete Signature:", inspect.signature(agent_engines.delete))
except Exception as e:
    print("Could not get delete signature", e)

creds, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)

url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/vtxdemos/locations/us-central1/reasoningEngines"
headers = {"Authorization": f"Bearer {creds.token}"}
resp = requests.get(url, headers=headers)
data = resp.json()
engines = data.get("reasoningEngines", [])

print("REST Engine count:", len(engines))
for e in engines:
    if "veo" in e.get("displayName", "").lower():
        print(f"REST Found: {e.get('displayName')} - {e.get('name')}")

# Try SDK again
try:
    vertexai.init(project="vtxdemos", location="us-central1")
    sdk_agents = agent_engines.list()
    sdk_agents_list = list(sdk_agents)
    print("SDK Engine count:", len(sdk_agents_list))
    for a in sdk_agents_list:
        if "veo" in a.display_name.lower():
            print(f"SDK Found: {a.display_name} - {a.resource_name}")
except Exception as e:
    print("SDK Error:", e)

