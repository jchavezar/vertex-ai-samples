"""Register the GA agent in sharepoint-wif Gemini Enterprise."""
import json, subprocess, sys

GE_PROJECT_ID = "sharepoint-wif"
GE_PROJECT_NUMBER = "984359513632"
AS_APP = "acc_1776970890534"
REASONING_ENGINE_RES = "projects/254356041555/locations/us-central1/reasoningEngines/8912734163484803072"

def _token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()

url = (
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{GE_PROJECT_NUMBER}/locations/global/collections/default_collection/"
    f"engines/{AS_APP}/assistants/default_assistant/agents"
)

payload = {
    "displayName": "docparse GA agent",
    "description": "Full GA stack: gemini-2.5 extraction + gemini-2.5-flash answering. 90.5% composite on 298 questions.",
    "icon": {"uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/find_in_page/default/24px.svg"},
    "adk_agent_definition": {
        "tool_settings": {"tool_description": "Use for questions about the documents. GA-compatible."},
        "provisioned_reasoning_engine": {"reasoning_engine": REASONING_ENGINE_RES},
    },
}

import requests
headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json", "x-goog-user-project": GE_PROJECT_ID}
r = requests.post(url, headers=headers, data=json.dumps(payload))

if r.status_code == 200:
    res = r.json()
    print(f"✅ Registered: {res.get('name')}")
    print(f"   Display: {res.get('displayName')}")
    
    # Share with ALL_USERS
    agent_name = res["name"]
    share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    share_payload = {"sharingConfig": {"scope": "ALL_USERS"}}
    r2 = requests.patch(share_url, headers=headers, data=json.dumps(share_payload))
    if r2.status_code == 200:
        print(f"   Shared: ALL_USERS")
else:
    print(f"❌ Failed ({r.status_code}): {r.text[:500]}")
    sys.exit(1)
