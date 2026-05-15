"""Print the DCR client_id/client_secret pair you need to paste into the
Gemini Enterprise console "Re-authenticate" dialog after the custom MCP
datastore is created and you click "Enable actions".

Reads from ``~/.secrets/atlassian-rovo-dcr-ge.json`` (mint via
``dcr_register.py``).

Usage:
    python reauth_helper.py
"""
import json
import os
import sys
from pathlib import Path

DCR_FILE = Path(os.path.expanduser(
    os.environ.get("DCR_FILE", "~/.secrets/atlassian-rovo-dcr-ge.json")
))


def main() -> None:
    if not DCR_FILE.exists():
        print(
            f"DCR creds not found at {DCR_FILE}. Run `python dcr_register.py` first.",
            file=sys.stderr,
        )
        sys.exit(1)
    data = json.loads(DCR_FILE.read_text())
    cid = data.get("client_id", "")
    secret = data.get("client_secret", "")
    print(
        "================================================================\n"
        " Gemini Enterprise → Custom MCP Datastore → 'Re-authenticate'\n"
        "================================================================\n"
        "\n"
        "Paste the values below into the form fields shown in the dialog.\n"
        "These come from the RFC 7591 Dynamic Client Registration mint at\n"
        "https://cf.mcp.atlassian.com/v1/register and are bound to the GE\n"
        "redirect URI https://vertexaisearch.cloud.google.com/oauth-redirect\n"
        f"(file: {DCR_FILE}).\n"
        "\n"
        f"  Client ID     : {cid}\n"
        f"  Client Secret : {secret}\n"
        "\n"
        "After pasting and clicking 'Connect':\n"
        "  1. A popup opens to mcp.atlassian.com/v1/authorize.\n"
        "  2. Approve the Atlassian app consent.\n"
        "  3. Pick your Atlassian site (e.g. sockcop.atlassian.net) on the\n"
        "     standard 3LO consent screen.\n"
        "  4. Popup closes; the datastore goes ACTIVE and tools become\n"
        "     callable from GE chat.\n"
        "\n"
        "If you see 'invalid_client': the credentials above were minted at\n"
        "auth.atlassian.com instead of cf.mcp.atlassian.com — re-run\n"
        "`python dcr_register.py --force`.\n"
    )


if __name__ == "__main__":
    main()
