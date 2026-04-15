"""
Download SharePoint documents for MCP benchmark caching.

Uses MSAL device code flow with the ms365 MCP app registration.
Run once to download all documents, then mcp_bench.py uses the cached files.

Usage:
    uv run python download_docs.py
"""

import os, sys, msal, httpx
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "sharepoint_mcp" / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_ID = os.environ.get("MS365_CLIENT_ID", "")
TENANT_ID = os.environ.get("MS365_TENANT_ID", "")

DRIVE_ID = os.environ.get("SHAREPOINT_DRIVE_ID", "")
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

DOCUMENTS = [
    "01_Financial_Audit_Report_FY2024.pdf",
    "03_Client_Contract_Apex_Financial.pdf",
    "04_IT_Security_Assessment_2024.pdf",
    "05_MA_Due_Diligence_Project_Starlight.pdf",
    "Governance_Risk_Advisory_Report_FY2024.docx",
]

SCOPES = ["Files.Read.All", "Sites.Read.All"]


def get_token() -> str:
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    )

    # Try silent first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("  Using cached token")
            return result["access_token"]

    # Device code flow
    flow = app.initiate_device_flow(SCOPES)
    print(f"\n  {flow['message']}\n")
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print(f"  Auth failed: {result.get('error_description', 'unknown error')}")
        sys.exit(1)

    return result["access_token"]


def download_all(token: str):
    headers = {"Authorization": f"Bearer {token}"}

    for doc in DOCUMENTS:
        cache_path = CACHE_DIR / doc
        if cache_path.exists():
            print(f"  [cached] {doc} ({cache_path.stat().st_size:,} bytes)")
            continue

        print(f"  [download] {doc}...", end=" ", flush=True)
        endpoint = f"{GRAPH_BASE}/drives/{DRIVE_ID}/root:/{doc}:/content"

        with httpx.Client(follow_redirects=True, timeout=30) as client:
            resp = client.get(endpoint, headers=headers)
            resp.raise_for_status()
            cache_path.write_bytes(resp.content)
            print(f"✓ ({len(resp.content):,} bytes)")


def main():
    print("\n  SharePoint Document Downloader")
    print("  " + "=" * 40)

    token = get_token()
    download_all(token)

    print(f"\n  All documents cached in {CACHE_DIR}")
    print(f"  Run: uv run python mcp_bench.py")


if __name__ == "__main__":
    main()
