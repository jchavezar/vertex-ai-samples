"""Mint a Dynamic Client Registration (RFC 7591) client at the Atlassian
Remote MCP server for use with Gemini Enterprise's custom-MCP datastore
"Re-authenticate" dialog.

The MCP server runs its own OAuth 2.1 server with its own client registry —
credentials minted at developer.atlassian.com will NOT work. The DCR endpoint
lives on the `cf.mcp.atlassian.com` subdomain (the apex `mcp.atlassian.com`
returns 404 here).

Output is written to ~/.secrets/atlassian-rovo-dcr-ge.json with mode 0600.
The script is idempotent: a second run prints the existing creds and exits.
Pass --force to remint (overwriting the existing file).

Usage:
    python dcr_register.py            # mint or print existing
    python dcr_register.py --force    # remint
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

DCR_URL = "https://cf.mcp.atlassian.com/v1/register"
GE_REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"
CLIENT_NAME = "gemini-enterprise-jira-testing"
OUT_PATH = Path(os.path.expanduser("~/.secrets/atlassian-rovo-dcr-ge.json"))


def mint() -> dict:
    body = {
        "client_name": CLIENT_NAME,
        "redirect_uris": [GE_REDIRECT_URI],
        "token_endpoint_auth_method": "client_secret_basic",
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
    }
    print(f"POST {DCR_URL}")
    resp = requests.post(DCR_URL, json=body, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"ERROR ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    return data


def write_creds(data: dict) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2))
    OUT_PATH.chmod(0o600)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Remint even if the cred file exists")
    args = parser.parse_args()

    if OUT_PATH.exists() and not args.force:
        existing = json.loads(OUT_PATH.read_text())
        print(f"DCR creds already exist at {OUT_PATH}")
        print(f"  client_id     : {existing.get('client_id')}")
        secret = existing.get("client_secret", "")
        print(f"  client_secret : {secret[:8]}{'...' if secret else ''} (len={len(secret)})")
        print("Pass --force to remint.")
        return

    data = mint()
    write_creds(data)
    print(f"DCR creds written to {OUT_PATH}")
    print(f"  client_id     : {data.get('client_id')}")
    print(f"  client_secret : {data.get('client_secret', '')[:8]}... (full secret in file)")
    print(f"  redirect_uris : {data.get('redirect_uris')}")


if __name__ == "__main__":
    main()
