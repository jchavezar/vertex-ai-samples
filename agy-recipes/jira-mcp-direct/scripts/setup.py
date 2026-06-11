# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "requests",
# ]
# ///
"""
Setup script for Atlassian Jira MCP Direct integration recipe.
Deploys the custom MCP server to Cloud Run, registers both MCP datastores in GE,
and records details to last_setup_resources.json for teardown.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
import requests
import google.auth
import google.auth.transport.requests

# 1. Load local .env if available
_HERE = Path(__file__).resolve().parent
_env_path = _HERE.parent / ".env"
if _env_path.exists():
    print(f"[*] Loading environment variables from {_env_path}")
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
GE_LOCATION = os.environ.get("GE_LOCATION", "global")

ATLASSIAN_CLIENT_ID = os.environ.get("ATLASSIAN_CLIENT_ID", "")
ATLASSIAN_CLIENT_SECRET = os.environ.get("ATLASSIAN_CLIENT_SECRET", "")

RESOURCE_FILE = _HERE.parent / "last_setup_resources.json"

def get_gcp_headers():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID
    }

def register_mcp_datastore(datastore_id: str, display_name: str, dc_payload: dict):
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}:setUpDataConnector"
    )
    payload = {
        "collectionId": datastore_id,
        "collectionDisplayName": display_name,
        "dataConnector": dc_payload
    }
    print(f"[*] Registering datastore {datastore_id}...")
    resp = requests.post(url, headers=get_gcp_headers(), json=payload, timeout=60)
    if resp.status_code not in (200, 201):
        # Try V2
        from urllib.parse import urlencode
        qs = urlencode({
            "collectionId": datastore_id,
            "collectionDisplayName": display_name,
        })
        v2_url = (
            f"https://discoveryengine.googleapis.com/v1alpha/"
            f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}:setUpDataConnectorV2?{qs}"
        )
        resp = requests.post(v2_url, headers=get_gcp_headers(), json=dc_payload, timeout=60)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to register datastore: {resp.text}")
    
    # Wait for entity datastore creation
    print(f"[*] Waiting for entity datastore {datastore_id}_mcp_data...")
    entity_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}/"
        f"collections/default_collection/dataStores/{datastore_id}_mcp_data"
    )
    for _ in range(40):
        r = requests.get(entity_url, headers=get_gcp_headers(), timeout=30)
        if r.status_code == 200:
            print(f"[+] Datastore {datastore_id}_mcp_data is ready.")
            return
        time.sleep(3)
    raise TimeoutError(f"Datastore {datastore_id}_mcp_data did not become ready.")

def attach_to_engine(datastore_short_ids: list[str]):
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{GE_LOCATION}/"
        f"collections/default_collection/engines/{GE_ENGINE_ID}"
    )
    print(f"[*] Attaching datastores {datastore_short_ids} to engine {GE_ENGINE_ID}...")
    try:
        r = requests.get(url, headers=get_gcp_headers(), timeout=30)
        r.raise_for_status()
        engine_data = r.json()
        current_ids = list(engine_data.get("dataStoreIds", []))
        updated_ids = list(set(current_ids + datastore_short_ids))
        
        patch_url = f"{url}?updateMask=dataStoreIds"
        r_patch = requests.patch(patch_url, headers=get_gcp_headers(), json={"dataStoreIds": updated_ids}, timeout=30)
        if r_patch.status_code == 200:
            print("[+] Engine updated successfully.")
        else:
            print(f"[!] Engine update failed: {r_patch.text}. Engine may be in single-datastore mode. Swap datastore manually in console if needed.")
    except Exception as e:
        print(f"[!] Engine attachment failed: {e}")

def main():
    print("====================================================")
    print("  Jira MCP Direct Setup Execution")
    print("====================================================")
    print(f"  Project ID:     {GE_PROJECT_ID}")
    print(f"  Project Number: {GE_PROJECT_NUMBER}")
    print(f"  Engine ID:      {GE_ENGINE_ID}")
    print("====================================================")

    if not ATLASSIAN_CLIENT_ID or not ATLASSIAN_CLIENT_SECRET:
        print("[!] ERROR: ATLASSIAN_CLIENT_ID / ATLASSIAN_CLIENT_SECRET environment variables must be set.")
        print("    Create a .env file under agy-recipes/jira-mcp-direct/ containing standard Jira App Client details.")
        sys.exit(1)

    resources = {
        "project_id": GE_PROJECT_ID,
        "project_number": GE_PROJECT_NUMBER,
        "engine_id": GE_ENGINE_ID,
        "location": GE_LOCATION,
        "cloud_run_service": "jira-mcp-server-recipe",
        "cloud_run_region": "us-central1",
        "datastore_rovo_id": "jiramcp-rovo-recipe",
        "datastore_custom_id": "jiramcp-custom-recipe",
    }

    try:
        # 1. Deploy custom MCP Server to Cloud Run
        print("[*] Step 1: Deploying Custom MCP Server to Cloud Run...")
        mcp_server_dir = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "semiautonomous-agents"
            / "atlassian-jira-integration"
            / "option-a-custom-mcp-portal"
            / "jira_server"
        )
        
        deploy_cmd = [
            "gcloud", "run", "deploy", resources["cloud_run_service"],
            "--source", str(mcp_server_dir),
            "--region", resources["cloud_run_region"],
            "--project", GE_PROJECT_ID,
            "--allow-unauthenticated",
            "--quiet"
        ]
        print(f"[*] Running: {' '.join(deploy_cmd)}")
        res = subprocess.run(deploy_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Cloud Run deploy failed: {res.stderr}")
        
        # Get custom MCP service URL
        url_cmd = [
            "gcloud", "run", "services", "describe", resources["cloud_run_service"],
            "--region", resources["cloud_run_region"],
            "--project", GE_PROJECT_ID,
            "--format", "value(status.url)"
        ]
        url_res = subprocess.run(url_cmd, capture_output=True, text=True)
        if url_res.returncode != 0:
            raise RuntimeError(f"Failed to get Cloud Run service URL: {url_res.stderr}")
        
        custom_mcp_url = url_res.stdout.strip()
        resources["cloud_run_url"] = custom_mcp_url
        print(f"[+] Custom MCP Server deployed successfully: {custom_mcp_url}")

        # 2. Dynamic Client Registration (DCR) for Atlassian Hosted (Rovo)
        print("[*] Step 2: Registering DCR Client with Atlassian Hosted Rovo MCP...")
        dcr_file = Path(os.path.expanduser("~/.secrets/atlassian-rovo-dcr-ge.json"))
        if dcr_file.exists():
            print(f"[*] Reusing existing DCR credentials at {dcr_file}")
            dcr_data = json.loads(dcr_file.read_text())
        else:
            dcr_body = {
                "client_name": "gemini-enterprise-jira-testing-recipe",
                "redirect_uris": ["https://vertexaisearch.cloud.google.com/oauth-redirect"],
                "token_endpoint_auth_method": "client_secret_basic",
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
            }
            resp = requests.post("https://cf.mcp.atlassian.com/v1/register", json=dcr_body, timeout=30)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"DCR registration failed ({resp.status_code}): {resp.text}")
            dcr_data = resp.json()
            dcr_file.parent.mkdir(parents=True, exist_ok=True)
            dcr_file.write_text(json.dumps(dcr_data, indent=2))
            dcr_file.chmod(0o600)
            print(f"[+] DCR credentials saved to {dcr_file}")
        
        rovo_client_id = dcr_data["client_id"]
        rovo_client_secret = dcr_data["client_secret"]

        # 3. Register Rovo datastore in GE
        print("[*] Step 3: Registering Atlassian Rovo Hosted MCP datastore in Gemini Enterprise...")
        rovo_dc_payload = {
            "dataSource": "custom_mcp",
            "params": {"oauth_access_token": "placeholder-real-auth-via-3LO"},
            "connectorModes": ["ACTIONS", "FEDERATED"],
            "bapConfig": {"supportedConnectorModes": ["ACTIONS"]},
            "entities": [{"entityName": "mcp_data"}],
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": True,
                "actionParams": {
                    "instance_uri": "https://mcp.atlassian.com/v1/mcp",
                    "auth_type": "OAUTH",
                    "auth_uri": "https://mcp.atlassian.com/v1/authorize",
                    "token_uri": "https://cf.mcp.atlassian.com/v1/token",
                    "scopes": "read:jira-work write:jira-work read:jira-user read:confluence-content.all read:confluence-space.summary read:me offline_access",
                    "client_id": rovo_client_id,
                    "client_secret": rovo_client_secret,
                    "mcp_server_source": "BYO_MCP",
                    "registry_mcp_server_name": "",
                    "mcp_server_description": "Atlassian Rovo Hosted MCP connector.",
                    "mcp_agent_instructions": (
                        "When user asks about Jira issues, tickets, bugs or projects, "
                        "call searchJiraIssuesUsingJql or getJiraIssue. Format results "
                        "as a markdown table with columns: Key, Summary, Status, Assignee."
                    )
                }
            }
        }
        register_mcp_datastore(resources["datastore_rovo_id"], "Jira MCP (Atlassian Rovo Recipe)", rovo_dc_payload)

        # 4. Register Custom MCP datastore in GE
        print("[*] Step 4: Registering Custom MCP datastore in Gemini Enterprise...")
        custom_dc_payload = {
            "dataSource": "custom_mcp",
            "params": {"oauth_access_token": "placeholder-real-auth-via-3LO"},
            "connectorModes": ["ACTIONS", "FEDERATED"],
            "bapConfig": {"supportedConnectorModes": ["ACTIONS"]},
            "entities": [{"entityName": "mcp_data"}],
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": True,
                "actionParams": {
                    "instance_uri": f"{custom_mcp_url}/mcp",
                    "auth_type": "OAUTH",
                    "auth_uri": "https://auth.atlassian.com/authorize",
                    "token_uri": "https://auth.atlassian.com/oauth/token",
                    "scopes": "read:jira-work write:jira-work read:jira-user offline_access",
                    "client_id": ATLASSIAN_CLIENT_ID,
                    "client_secret": ATLASSIAN_CLIENT_SECRET,
                    "mcp_server_source": "BYO_MCP",
                    "registry_mcp_server_name": "",
                    "mcp_server_description": "Custom Jira MCP server deployed on Cloud Run.",
                    "mcp_agent_instructions": (
                        "When user asks about Jira issues, tickets, bugs or projects, "
                        "call searchJiraIssuesUsingJql or getJiraIssue. Format results "
                        "as a markdown table with columns: Key, Summary, Status, Assignee."
                    )
                }
            }
        }
        register_mcp_datastore(resources["datastore_custom_id"], "Jira MCP (Custom Cloud Run Recipe)", custom_dc_payload)

        # 5. Attach both datastores to the Engine
        print("[*] Step 5: Attaching datastores to Gemini Enterprise Engine...")
        attach_to_engine([f"{resources['datastore_rovo_id']}_mcp_data", f"{resources['datastore_custom_id']}_mcp_data"])

        # Save resource details
        with open(RESOURCE_FILE, "w") as f:
            json.dump(resources, f, indent=2)
        print(f"[+] Resource details saved to {RESOURCE_FILE}")
        print("====================================================")
        print("  Setup complete! Next steps:")
        print("  1. Open the GE Console -> Data Stores.")
        print(f"  2. Select '{resources['datastore_rovo_id']}_mcp_data' -> Actions -> Reload custom actions -> Enable tools -> Re-authenticate (using dynamic client credentials).")
        print(f"  3. Select '{resources['datastore_custom_id']}_mcp_data' -> Actions -> Reload custom actions -> Enable tools -> Re-authenticate (using standard OAuth credentials).")
        print("  4. Once both show ACTIVE, execute e2e tests:")
        print("     uv run scripts/test_recipe.py")
        print("====================================================")

    except Exception as e:
        print(f"[!] ERROR: Setup failed: {e}")
        # Save what was created for clean teardown
        with open(RESOURCE_FILE, "w") as f:
            json.dump(resources, f, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    main()
