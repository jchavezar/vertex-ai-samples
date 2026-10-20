#!/usr/bin/env python3
"""Registers all 5 separate LexGraph Legal AI Cloud Run services as distinct Custom MCP App DataStores (`custom_mcp`) in Gemini Enterprise (`lexgraph-legal-spanner-ge` and `gemini-enterprise-17877637_1787763712023`)."""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ID = "vtxdemos"
PROJECT_NUMBER = "254356041555"
LOCATION = "global"

ENGINES = [
    "lexgraph-legal-spanner-ge",
    "gemini-enterprise-17877637_1787763712023",
]

FIVE_MCP_DATASTORES = [
    {
        "datastore_id": "mike-oss-legal-grid-mcp",
        "display_name": "Mike OSS — Tabular Diligence Grid & Pin-Cite Reader (MCP App)",
        "instance_uri": "https://mike-gcp-platform-254356041555.us-central1.run.app/mcp",
        "tools": [
            "open_legal_analysis_grid",
        ],
        "description": (
            "Mike OSS — Tabular Diligence Grid & Pin-Cite Reader (MCP App). "
            "Use whenever the user asks about M&A diligence, Project Kestrel (M-331), "
            "Change of Control provisions, assignment covenants, notice windows, or comparing contracts in an interactive spreadsheet grid."
        ),
        "instructions": (
            "CRITICAL: Do NOT use the built-in canvas tool for legal document grids. "
            "For any question about legal agreements, M&A diligence (Project Kestrel / M-331), "
            "Change of Control provisions, or comparing documents in a grid, ALWAYS call `open_legal_analysis_grid` "
            "with the user's question to open the Mike OSS Tabular Diligence Grid side panel."
        ),
    },
    {
        "datastore_id": "lexgraph-redline-legos-mcp",
        "display_name": "LexGraph Deterministic Redline & Word Legal Legos Studio (MCP App)",
        "instance_uri": "https://lexgraph-redline-word-agent-254356041555.us-central1.run.app/mcp",
        "tools": [
            "run_deterministic_redline",
        ],
        "description": (
            "LexGraph Deterministic Redline & Word Legal Legos Studio (MCP App). "
            "Computes word-level deterministic redline diffs comparing LexGraph v3 Playbook vs Skadden v4 Counterparty Markups "
            "(SPA Sec. 8.02(b) Indemnity Cap, Sec. 8.04(a) Double Materiality Scrape, Sec. 3.04 Tax 338(h)(10)) "
            "and composes modular Privacy Pro / M&A Legal Legos .docx clause riders."
        ),
        "instructions": (
            "Whenever the user asks to compare contract versions, inspect redlines (LexGraph v3 vs Skadden v4), "
            "check Playbook deviations, or assemble Legal Legos .docx clauses, ALWAYS call `run_deterministic_redline`."
        ),
    },
    {
        "datastore_id": "lexgraph-funds-antitrust-mcp",
        "display_name": "LexGraph FundGen / FundHQ MFN & Antitrust HSR Lab (MCP App)",
        "instance_uri": "https://lexgraph-funds-antitrust-agent-254356041555.us-central1.run.app/mcp",
        "tools": [
            "analyze_fundgen_and_antitrust",
        ],
        "description": (
            "LexGraph FundGen / FundHQ MFN & Antitrust HSR Multimodal Lab (MCP App). "
            "Evaluates LexGraph Private Equity Partners XII ($12.5B) LP side-letter MFN tiers (CalPERS, ADIA, Ontario Teachers, Yale, GIC), "
            "FTC HSR Second Request HHI market concentration deltas, and extracted multimodal EBITDA/Fee/Org charts."
        ),
        "instructions": (
            "Whenever the user asks about Private Funds (FundGen / FundHQ), LP side-letter MFN compendiums, "
            "management fee discounts, Antitrust HSR Second Request HHI concentration, or financial charts/diagrams, "
            "ALWAYS call `analyze_fundgen_and_antitrust`."
        ),
    },
    {
        "datastore_id": "lexgraph-intapp-wall-graph-mcp",
        "display_name": "LexGraph Intapp Ethical Wall, CMN Switcher & Spanner Graph (MCP App)",
        "instance_uri": "https://lexgraph-governance-wall-agent-254356041555.us-central1.run.app/mcp",
        "tools": [
            "traverse_precedent_graph",
        ],
        "description": (
            "LexGraph Intapp Ethical Wall, Client Matter Number (CMN) Switcher & Cloud Spanner LexGraphLegalGraph Explorer (MCP App). "
            "Enforces Screen-Before-Rank Intapp Ethical Walls (e.g. Project Omega M-999 vs Project Kestrel M-331) "
            "and traverses multi-hop precedent citations in Cloud Spanner."
        ),
        "instructions": (
            "Whenever the user asks about Intapp Ethical Walls, Screen-Before-Rank access control, "
            "Client Matter Numbers (CMN), Project Omega (M-999), or Cloud Spanner LexGraphLegalGraph traversal, "
            "ALWAYS call `traverse_precedent_graph`."
        ),
    },
    {
        "datastore_id": "lexgraph-inbox-calendar-mcp",
        "display_name": "LexGraph Partner Deal Inbox, CMN Auto-Filer & Calendar Triage (MCP App)",
        "instance_uri": "https://lexgraph-inbox-calendar-agent-254356041555.us-central1.run.app/mcp",
        "tools": [
            "triage_inbox_and_cmn_wall",
        ],
        "description": (
            "LexGraph Partner Deal Inbox, CMN Auto-Filer & Calendar Conflict Resolver (MCP App). "
            "Triages Partner Sarah Jenkins's P0 deal emails (EM-9901 Section 338(h)(10) Tax Gross-Up, EM-9902 Skadden Redline Strategy, "
            "EM-9903 Intapp Wall Alert), files to iManage, and delegates the Oct 15 Board vs FTC HSR calendar conflict (CAL-101)."
        ),
        "instructions": (
            "Whenever the user asks to triage partner emails, check unfiled deal emails (EM-9901..9903), "
            "auto-file emails to iManage by CMN, or resolve calendar conflicts (CAL-101), "
            "ALWAYS call `triage_inbox_and_cmn_wall`."
        ),
    },
]


