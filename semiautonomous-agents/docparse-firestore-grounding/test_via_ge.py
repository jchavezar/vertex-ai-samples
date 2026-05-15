"""Test via Gemini Enterprise streamAssist (how GE actually invokes agents)."""
import json
import requests
import subprocess

PROJECT = "984359513632"
ENGINE = "acc_1776970890534"
AGENT_ID = "5335208462042747635"

token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT}/locations/global/collections/default_collection/engines/{ENGINE}:streamAssist"

payload = {
    "query": {"parts": [{"text": "bring me all the statistics for milenial gen?"}]},
    "toolsSpec": {
        "assistantAgentIds": [AGENT_ID]
    },
    "assistSkippingMode": "ASSISTANTS_ASSIST_SKIPPING_MODE_UNSPECIFIED"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-goog-user-project": "sharepoint-wif"
}

print("Querying via GE streamAssist...")
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)

if r.status_code == 200:
    result = r.json()
    print("\n=== RESPONSE ===")
    print(json.dumps(result, indent=2))
else:
    print(f"Error {r.status_code}: {r.text}")
