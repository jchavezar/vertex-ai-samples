"""Test newly deployed Firestore agent."""
import json
import requests
import subprocess

PROJECT_NUM = "984359513632"
LOCATION = "us-central1"
RESOURCE_NAME = "5488960507706605568"

token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_NUM}/locations/{LOCATION}/reasoningEngines/{RESOURCE_NAME}:query"

# Test both queries
for test_query in ["what is the metaverse?", "bring me all the statistics for milenial gen?"]:
    print(f"\n{'='*80}")
    print(f"Testing: {test_query}")
    print('='*80)

    payload = {"input": {"query": test_query}}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

    if r.status_code == 200:
        result = r.json()
        output = result.get("output", "")
        print(f"✓ SUCCESS")
        print(f"Response: {output[:400]}...")
    else:
        print(f"✗ FAILED: {r.status_code}")
        error_msg = r.json().get("error", {}).get("message", r.text)
        print(f"Error: {error_msg[:300]}")
