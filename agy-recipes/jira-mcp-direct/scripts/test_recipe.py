# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "httpx",
#     "requests",
# ]
# ///
"""
E2E verification and testing script for Jira MCP Direct recipe.
Sends a test query using streamAssist against both registered datastores.
"""
import os
import sys
import json
from pathlib import Path
import httpx
import google.auth
import google.auth.transport.requests

_HERE = Path(__file__).resolve().parent
RESOURCE_FILE = _HERE.parent / "last_setup_resources.json"

# Load local .env if available
_env_path = _HERE.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GCLOUD_ACCOUNT = os.environ.get("GCLOUD_ACCOUNT", "")

def _gcp_token():
    if GCLOUD_ACCOUNT:
        import subprocess
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token", "--account", GCLOUD_ACCOUNT],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token

def get_headers():
    return {
        "Authorization": f"Bearer {_gcp_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

def build_payload(project_number, location, datastore_id, question):
    ds_path = f"projects/{project_number}/locations/{location}/collections/default_collection/dataStores/{datastore_id}_mcp_data"
    return {
        "query": {"parts": [{"text": question}]},
        "answerGenerationMode": "NORMAL",
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": ds_path}]
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        },
        "languageCode": "en-US",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }

def run_test_for_datastore(project_number, location, engine_id, datastore_id, label):
    print(f"\n----------------------------------------------------")
    print(f"  Testing E2E for {label} ({datastore_id}_mcp_data)")
    print(f"----------------------------------------------------")
    
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project_number}/locations/{location}/"
        f"collections/default_collection/engines/{engine_id}/"
        f"assistants/default_assistant:streamAssist"
    )
    
    payload = build_payload(project_number, location, datastore_id, "list 3 jira issues")
    
    try:
        resp = httpx.post(url, headers=get_headers(), json=payload, timeout=60.0)
    except Exception as exc:
        print(f"[!] Network error: {exc}")
        return False

    if resp.status_code >= 400:
        print(f"[!] HTTP Error {resp.status_code}: {resp.text[:800]}")
        return False

    try:
        chunks = resp.json()
    except Exception as exc:
        print(f"[!] Failed to parse JSON response: {exc}")
        print(f"    Raw Response: {resp.text[:400]}")
        return False

    # Standardize to list
    if not isinstance(chunks, list):
        chunks = [chunks]

    answer_parts = []
    has_auth_error = False
    
    for chunk in chunks:
        ans = chunk.get("answer", {})
        for reply in ans.get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text") or ""
            is_thought = content.get("thought", False)
            if text and not is_thought:
                answer_parts.append(text)
                
            # Check for generic "unable to connect" or OAuth error indicators
            if "unable to" in text.lower() or "authorize" in text.lower() or "sign in" in text.lower():
                has_auth_error = True

    final_answer = "".join(answer_parts).strip()
    print(f"[*] Response:\n{final_answer}")
    
    if has_auth_error or not final_answer:
        print(f"[!] WARNING: The response suggests Atlassian OAuth consent is missing or incomplete.")
        print(f"    Please complete the 'Re-authenticate' flow in the Google Cloud Console for datastore '{datastore_id}'.")
        return False

    print(f"[+] E2E Success: Grounded response received.")
    return True

def main():
    if not RESOURCE_FILE.exists():
        print(f"[!] ERROR: Tracker file {RESOURCE_FILE} not found. Run setup.py first.")
        sys.exit(1)

    with open(RESOURCE_FILE, "r") as f:
        resources = json.load(f)

    project_number = resources.get("project_number")
    location = resources.get("location")
    engine_id = resources.get("engine_id")
    rovo_ds = resources.get("datastore_rovo_id")
    custom_ds = resources.get("datastore_custom_id")

    success = True
    if rovo_ds:
        ok = run_test_for_datastore(project_number, location, engine_id, rovo_ds, "Atlassian Hosted Rovo MCP")
        if not ok:
            success = False
            
    if custom_ds:
        ok = run_test_for_datastore(project_number, location, engine_id, custom_ds, "Custom Cloud Run MCP")
        if not ok:
            success = False

    if not success:
        print("\n[!] One or more E2E tests failed or returned unauthorized responses.")
        sys.exit(1)

    print("\n[+] All E2E tests completed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    main()
