#!/usr/bin/env bash
# Run this in Cloud Shell (authenticated as admin@jesusarguelles.altostrat.com)
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "=== Deploy Firestore agent to vtxdemos Agent Engine ==="
pip install uv --quiet

uv run --with "google-cloud-aiplatform[adk,agent_engines]" \
  --with google-cloud-firestore \
  --with google-genai \
  --with requests \
  python deploy_firestore.py

# Capture the reasoning engine resource name from output
# (it prints "Resource: projects/.../reasoningEngines/...")
# Then auto-register in GE

echo
echo "=== Auto-register in sharepoint-wif GE ==="
echo "Paste the reasoning engine resource name when prompted:"
read -p "Resource: " REASONING_ENGINE_RES

python3 << 'PYEOF'
import json, subprocess, requests, os

REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", input("Resource name: "))
GE_PROJECT_ID = "sharepoint-wif"
GE_PROJECT_NUMBER = "984359513632"
AS_APP = "acc_1776970890534"

token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{AS_APP}/assistants/default_assistant/agents"

payload = {
    "displayName": "docparse Firestore (PDF grounding)",
    "description": "Firestore retrieval + manual PDF-level grounding, text-embedding-005, gemini-2.5-flash",
    "icon": {"uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/find_in_page/default/24px.svg"},
    "adk_agent_definition": {
        "tool_settings": {"tool_description": "Use for document questions. Firestore variant with PDF grounding."},
        "provisioned_reasoning_engine": {"reasoning_engine": REASONING_ENGINE_RES},
    },
}

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "x-goog-user-project": GE_PROJECT_ID}
r = requests.post(url, headers=headers, data=json.dumps(payload))

if r.status_code == 200:
    res = r.json()
    agent_name = res["name"]
    print(f"✅ Registered: {res.get('displayName')}")

    # Share ALL_USERS
    share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    r2 = requests.patch(share_url, headers=headers, data=json.dumps({"sharingConfig": {"scope": "ALL_USERS"}}))
    if r2.status_code == 200:
        print(f"   Shared: ALL_USERS")

    print(f"\n✅ DONE")
    print(f"Agent registered in sharepoint-wif Gemini Enterprise")
    print(f"Test by asking: 'What was the total mentions in 2020 Q1?'")
else:
    print(f"❌ Registration failed ({r.status_code}): {r.text[:200]}")
PYEOF

echo
echo "=== Complete ==="
echo "Open Gemini Enterprise UI and test the 'docparse Firestore (PDF grounding)' agent"
