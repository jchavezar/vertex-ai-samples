"""Test RAG agent using SA credentials."""
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROJECT_NUM = "984359513632"
LOCATION = "us-west1"
RESOURCE_NAME = "6921478473408053248"

creds = service_account.Credentials.from_service_account_file(
    "/secrets/sa-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(Request())

headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}:query"

# Test both queries
for test_query in ["what is the metaverse?", "bring me all the statistics for milenial gen?"]:
    print(f"\nTesting: {test_query}")
    print('='*80)

    payload = {"input": {"query": test_query}}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

    if r.status_code == 200:
        result = r.json()
        output = result.get("output", "")
        print(f"✓ Status {r.status_code}")
        print(f"Response preview: {str(output)[:500]}...")
    else:
        print(f"✗ Status {r.status_code}")
        print(f"Error: {r.text[:400]}")
    print()
