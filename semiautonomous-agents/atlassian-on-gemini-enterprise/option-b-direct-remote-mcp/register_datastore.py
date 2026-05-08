"""Create the Atlassian Remote MCP custom-MCP datastore on Gemini Enterprise
engine ``jira-testing_1778158449701`` (project ``vtxdemos``).

The DE backend creates a fresh per-MCP **Collection** (singleton DataConnector
inside it) and a `_mcp_data` entity datastore in `default_collection`. This is
done atomically by the ``setUpDataConnector`` method on
``projects/{p}/locations/{l}``. The resulting entity datastore is then
attached to the engine via PATCH on ``engines/<id>?updateMask=dataStoreIds``.

The actionConfig.actionParams shape is copied verbatim from the prior
ground-truth datastore (see plan §"Inputs you have").

Both creation paths are tried in order, and whichever succeeds is recorded:
    1. POST .../locations/global:setUpDataConnector  (V1 — wrapper body)
    2. POST .../locations/global:setUpDataConnectorV2 (V2 — query params)

Idempotent: if a datastore with the chosen id already exists on the engine,
the script prints its info and exits 0.

Usage:
    python register_datastore.py
    DATASTORE_ID=jiramcp-rovo-custom python register_datastore.py
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
import google.auth
import google.auth.transport.requests

# ---- Lightweight .env loader (no python-dotenv) ----
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
GE_ENGINE_ID = os.environ.get("GE_ENGINE_ID", "jira-testing_1778158449701")
COLLECTION_ID = os.environ.get("GE_COLLECTION_ID", "default_collection")
LOCATION = os.environ.get("GE_LOCATION", "global")
# DATASTORE_ID is the per-MCP Collection ID; the resulting entity datastore is
# placed in default_collection and named ``<DATASTORE_ID>_mcp_data``.
DEFAULT_DATASTORE_ID = f"jiramcp-rovo-{int(time.time())}"
DATASTORE_ID = os.environ.get("DATASTORE_ID", DEFAULT_DATASTORE_ID)
COLLECTION_DISPLAY_NAME = os.environ.get(
    "COLLECTION_DISPLAY_NAME", "Jira MCP (Atlassian Rovo)"
)
DCR_FILE = Path(os.path.expanduser(
    os.environ.get("DCR_FILE", "~/.secrets/atlassian-rovo-dcr-ge.json")
))

ATLASSIAN_MCP_URL = "https://mcp.atlassian.com/v1/mcp"
ATLASSIAN_AUTH_URI = "https://mcp.atlassian.com/v1/authorize"
ATLASSIAN_TOKEN_URI = "https://cf.mcp.atlassian.com/v1/token"  # cf. is mandatory
ATLASSIAN_SCOPES = (
    "read:jira-work write:jira-work read:jira-user "
    "read:confluence-content.all read:confluence-space.summary "
    "read:me offline_access"
)


def _headers() -> dict:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base_url() -> str:
    return (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{LOCATION}"
    )


def _load_dcr() -> tuple[str, str]:
    if not DCR_FILE.exists():
        print(
            f"DCR creds not found at {DCR_FILE}. Run dcr_register.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(DCR_FILE.read_text())
    cid = data.get("client_id")
    secret = data.get("client_secret")
    if not cid or not secret:
        print(f"DCR file is missing client_id/client_secret: {DCR_FILE}", file=sys.stderr)
        sys.exit(1)
    return cid, secret


def _data_connector(client_id: str, client_secret: str) -> dict:
    """Mirror the ground-truth dataConnector shape (custom_mcp BYO_MCP)."""
    return {
        "dataSource": "custom_mcp",
        # The public DE validator for custom_mcp insists on
        # params.oauth_access_token; it ignores params.instance_uri (the
        # post-create dataConnector will show params.instance_uri because the
        # backend re-derives it from actionParams). We pass a placeholder
        # token here — real auth flows through actionConfig.actionParams (3LO
        # via the GE console "Re-authenticate" dialog).
        "params": {"oauth_access_token": "placeholder-real-auth-via-3LO"},
        "connectorModes": ["ACTIONS", "FEDERATED"],
        "bapConfig": {"supportedConnectorModes": ["ACTIONS"]},
        # entities[].entityName = "mcp_data" triggers the per-entity
        # `<collection>_mcp_data` DataStore creation in default_collection.
        "entities": [{"entityName": "mcp_data"}],
        "actionConfig": {
            "isActionConfigured": True,
            "createBapConnection": True,
            "actionParams": {
                "instance_uri": ATLASSIAN_MCP_URL,
                "auth_type": "OAUTH",
                "auth_uri": ATLASSIAN_AUTH_URI,
                "token_uri": ATLASSIAN_TOKEN_URI,
                "scopes": ATLASSIAN_SCOPES,
                "client_id": client_id,
                "client_secret": client_secret,
                "mcp_server_source": "BYO_MCP",
                "registry_mcp_server_name": "",
                "mcp_server_description": (
                    "Atlassian Rovo MCP server providing access to Jira "
                    "issues, projects, sprints, comments, worklogs and "
                    "Confluence pages, spaces, comments. Use whenever the "
                    "user asks about Jira tickets, projects, sprints, "
                    "Confluence pages or anything in sockcop.atlassian.net."
                ),
                "mcp_agent_instructions": (
                    "When the user asks about Jira issues, tickets, bugs, "
                    "stories, epics, sprints, projects, worklogs or "
                    "Confluence pages, ALWAYS call the Atlassian MCP "
                    "tools (e.g. searchJiraIssuesUsingJql, getJiraIssue, "
                    "createJiraIssue, getConfluencePage, "
                    "searchConfluenceUsingCql). For listings, call "
                    "searchJiraIssuesUsingJql with a JQL such as "
                    "'order by created DESC' and a limit. Format issue "
                    "results as a numbered list with key, summary, "
                    "status, and assignee. Never tell the user the "
                    "connector is unavailable — always attempt the tool "
                    "call first."
                ),
            },
        },
    }


def _entity_ds_name(datastore_id: str) -> str:
    return (
        f"projects/{GE_PROJECT_NUMBER}/locations/{LOCATION}/collections/"
        f"{COLLECTION_ID}/dataStores/{datastore_id}_mcp_data"
    )


def _engine_url() -> str:
    return (
        f"{_base_url()}/collections/{COLLECTION_ID}/engines/{GE_ENGINE_ID}"
    )


def _get_engine() -> dict:
    resp = requests.get(_engine_url(), headers=_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def _get_datastore(name: str) -> dict | None:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{name}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def _wait_lro(op_name: str, timeout_s: int = 180) -> dict:
    """Poll an LRO. Tolerates 404s (some MCP setup ops vanish from the LRO
    surface within seconds — we treat 5 consecutive 404s as 'completed,
    fall through and verify by GET on the entity datastore'."""
    op_url = f"https://discoveryengine.googleapis.com/v1alpha/{op_name}"
    deadline = time.time() + timeout_s
    not_found_streak = 0
    while time.time() < deadline:
        resp = requests.get(op_url, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            not_found_streak = 0
            body = resp.json()
            if body.get("done"):
                if "error" in body:
                    raise RuntimeError(f"LRO failed: {body['error']}")
                return body
        elif resp.status_code == 404:
            not_found_streak += 1
            if not_found_streak >= 5:
                print("  LRO no longer queryable (5x 404) — assuming completed")
                return {"done": True, "_inferred": True}
        else:
            print(f"  LRO poll non-200 ({resp.status_code}): {resp.text[:200]}")
        time.sleep(3)
    raise TimeoutError(f"LRO {op_name} did not complete in {timeout_s}s")


def _try_setup(label: str, url: str, payload: dict) -> tuple[bool, dict | None]:
    print(f"\n--- Try [{label}] ---")
    print(f"POST {url}")
    resp = requests.post(url, headers=_headers(), json=payload, timeout=60)
    print(f"  status: {resp.status_code}")
    if resp.status_code in (200, 201):
        body = resp.json()
        op = body.get("name", "")
        print(f"  LRO: {op}")
        if op:
            try:
                done = _wait_lro(op)
                print(f"  LRO done: {done.get('done')}")
                return True, done
            except Exception as e:
                print(f"  LRO error: {e}")
                return False, None
        return True, body
    print(f"  body: {resp.text[:800]}")
    return False, None


def attach_to_engine(short_id: str) -> bool:
    """PATCH the engine to add the new entity datastore to its dataStoreIds.

    SOLUTION_TYPE_SEARCH engines created in single-datastore mode return
    ``FAILED_PRECONDITION: Engines with a single data store cannot add or
    remove data stores``. In that case, set ``SWAP_EXISTING=1`` to replace
    the engine's datastore list with just this one (the caller is
    responsible for understanding that the prior datastore becomes orphaned
    from this engine's chat surface — its underlying connector is left
    intact)."""
    engine = _get_engine()
    existing = list(engine.get("dataStoreIds", []))
    if short_id in existing:
        print(f"  Engine already references {short_id}; skipping PATCH")
        return True
    new_ids = existing + [short_id]
    url = f"{_engine_url()}?updateMask=dataStoreIds"
    print(f"PATCH {url}\n  dataStoreIds += {short_id}")
    resp = requests.patch(
        url, headers=_headers(), json={"dataStoreIds": new_ids}, timeout=30
    )
    if resp.status_code == 200:
        print("  PATCH OK")
        return True

    body = resp.text
    print(f"  PATCH FAILED ({resp.status_code}): {body[:600]}")

    if (
        resp.status_code == 400
        and os.environ.get("SWAP_EXISTING") == "1"
        and "single data store" in body
    ):
        print(
            f"\n  SWAP_EXISTING=1 set — replacing dataStoreIds with [{short_id}]\n"
            f"  (prior dataStoreIds: {existing})"
        )
        resp2 = requests.patch(
            url, headers=_headers(), json={"dataStoreIds": [short_id]}, timeout=30
        )
        if resp2.status_code == 200:
            print("  SWAP OK")
            return True
        print(f"  SWAP FAILED ({resp2.status_code}): {resp2.text[:600]}")
    elif resp.status_code == 400 and "single data store" in body:
        print(
            "\n  Engine is in single-datastore mode and already has a "
            "datastore attached. The new datastore exists and is fully "
            "wired, but the engine still serves the OLD datastore. "
            "Re-run with SWAP_EXISTING=1 to point this engine at the new "
            "datastore (and orphan the previous one's engine attachment)."
        )
    return False


def main() -> None:
    cid, secret = _load_dcr()
    print(f"Using DCR client_id : {cid}")
    print(f"Target project      : {GE_PROJECT_ID} ({GE_PROJECT_NUMBER})")
    print(f"Target engine       : {GE_ENGINE_ID}")
    print(f"Per-MCP collection  : {DATASTORE_ID}")
    print(f"Entity datastore    : {DATASTORE_ID}_mcp_data (in {COLLECTION_ID})")

    entity_name = _entity_ds_name(DATASTORE_ID)
    existing = _get_datastore(entity_name)
    if existing is not None:
        print("\nDatastore already exists — skipping create.")
        print(f"  name          : {existing['name']}")
        print(f"  connectorName : {existing.get('connectorName')}")
        # Make sure the engine has it (best-effort).
        attached = attach_to_engine(f"{DATASTORE_ID}_mcp_data")
        if attached:
            print(f"  engine attach : OK ({GE_ENGINE_ID})")
        return

    dc = _data_connector(cid, secret)
    chosen = None

    # V1 — wrapper body
    v1_url = f"{_base_url()}:setUpDataConnector"
    v1_body = {
        "collectionId": DATASTORE_ID,
        "collectionDisplayName": COLLECTION_DISPLAY_NAME,
        "dataConnector": dc,
    }
    ok, _ = _try_setup("setUpDataConnector (V1)", v1_url, v1_body)
    if ok:
        chosen = "setUpDataConnector"
    else:
        # V2 — collection params in query, dataConnector as full body
        from urllib.parse import urlencode
        qs = urlencode({
            "collectionId": DATASTORE_ID,
            "collectionDisplayName": COLLECTION_DISPLAY_NAME,
        })
        v2_url = f"{_base_url()}:setUpDataConnectorV2?{qs}"
        ok, _ = _try_setup("setUpDataConnectorV2", v2_url, dc)
        if ok:
            chosen = "setUpDataConnectorV2"

    if not chosen:
        print("\nBOTH setUpDataConnector paths failed. Aborting.", file=sys.stderr)
        sys.exit(2)

    # Resolve final entity datastore
    print("\nResolving entity datastore...")
    ds = None
    for _ in range(40):
        ds = _get_datastore(entity_name)
        if ds is not None:
            break
        time.sleep(3)

    if ds is None:
        print(
            "\nEntity datastore not yet visible via GET; LRO may still be propagating.\n"
            f"Expected name: {entity_name}",
            file=sys.stderr,
        )
        sys.exit(4)

    # Attach to engine
    print()
    attached = attach_to_engine(f"{DATASTORE_ID}_mcp_data")

    print("\n=== DATASTORE CREATE SUCCESS ===")
    print(f"  setup method     : {chosen}")
    print(f"  entity datastore : {ds['name']}")
    print(f"  connector        : {ds.get('connectorName')}")
    print(f"  short id         : {DATASTORE_ID}_mcp_data")
    if attached:
        print(f"  engine attach    : OK ({GE_ENGINE_ID} → {DATASTORE_ID}_mcp_data)")
    else:
        print(
            f"  engine attach    : NOT ATTACHED to {GE_ENGINE_ID}\n"
            f"                     (engine is in single-datastore mode and is "
            f"locked to its current datastore via the public DE API).\n"
            f"                     The datastore is fully wired and usable; "
            f"to swap it onto the engine,\n"
            f"                     use the console UI: AI Applications → "
            f"Engine → Data stores → 'Edit data stores'."
        )
    print(
        "\nNext: open the GE console → AI Applications → Engine "
        f"'{GE_ENGINE_ID}' → Data stores → mcp_data ({DATASTORE_ID}) → "
        "Actions tab → 'Reload custom actions' → enable tools → "
        "'Re-authenticate' (paste DCR client_id/secret from "
        "~/.secrets/atlassian-rovo-dcr-ge.json).\n"
        "See enable_actions_checklist.md for the full sequence."
    )


if __name__ == "__main__":
    main()
