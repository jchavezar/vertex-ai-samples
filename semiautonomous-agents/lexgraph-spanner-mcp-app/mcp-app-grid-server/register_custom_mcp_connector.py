"""Register and configure the LexGraph Interactive Legal Grid & Citation Highlighter MCP App (SEP-1865) as a Custom MCP Data Connector (custom_mcp) in Gemini Enterprise."""

import json
import subprocess
import time
import urllib.error
import urllib.request

PROJECT_ID = "vtxdemos"
PROJECT_NUMBER = "254356041555"
LOCATION = "global"
MCP_BASE_URL = "https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app"
INSTANCE_URI = f"{MCP_BASE_URL}/mcp"
DATASTORE_ID = "lexgraph-legal-grid-mcp-app"
LEGACY_DATASTORE_ID = "agentspace-hybrid-custom-mcp-lexgraph-grid_mcp_data"
COLLECTION_DISPLAY_NAME = "LexGraph Interactive Legal Grid & Citation Highlighter (MCP App)"

ENGINES = [
    "lexgraph-legal-spanner-ge",
    "gemini-enterprise-17877637_1787763712023",
]

ENABLED_TOOLS = [
    "open_legal_analysis_grid",
    "inspect_selected_files",
    "grant_teammate_email_30d",
]

ACTION_PARAMS = {
    "instance_uri": INSTANCE_URI,
    "auth_type": "NO_AUTH",
    "tool_list": " ".join(ENABLED_TOOLS),
    "mcp_server_source": "BYO_MCP",
    "registry_mcp_server_name": "",
    "mcp_server_description": (
        "LexGraph Interactive Legal Document Analysis Grid & Original Citation Highlighter MCP App (SEP-1865). "
        "Use whenever the user asks about legal agreements, M&A indemnification caps, baskets, materiality scrapes, "
        "Skadden redlines, tax riders, or comparing documents in an interactive grid."
    ),
    "mcp_agent_instructions": (
        "CRITICAL: Do NOT use the built-in canvas tool for legal document grids. "
        "For any question about legal agreements, M&A deals (M-331, M-215, M-518, M-402, M-109), "
        "indemnification caps, baskets, materiality scrapes, Skadden redlines, or comparing documents in a grid, "
        "ALWAYS call `open_legal_analysis_grid` with the user's question to open the interactive MCP App side panel. "
        "When the user selects specific files to inspect, call `inspect_selected_files`."
    ),
}


def get_token() -> str:
  return subprocess.check_output(
      ["gcloud", "auth", "print-access-token"], text=True
  ).strip()


def api_req(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
  headers = {
      "Authorization": f"Bearer {get_token()}",
      "Content-Type": "application/json",
      "X-Goog-User-Project": PROJECT_ID,
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


def refresh_dynamic_tools_via_stubby(collection_id: str) -> None:
  """Calls internal DataConnectorService.RefreshDataConnectorTools via stubby to populate dynamic_tools in Spanner."""
  auth_path = "/tmp/auth_node.txt"
  subprocess.run(
      [
          "/google/data/ro/projects/gaiamint/bin/get_mint",
          "--type=loas",
          "--text",
          "--endusercreds",
          "--scopes=35600",
          f"--out={auth_path}",
      ],
      check=True,
  )
  connector_name = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/{collection_id}/dataConnector"
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
  )
  print(f"[+] Refreshed dynamic_tools in Spanner for {connector_name}")


def setup_custom_mcp_connector():
  base_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}"
  ds_name = f"{base_url}/collections/default_collection/dataStores/{DATASTORE_ID}_mcp_data"
  code, _ = api_req("GET", ds_name)
  if code == 200:
    print(f"[+] Custom MCP DataStore already exists: {ds_name}")
  else:
    setup_url = f"{base_url}:setUpDataConnector"
    payload = {
        "collectionId": DATASTORE_ID,
        "collectionDisplayName": COLLECTION_DISPLAY_NAME,
        "dataConnector": {
            "dataSource": "custom_mcp",
            "params": {
                "instance_uri": INSTANCE_URI,
                "auth_type": "NO_AUTH",
            },
            "connectorModes": ["ACTIONS", "FEDERATED"],
            "bapConfig": {
                "supportedConnectorModes": ["ACTIONS"],
                "enabledActions": ENABLED_TOOLS,
            },
            "entities": [{"entityName": "mcp_data"}],
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": False,
                "actionParams": ACTION_PARAMS,
            },
        },
    }
    print(f"[*] Calling setUpDataConnector for {DATASTORE_ID}...")
    s_code, s_body = api_req("POST", setup_url, payload)
    print(f"    HTTP {s_code}: {json.dumps(s_body)[:400]}")
    time.sleep(5)

  # Populate dynamic_tools in Spanner via RefreshDataConnectorTools (preserving enabled_actions -> enabled: true)
  refresh_dynamic_tools_via_stubby(DATASTORE_ID)

  # Verify dynamic_tools on the connector
  dc_base = f"{base_url}/collections/{DATASTORE_ID}/dataConnector"
  g_code, g_body = api_req("GET", dc_base)
  if g_code == 200:
    dt = g_body.get("dynamicTools", [])
    print(f"[+] Verified {len(dt)} dynamicTools on {DATASTORE_ID}: {[ (t.get('name'), t.get('enabled')) for t in dt ]}")

  # Attach to Gemini Enterprise engines
  short_ds_id = f"{DATASTORE_ID}_mcp_data"
  for eng in ENGINES:
    eng_url = f"{base_url}/collections/default_collection/engines/{eng}"
    e_code, e_body = api_req("GET", eng_url)
    if e_code != 200:
      print(f"[!] Could not read engine {eng}: {e_code}")
      continue
    existing_ids = list(e_body.get("dataStoreIds", []))
    new_ids = [x for x in existing_ids if x != LEGACY_DATASTORE_ID]
    if short_ds_id not in new_ids:
      new_ids.append(short_ds_id)
    if new_ids != existing_ids:
      u_code, _ = api_req(
          "PATCH",
          f"{eng_url}?updateMask=dataStoreIds",
          {"dataStoreIds": new_ids},
      )
      print(f"[+] Updated dataStoreIds on engine {eng} -> {new_ids}: HTTP {u_code}")
    else:
      print(f"[=] Engine {eng} already has {new_ids}")


if __name__ == "__main__":
  setup_custom_mcp_connector()
