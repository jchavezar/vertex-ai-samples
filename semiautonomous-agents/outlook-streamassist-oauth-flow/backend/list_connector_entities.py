import os
import subprocess
import requests
import json
from dotenv import load_dotenv

load_dotenv()

PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
CONNECTOR_ID = "outlook-connector_1784199575073"
BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections"
CONNECTOR_URL = f"{BASE}/{CONNECTOR_ID}"

try:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    resp = requests.get(f"{CONNECTOR_URL}/dataConnector", headers=headers, timeout=10)
    print("Status Code:", resp.status_code)
    if resp.ok:
        data = resp.json()
        print(json.dumps(data, indent=2))
    else:
        print(resp.text)
except Exception as e:
    print("Error:", e)
