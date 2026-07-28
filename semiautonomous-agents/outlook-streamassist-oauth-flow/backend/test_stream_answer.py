import os
import subprocess
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
ENGINE_ID = os.environ["ENGINE_ID"]
BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
STREAM_ANSWER_URL = f"{BASE}/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:streamAnswer"

# Use ADC fallback token
token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

# Fetch datastore specs from the connector to match main.py
CONNECTOR_ID = os.environ["CONNECTOR_ID"]
CONNECTOR_URL = f"{BASE}/{CONNECTOR_ID}"
DATASTORE_SPECS = []
try:
    resp = requests.get(f"{CONNECTOR_URL}/dataConnector", headers=headers, timeout=10)
    if resp.ok:
        for entity in resp.json().get("entities", []):
            ds = entity.get("dataStore")
            if ds:
                DATASTORE_SPECS.append({"dataStore": ds})
except Exception as e:
    print("Could not load datastore specs:", e)

print(f"Loaded {len(DATASTORE_SPECS)} datastore specs.")

query = "what was my last email?"
payload = {
    "query": {"text": query},
    "answerGenerationSpec": {
        "ignoreAdversarialQuery": True,
        "ignoreNonAnswerSeekingQuery": False,
        "ignoreLowRelevantContent": False,
    },
    "session": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/sessions/-"
}

if DATASTORE_SPECS:
    payload["searchSpec"] = {"searchParams": {"dataStoreSpecs": DATASTORE_SPECS}}

print("Payload:")
print(json.dumps(payload, indent=2))

print("\nExecuting POST to streamAnswer...")
start = time.time()
resp = requests.post(STREAM_ANSWER_URL, headers=headers, json=payload, timeout=60)
elapsed = round((time.time() - start) * 1000)
print(f"Status Code: {resp.status_code} ({elapsed}ms)")

if resp.ok:
    try:
        data = resp.json()
        print("\nParsed JSON Response:")
        print(json.dumps(data, indent=2))
    except:
        print("\nRaw Text Response:")
        print(resp.text[:5000])
else:
    print(resp.text)
