import os
import urllib.request
import json
import base64

token = os.popen('gcloud auth print-access-token').read().strip()
project = 'vtxdemos'

url = f'https://discoveryengine.googleapis.com/v1alpha/projects/vtxdemos/locations/global/collections/default_collection/engines/agent-fdf659e9-c334-4ef2-bead-71eef3a395c3-chat-engine/agents'
try:
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'x-goog-user-project': project
    })
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Agents for chat engine:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error v1alpha chat agents: {e}")
