"""Test the deployed ADK agent."""
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROJECT_NUM = "984359513632"
LOCATION = "us-central1"
RESOURCE_NAME = "2234546826978000896"

creds = service_account.Credentials.from_service_account_file(
    "/secrets/sa-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(Request())

headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}:query"

# Test 1: Metaverse question
print("=== Test 1: What is the metaverse? ===")
payload = {"input": {"query": "what is the metaverse?"}}
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

if r.status_code == 200:
    result = r.json()
    output = result.get("output", {})
    if isinstance(output, dict):
        print(f"Response: {output.get('response', output)[:500]}")
    else:
        print(f"Response: {str(output)[:500]}")
else:
    print(f"Error {r.status_code}: {r.text[:300]}")

print("\n" + "="*80 + "\n")

# Test 2: Millennial statistics
print("=== Test 2: Millennial statistics ===")
payload = {"input": {"query": "bring me all the statistics for milenial gen?"}}
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

if r.status_code == 200:
    result = r.json()
    output = result.get("output", {})
    if isinstance(output, dict):
        print(f"Response: {output.get('response', output)[:800]}")
    else:
        print(f"Response: {str(output)[:800]}")
else:
    print(f"Error {r.status_code}: {r.text[:300]}")
