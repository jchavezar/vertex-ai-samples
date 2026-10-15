#!/usr/bin/env python3
"""Register and configure the Mike OSS Enterprise Legal Diligence Cockpit (SEP-1865) as a Custom MCP Data Connector (custom_mcp) in Gemini Enterprise.

Features:
1. Automated setUpDataConnector call with BYO_MCP configuration and actionConfig.
2. Dual-mode support for internal gLinux (via stubby RefreshDataConnectorTools) and external environments.
3. Automatic attachment to target Gemini Enterprise engines (lexgraph-legal-spanner-ge, gemini-enterprise-17877637_1787763712023).
4. CLI flag and environment variable overrides for CI/CD and multi-environment portability.
5. Zero-Leak security architecture: No tokens, secrets, or hardcoded keys.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# Default Configuration
DEFAULT_PROJECT_ID = os.environ.get("VERTEX_PROJECT_ID", "vtxdemos")
DEFAULT_PROJECT_NUMBER = os.environ.get("GCP_PROJECT_NUMBER", "254356041555")
DEFAULT_LOCATION = os.environ.get("VERTEX_LOCATION", "global")
DEFAULT_MCP_BASE_URL = os.environ.get(
    "MIKE_SERVICE_URL",
    "https://mike-gcp-platform-254356041555.us-central1.run.app",
)
DEFAULT_INSTANCE_URI = f"{DEFAULT_MCP_BASE_URL}/mcp"
DEFAULT_DATASTORE_ID = "mike-oss-legal-grid-mcp"
DEFAULT_COLLECTION_DISPLAY_NAME = "Mike OSS - Enterprise Legal AI Diligence Cockpit (MCP App)"

DEFAULT_ENGINES = [
    "weil-legal-spanner-ge",
    "gemini-enterprise-17877637_1787763712023",
]

ENABLED_TOOLS = [
    "open_legal_analysis_grid",
    "add_dynamic_grid_column",
    "hybrid_search_legal_graph",
    "traverse_precedent_graph",
    "run_deterministic_redline",
    "analyze_fundgen_and_antitrust",
    "triage_inbox_and_cmn_wall",
]


def get_token() -> str:
    """Retrieves short-lived GCP access token via gcloud CLI without leaking to output."""
    try:
        return subprocess.check_output(
            ["gcloud", "auth", "print-access-token"], text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        sys.exit(f"[FATAL] Failed to retrieve access token via gcloud: {e}")


def api_req(
    method: str,
    url: str,
    body: Optional[Dict[str, Any]] = None,
    project_id: str = DEFAULT_PROJECT_ID,
) -> Tuple[int, Dict[str, Any]]:
    """Executes authenticated REST request against Google Cloud Discovery Engine v1alpha."""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id,
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}
    except Exception as e:
        return 500, {"error": str(e)}


def try_refresh_dynamic_tools_via_stubby(project_number: str, location: str, collection_id: str) -> bool:
    """Attempts to call internal DataConnectorService.RefreshDataConnectorTools via stubby if on gLinux corp host."""
    mint_bin = "/google/data/ro/projects/gaiamint/bin/get_mint"
    has_mint = os.path.exists(mint_bin)
    has_stubby = shutil.which("stubby") is not None

    if not (has_mint and has_stubby):
        print("  [i] Internal stubby/get_mint tooling not detected (non-gLinux host).")
        print("      Discovery Engine discovers tools automatically via HTTP JSON-RPC handshake or when refreshed from gLinux.")
        return False

    auth_path = "/tmp/auth_node.txt"
    try:
        subprocess.run(
            [
                mint_bin,
                "--type=loas",
                "--text",
                "--endusercreds",
                "--scopes=35600",
                f"--out={auth_path}",
            ],
            check=True,
            capture_output=True,
        )
        connector_name = f"projects/{project_number}/locations/{location}/collections/{collection_id}/dataConnector"
        subprocess.run(
            [
                "stubby",
                f"--rpc_creds_file={auth_path}",
                "--deadline=60",
                "--output_json",
                "call",
                "blade:cloud-discovery-engine-assistant-data-connector-service-prod-global",
                "google.cloud.discoveryengine.v1main.DataConnectorService.RefreshDataConnectorTools",
            ],
            input=f'name: "{connector_name}"\n',
            text=True,
            check=True,
            capture_output=True,
        )
        print(f"  [+] Successfully refreshed dynamic_tools in Spanner via stubby for {connector_name}")
        return True
    except Exception as e:
        print(f"  [!] Note: stubby invocation skipped or encountered non-fatal error: {e}")
        return False


def build_action_params(instance_uri: str, tools: List[str]) -> Dict[str, Any]:
    return {
        "instance_uri": instance_uri,
        "auth_type": "NO_AUTH",
        "tool_list": " ".join(tools),
        "mcp_server_source": "BYO_MCP",
        "registry_mcp_server_name": "",
        "mcp_server_description": (
            "Mike OSS - Enterprise Legal AI Diligence Cockpit (MCP App). "
            "Scalable Google Cloud migration of Mike OSS with Cloud Spanner GraphRAG, "
            "Vertex AI Model Garden, and OpenTelemetry Cloud Trace. "
            "Use whenever the user asks about M&A diligence, Project Kestrel (M-331), "
            "Change of Control provisions, assignment covenants, notice windows, "
            "or comparing legal contracts in an interactive grid."
        ),
        "mcp_agent_instructions": (
            "CRITICAL: Do NOT use the built-in canvas tool for legal document grids. "
            "For any question about legal agreements, M&A diligence (Project Kestrel / M-331), "
            "Change of Control provisions, assignment covenants, termination rights, notice windows, "
            "or comparing documents in a grid, ALWAYS call `open_legal_analysis_grid` to open the "
            "interactive MCP App side panel. To evaluate new diligence criteria across contracts, "
            "call `add_dynamic_grid_column`."
        ),
    }


def register_mike_mcp_connector(
    project_id: str,
    project_number: str,
    location: str,
    instance_uri: str,
    datastore_id: str,
    display_name: str,
    engines: List[str],
    tools: List[str],
    dry_run: bool = False,
    verify_only: bool = False,
):
    print("================================================================================")
    print("MIKE OSS — GEMINI ENTERPRISE CUSTOM MCP APP CONNECTOR REGISTRATION")
    print("================================================================================")
    print(f"  GCP Project ID:         {project_id}")
    print(f"  Project Number:         {project_number}")
    print(f"  Discovery Location:     {location}")
    print(f"  Datastore ID:           {datastore_id}")
    print(f"  Collection Name:        {display_name}")
    print(f"  Instance URI:           {instance_uri}")
    print(f"  Enabled Tools:          {tools}")
    print(f"  Target Engines:         {engines}")
    print(f"  Mode:                   {'VERIFY ONLY' if verify_only else ('DRY RUN' if dry_run else 'ACTIVE REGISTRATION')}")
    print("================================================================================")

    base_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/{location}"
    ds_name = f"{base_url}/collections/default_collection/dataStores/{datastore_id}_mcp_data"
    dc_url = f"{base_url}/collections/{datastore_id}/dataConnector"

    # Step 1: Verify existing DataStore & DataConnector
    print("\n[1/4] Checking existing DataStore and DataConnector state...")
    ds_code, ds_body = api_req("GET", ds_name, project_id=project_id)
    dc_code, dc_body = api_req("GET", dc_url, project_id=project_id)

    ds_exists = (ds_code == 200)
    dc_exists = (dc_code == 200)

    if ds_exists:
        print(f"  [+] DataStore already exists: {ds_name}")
        print(f"      Display Name: {ds_body.get('displayName')}")
    else:
        print(f"  [-] DataStore not yet found (HTTP {ds_code}).")

    if dc_exists:
        print(f"  [+] DataConnector already exists: {dc_url}")
        print(f"      State: {dc_body.get('state')}, Action State: {dc_body.get('actionState')}")
        dyn_tools = dc_body.get("dynamicTools", [])
        print(f"      Dynamic Tools ({len(dyn_tools)}): {[(t.get('name'), t.get('enabled')) for t in dyn_tools]}")
    else:
        print(f"  [-] DataConnector not yet configured (HTTP {dc_code}).")

    if verify_only:
        print("\n[+] Verify-only mode finished.")
        return

    # Step 2: Provision via setUpDataConnector if not present
    print("\n[2/4] Provisioning Custom MCP DataConnector...")
    action_params = build_action_params(instance_uri, tools)
    setup_payload = {
        "collectionId": datastore_id,
        "collectionDisplayName": display_name,
        "dataConnector": {
            "dataSource": "custom_mcp",
            "params": {
                "instance_uri": instance_uri,
                "auth_type": "NO_AUTH",
            },
            "connectorModes": ["ACTIONS", "FEDERATED"],
            "bapConfig": {
                "supportedConnectorModes": ["ACTIONS"],
            },
            "entities": [{"entityName": "mcp_data"}],
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": False,
                "actionParams": action_params,
            },
        },
    }

    if dry_run:
        print("  [DRY RUN] Would call setUpDataConnector with payload:")
        print(json.dumps(setup_payload, indent=2))
    elif not ds_exists:
        setup_url = f"{base_url}:setUpDataConnector"
        print(f"  [*] Executing setUpDataConnector for {datastore_id}...")
        s_code, s_body = api_req("POST", setup_url, body=setup_payload, project_id=project_id)
        print(f"      Response HTTP {s_code}: {json.dumps(s_body)[:300]}")
        if s_code not in (200, 201):
            print(f"  [!] Warning: setUpDataConnector returned HTTP {s_code}. Inspect output above.")
        print("  [*] Waiting 5s for collection and datastore propagation...")
        time.sleep(5)
    else:
        print("  [=] Skipping setUpDataConnector since DataStore already exists.")

    # Step 3: Refresh dynamic tools and enable all 7 tools via PATCH
    print("\n[3/4] Refreshing Dynamic Tools in Spanner / Discovery Engine...")
    if not dry_run:
        try_refresh_dynamic_tools_via_stubby(project_number, location, datastore_id)
        patch_dc_url = f"{dc_url}?updateMask=bapConfig,actionConfig"
        patch_dc_payload = {
            "bapConfig": {
                "supportedConnectorModes": ["ACTIONS"],
                "enabledActions": tools,
            },
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": False,
                "actionParams": action_params,
            },
        }
        p_code, p_body = api_req("PATCH", patch_dc_url, body=patch_dc_payload, project_id=project_id)
        print(f"  [+] PATCH dataConnector enabledActions HTTP {p_code}")
        # Verify dynamic tools
        v_code, v_body = api_req("GET", dc_url, project_id=project_id)
        if v_code == 200:
            dt = v_body.get("dynamicTools", [])
            print(f"  [+] DataConnector state={v_body.get('state')}, actionState={v_body.get('actionState')}")
            print(f"  [+] DataConnector dynamicTools ({len(dt)}): {[(t.get('name'), t.get('enabled')) for t in dt]}")

    # Step 4: Attach DataStore to Gemini Enterprise Engines
    print("\n[4/4] Attaching DataStore to Gemini Enterprise Engines...")
    short_ds_id = f"{datastore_id}_mcp_data"
    for eng in engines:
        eng_url = f"{base_url}/collections/default_collection/engines/{eng}"
        e_code, e_body = api_req("GET", eng_url, project_id=project_id)
        if e_code == 404:
            print(f"  [!] Engine '{eng}' not found (HTTP 404). Skipping.")
            continue
        if e_code != 200:
            print(f"  [!] Engine '{eng}' error (HTTP {e_code}): {e_body}")
            continue

        existing_ids = list(e_body.get("dataStoreIds", []))
        if short_ds_id not in existing_ids:
            new_ids = existing_ids + [short_ds_id]
            if dry_run:
                print(f"  [DRY RUN] Would update engine '{eng}' dataStoreIds -> {new_ids}")
            else:
                patch_url = f"{eng_url}?updateMask=dataStoreIds"
                u_code, u_body = api_req("PATCH", patch_url, body={"dataStoreIds": new_ids}, project_id=project_id)
                if u_code == 200:
                    print(f"  [+] Engine '{eng}' attached successfully -> {new_ids}")
                else:
                    print(f"  [!] Failed to update engine '{eng}' (HTTP {u_code}): {u_body}")
        else:
            print(f"  [=] Engine '{eng}' already contains datastore '{short_ds_id}'.")

    print("\n================================================================================")
    print("REGISTRATION SCRIPT FINISHED")
    print("================================================================================")
    print(f"  Datastore ID: {short_ds_id}")
    print(f"  Instance URI: {instance_uri}")
    print(f"  Tools:        {tools}")
    print("================================================================================")


def main():
    parser = argparse.ArgumentParser(
        description="Register Mike OSS Diligence Cockpit Custom MCP Connector in Gemini Enterprise."
    )
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID, help=f"GCP Project ID (default: {DEFAULT_PROJECT_ID})")
    parser.add_argument("--project-number", default=DEFAULT_PROJECT_NUMBER, help=f"GCP Project Number (default: {DEFAULT_PROJECT_NUMBER})")
    parser.add_argument("--location", default=DEFAULT_LOCATION, help=f"Discovery Location (default: {DEFAULT_LOCATION})")
    parser.add_argument("--instance-uri", default=DEFAULT_INSTANCE_URI, help=f"Streamable MCP URL (default: {DEFAULT_INSTANCE_URI})")
    parser.add_argument("--datastore-id", default=DEFAULT_DATASTORE_ID, help=f"Collection/DataStore ID (default: {DEFAULT_DATASTORE_ID})")
    parser.add_argument("--display-name", default=DEFAULT_COLLECTION_DISPLAY_NAME, help="Collection Display Name")
    parser.add_argument("--engines", nargs="+", default=DEFAULT_ENGINES, help=f"Target GE engines (default: {DEFAULT_ENGINES})")
    parser.add_argument("--dry-run", action="store_true", help="Print API payloads without executing state-changing calls.")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing connector and engine states.")

    args = parser.parse_args()

    register_mike_mcp_connector(
        project_id=args.project_id,
        project_number=args.project_number,
        location=args.location,
        instance_uri=args.instance_uri,
        datastore_id=args.datastore_id,
        display_name=args.display_name,
        engines=args.engines,
        tools=ENABLED_TOOLS,
        dry_run=args.dry_run,
        verify_only=args.verify_only,
    )


if __name__ == "__main__":
    main()
