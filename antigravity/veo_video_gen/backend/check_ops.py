import google.auth
import google.auth.transport.requests
import requests
import os

creds, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)

location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/operations"
headers = {"Authorization": f"Bearer {creds.token}"}

resp = requests.get(url, headers=headers)
if resp.ok:
    data = resp.json().get('operations', [])
    for op in data[:2]:
        print(f"Operation: {op.get('name')}")
        print(f"Metadata: {op.get('metadata')}")
        print("---")
else:
    print(f"Error: {resp.text}")
