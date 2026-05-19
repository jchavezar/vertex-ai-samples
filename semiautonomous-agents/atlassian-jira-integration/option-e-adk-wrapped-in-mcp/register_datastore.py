"""Register the Option E `mcp-adk-wrapper` Cloud Run service as a custom MCP
data store on the Gemini Enterprise engine `jira-testing_1778158449701`.

Same shape as option-b's register_datastore.py — the only differences are:
  - instance_uri points at the Option E wrapper, not Atlassian's hosted MCP.
  - OAuth endpoints are the standard Atlassian auth.atlassian.com endpoints
    (NOT cf.mcp.atlassian.com), matching Option C's connector — because the
    bearer token is consumed inside our wrapper, then re-injected into the
    ADK agent's session state.
  - Datastore collection id defaults to `mcp-adk-wrapper-<ts>`.
  - mcp_agent_instructions reflects search/fetch primitives.

Usage:
    python register_datastore.py
    DATASTORE_ID=mcp-adk-wrapper-prod python register_datastore.py

After running, complete the GE console steps:
  AI Applications → Engine → Data stores → mcp_adk_wrapper-<ts> →
  Actions tab → "Reload custom actions" → enable search + fetch →
  "Re-authenticate" (paste OPTION_C/E OAuth client_id/secret; sign in as
  the admin@jesusarguelles.altostrat.com user that owns the Jira site).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
import google.auth
import google.auth.transport.requests

# ---- Load eval/.env so we can reuse OPTION_C OAuth creds + IDs -------------
_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE / ".env", _HERE.parent / "eval" / ".env"):
    if _candidate.exists():
        for line in _candidate.read_text().splitlines():
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

DEFAULT_DATASTORE_ID = f"mcp-adk-wrapper-{int(time.time())}"
DATASTORE_ID = os.environ.get("DATASTORE_ID", DEFAULT_DATASTORE_ID)
COLLECTION_DISPLAY_NAME = os.environ.get(
    "COLLECTION_DISPLAY_NAME", "Jira ADK-wrapped MCP (Option E)"
)

# Option E Cloud Run service URL — the /mcp StreamableHTTP endpoint.
WRAPPER_BASE_URL = os.environ.get(
    "WRAPPER_BASE_URL",
    "https://mcp-adk-wrapper-254356041555.us-central1.run.app",
).rstrip("/")
INSTANCE_URI = os.environ.get("INSTANCE_URI", f"{WRAPPER_BASE_URL}/mcp")

# Reuse Option C's Atlassian OAuth client (same OAuth app, same scopes; the
# token gets forwarded into the ADK agent's session state).
ATLASSIAN_AUTH_URI = "https://auth.atlassian.com/authorize"
ATLASSIAN_TOKEN_URI = "https://auth.atlassian.com/oauth/token"
ATLASSIAN_SCOPES = (
    "read:jira-work write:jira-work read:jira-user offline_access"
)
CLIENT_ID = os.environ.get("ATLASSIAN_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("ATLASSIAN_CLIENT_SECRET", "")


def _gcp_token() -> str:
    """Prefer GCLOUD_ACCOUNT for parity with the eval runners; falls back to
    ADC. The engine PATCH and setUpDataConnector require an identity with
    discoveryengine.admin permissions on the project."""
    acct = os.environ.get("GCLOUD_ACCOUNT")
    if acct:
        import subprocess
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token", "--account", acct],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token  # type: ignore[return-value]


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_gcp_token()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base_url() -> str:
    return (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/{LOCATION}"
    )


def _data_connector(client_id: str, client_secret: str) -> dict:
    return {
        "dataSource": "custom_mcp",
        # The public DE validator insists on params.oauth_access_token; the
        # real OAuth flows through actionConfig.actionParams (3LO).
        "params": {"oauth_access_token": "placeholder-real-auth-via-3LO"},
        "connectorModes": ["ACTIONS", "FEDERATED"],
        "bapConfig": {"supportedConnectorModes": ["ACTIONS"]},
        "entities": [{"entityName": "mcp_data"}],
        "actionConfig": {
            "isActionConfigured": True,
            "createBapConnection": True,
            "actionParams": {
                "instance_uri": INSTANCE_URI,
                "auth_type": "OAUTH",
                "auth_uri": ATLASSIAN_AUTH_URI,
                "token_uri": ATLASSIAN_TOKEN_URI,
                "scopes": ATLASSIAN_SCOPES,
                "client_id": client_id,
                "client_secret": client_secret,
                "mcp_server_source": "BYO_MCP",
                "registry_mcp_server_name": "",
                "mcp_server_description": (
                    "Jira via an ADK agent wrapped inside an MCP server. "
                    "Exposes two retrieval primitives — search(query) and "
                    "fetch(id) — both of which delegate to the deep "
                    "Option A ADK orchestration on Vertex Agent Engine. "
                    "Use whenever the user asks about Jira tickets, "
                    "projects, sprints, comments, worklogs, links or "
                    "cross-issue analysis."
                ),
                "mcp_agent_instructions": (
                    "For ANY Jira question, call `search` with the user's "
                    "question verbatim — do not rewrite, summarize, or "
                    "split it. The tool returns a SearchResultPage whose "
                    "single result already contains a complete, polished "
                    "answer (markdown tables, clickable [KEY](URL) links, "
                    "explicit refusals when appropriate). COPY the "
                    "`results[0].text` field VERBATIM as the assistant's "
                    "response — do not re-summarize or trim it. Use "
                    "`fetch(id)` only when the user explicitly asks for "
                    "the full record of a single issue key."
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
        print(f"\n  SWAP_EXISTING=1 — replacing dataStoreIds with [{short_id}]")
        resp2 = requests.patch(
            url, headers=_headers(), json={"dataStoreIds": [short_id]}, timeout=30
        )
        if resp2.status_code == 200:
            print("  SWAP OK")
            return True
        print(f"  SWAP FAILED ({resp2.status_code}): {resp2.text[:600]}")
    return False


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        print(
            "ATLASSIAN_CLIENT_ID / ATLASSIAN_CLIENT_SECRET missing — "
            "set them in eval/.env (same OAuth app Option C uses).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Wrapper instance_uri : {INSTANCE_URI}")
    print(f"OAuth client_id      : {CLIENT_ID}")
    print(f"Target project       : {GE_PROJECT_ID} ({GE_PROJECT_NUMBER})")
    print(f"Target engine        : {GE_ENGINE_ID}")
    print(f"Per-MCP collection   : {DATASTORE_ID}")
    print(f"Entity datastore     : {DATASTORE_ID}_mcp_data (in {COLLECTION_ID})")

    entity_name = _entity_ds_name(DATASTORE_ID)
    existing = _get_datastore(entity_name)
    if existing is not None:
        print("\nDatastore already exists — skipping create.")
        print(f"  name          : {existing['name']}")
        print(f"  connectorName : {existing.get('connectorName')}")
        attached = attach_to_engine(f"{DATASTORE_ID}_mcp_data")
        if attached:
            print(f"  engine attach : OK ({GE_ENGINE_ID})")
        return

    dc = _data_connector(CLIENT_ID, CLIENT_SECRET)
    chosen = None

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

    print("\nResolving entity datastore...")
    ds = None
    for _ in range(40):
        ds = _get_datastore(entity_name)
        if ds is not None:
            break
        time.sleep(3)

    if ds is None:
        print(
            f"\nEntity datastore not visible. Expected: {entity_name}",
            file=sys.stderr,
        )
        sys.exit(4)

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
            f"  engine attach    : NOT ATTACHED (engine is in single-datastore "
            f"mode; use SWAP_EXISTING=1 or attach via console)"
        )
    print(
        "\nNext steps in the GE Console:\n"
        f"  AI Applications → Engine '{GE_ENGINE_ID}' → Data stores → "
        f"mcp_data ({DATASTORE_ID}) → Actions tab → 'Reload custom actions' "
        f"→ enable search + fetch → 'Re-authenticate' (sign in as the "
        f"admin@jesusarguelles.altostrat.com user that owns the Jira site).\n"
        f"\nThen set in eval/.env:\n"
        f"  OPTION_I_DATASTORE_ID={DATASTORE_ID}_mcp_data"
    )


if __name__ == "__main__":
    main()
