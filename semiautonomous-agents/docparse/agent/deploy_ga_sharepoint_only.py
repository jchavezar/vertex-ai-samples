"""Deploy GA agent to sharepoint-wif Agent Engine (same project as GE)."""
import os
from pathlib import Path
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-central1"
# Corpus can be cross-project for retrieval (allowed)
CORPUS = os.environ.get("RAG_CORPUS_NAME", "projects/254356041555/locations/us-central1/ragCorpora/8338977660029894656")

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "RAG_CORPUS_NAME": CORPUS,
    "AGENT_MODEL": "gemini-2.5-flash",
    "AGENT_TOP_K": "20",
}

def deploy():
    print(f"\n=== Deploying GA agent to {PROJECT_ID} ===")
    print(f"Corpus: {CORPUS} (cross-project retrieval OK)")
    
    # Create staging bucket if needed
    import subprocess
    bucket = f"gs://{PROJECT_ID}-agent-staging"
    r = subprocess.run(
        ["gcloud", "storage", "buckets", "describe", bucket, "--project", PROJECT_ID],
        capture_output=True)
    if r.returncode != 0:
        print(f"Creating {bucket}...")
        subprocess.run(
            ["gcloud", "storage", "buckets", "create", bucket,
             "--project", PROJECT_ID, "--location", LOCATION,
             "--uniform-bucket-level-access"], check=True)
    
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=bucket)
    from docparse_agent.agent_ga import root_agent
    
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    
    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-ga-agent",
        description="GA gemini-2.5-flash, 90.5% composite, same-project deployment",
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["docparse_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )
    
    print(f"\n=== Deployed ===")
    print(f"Resource: {remote.resource_name}")
    print(f"Project: {PROJECT_ID} (same as GE)")
    
    # Auto-register in GE
    print(f"\n=== Auto-registering in GE ===")
    import json, requests
    
    def _token():
        return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/984359513632/locations/global/collections/default_collection/"
        f"engines/acc_1776970890534/assistants/default_assistant/agents"
    )
    
    payload = {
        "displayName": "docparse GA (same-project)",
        "description": "GA gemini-2.5-flash, 90.5% composite. Agent Engine in sharepoint-wif (no cross-project).",
        "icon": {"uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/find_in_page/default/24px.svg"},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": "Use for document questions. Full GA stack."},
            "provisioned_reasoning_engine": {"reasoning_engine": remote.resource_name},
        },
    }
    
    headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json", "x-goog-user-project": PROJECT_ID}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if r.status_code == 200:
        res = r.json()
        agent_name = res["name"]
        print(f"✅ Registered: {res.get('displayName')}")
        
        # Share ALL_USERS
        share_url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
        share_payload = {"sharingConfig": {"scope": "ALL_USERS"}}
        r2 = requests.patch(share_url, headers=headers, data=json.dumps(share_payload))
        if r2.status_code == 200:
            print(f"   Shared: ALL_USERS")
    else:
        print(f"Registration failed ({r.status_code}): {r.text[:200]}")
    
    return remote

if __name__ == "__main__":
    deploy()
