"""Test Firestore agent with millennials query."""
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROJECT_NUM = "984359513632"
LOCATION = "us-central1"
RESOURCE_NAME = "81966942583259136"

creds = service_account.Credentials.from_service_account_file(
    "/secrets/sa-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(Request())

headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}:query"

payload = {
    "input": {
        "query": "bring me all the statistics for milenial gen?"
    }
}

print("Testing agent with millennials query...")
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

if r.status_code == 200:
    result = r.json()
    print("\n=== RESPONSE ===")
    print(json.dumps(result, indent=2))
else:
    print(f"Error {r.status_code}: {r.text}")
