"""Test both query and stream_query endpoints."""
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
base_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}"

test_query = "what is the metaverse?"

# Test 1: Regular query endpoint
print("1. Testing /query endpoint...")
url = f"{base_url}:query"
payload = {"input": {"query": test_query}}
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    print(f"   ✓ Works: {r.json().get('output', '')[:150]}...")
else:
    print(f"   ✗ Error: {r.text[:200]}")

print("\n2. Testing /streamQuery endpoint...")
url = f"{base_url}:streamQuery"
payload = {"input": {"query": test_query}}
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    print(f"   ✓ Works: {r.text[:150]}...")
else:
    print(f"   ✗ Error: {r.text[:200]}")
