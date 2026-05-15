"""Final test of streaming endpoint."""
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROJECT_NUM = "984359513632"
LOCATION = "us-central1"
RESOURCE_NAME = "6337889037465944064"

creds = service_account.Credentials.from_service_account_file(
    "/secrets/sa-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(Request())

headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}:streamQuery"

# Test metaverse (the one that keeps failing in GE)
payload = {"input": {"query": "what is the metaverse?"}}

print("Testing streamQuery endpoint (what GE uses)...")
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90, stream=True)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    full_response = ""
    for line in r.iter_lines():
        if line:
            full_response += line.decode('utf-8')

    print(f"✓ SUCCESS")
    print(f"Response: {full_response[:500]}...")
else:
    print(f"✗ FAILED")
    print(f"Error: {r.text[:400]}")