def get_token() -> str:
    return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()


def api_req(method: str, url: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
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
    except Exception as e:
        return 500, {"error": str(e)}


def refresh_via_stubby(collection_id: str) -> bool:
    mint_bin = "/google/data/ro/projects/gaiamint/bin/get_mint"
    if not (os.path.exists(mint_bin) and shutil.which("stubby")):
        return False
    auth_path = "/tmp/auth_node.txt"
    try:
        subprocess.run(
            [mint_bin, "--type=loas", "--text", "--endusercreds", "--scopes=35600", f"--out={auth_path}"],
            check=True,
            capture_output=True,
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
            capture_output=True,
        )
        print(f"    [+] Refreshed dynamicTools via stubby for {collection_id}")
        return True
    except Exception as e:
        print(f"    [!] stubby refresh warning for {collection_id}: {e}")
        return False


def main():
    base_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}"
    all_short_ds_ids = []

    for spec in FIVE_MCP_DATASTORES:
        ds_id = spec["datastore_id"]
        disp = spec["display_name"]
        uri = spec["instance_uri"]
        tools = spec["tools"]
        short_ds = f"{ds_id}_mcp_data"
        all_short_ds_ids.append(short_ds)

        print(f"\n=== Registering [{ds_id}] -> {uri} ===")
        ds_name = f"{base_url}/collections/default_collection/dataStores/{short_ds}"
        dc_url = f"{base_url}/collections/{ds_id}/dataConnector"

        ds_code, _ = api_req("GET", ds_name)
        action_params = {
            "instance_uri": uri,
            "auth_type": "NO_AUTH",
            "tool_list": " ".join(tools),
            "mcp_server_source": "BYO_MCP",
            "registry_mcp_server_name": "",
            "mcp_server_description": spec["description"],
            "mcp_agent_instructions": spec["instructions"],
        }

        if ds_code != 200:
            setup_payload = {
                "collectionId": ds_id,
                "collectionDisplayName": disp,
                "dataConnector": {
                    "dataSource": "custom_mcp",
                    "params": {
                        "instance_uri": uri,
                    },
                    "connectorModes": ["ACTIONS"],
                    "bapConfig": {
                        "supportedConnectorModes": ["ACTIONS"],
                    },
                    "entities": [{"entityName": "mcp_data"}],
                    "actionConfig": {
                        "isActionConfigured": True,
                        "createBapConnection": True,
                        "actionParams": action_params,
                    },
                },
            }
            s_code, s_body = api_req("POST", f"{base_url}:setUpDataConnector", body=setup_payload)
            print(f"    [*] setUpDataConnector HTTP {s_code}")
            time.sleep(5)
        else:
            print(f"    [=] DataStore {short_ds} already exists.")

        refresh_via_stubby(ds_id)
        time.sleep(2)

        patch_dc_payload = {
            "refreshInterval": "86400s",
            "bapConfig": {
                "supportedConnectorModes": ["ACTIONS"],
                "enabledActions": tools,
            },
            "actionConfig": {
                "isActionConfigured": True,
                "createBapConnection": True,
                "actionParams": action_params,
            },
        }
        p_code, p_body = api_req("PATCH", f"{dc_url}?updateMask=bapConfig,actionConfig,refreshInterval", body=patch_dc_payload)
        if p_code != 200:
            print(f"    [!] PATCH warning HTTP {p_code}: {p_body}")
        # Call refresh_via_stubby a second time so enabled_actions -> dynamicTools[].enabled = True in Spanner
        refresh_via_stubby(ds_id)
        v_code, v_body = api_req("GET", dc_url)
        dt = v_body.get("dynamicTools", []) if v_code == 200 else []
        print(
            f"    [+] PATCH HTTP {p_code} | State={v_body.get('state')} | ActionState={v_body.get('actionState')} | "
            f"Tools={[ (t.get('name'), t.get('enabled')) for t in dt ]}"
        )

    print("\n=== Attaching all 5 Custom MCP App DataStores to Gemini Enterprise Engines ===")
    for eng in ENGINES:
        eng_url = f"{base_url}/collections/default_collection/engines/{eng}"
        e_code, e_body = api_req("GET", eng_url)
        if e_code != 200:
            print(f"  [!] Engine {eng} HTTP {e_code}")
            continue
        existing = list(e_body.get("dataStoreIds", []))
        merged = list(existing)
        for sds in all_short_ds_ids:
            if sds not in merged:
                merged.append(sds)
        if merged != existing:
            u_code, u_body = api_req("PATCH", f"{eng_url}?updateMask=dataStoreIds", body={"dataStoreIds": merged})
            print(f"  [+] Updated Engine {eng} HTTP {u_code} -> {merged}")
        else:
            print(f"  [=] Engine {eng} already has all 5 datastores -> {merged}")


if __name__ == "__main__":
    main()
