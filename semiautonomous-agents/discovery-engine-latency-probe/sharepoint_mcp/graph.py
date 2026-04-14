"""Microsoft Graph API client for SharePoint file operations."""

import httpx
from pathlib import Path

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# SharePoint site: Financial Document
SITE_ID = "REDACTED_SITE_ID"
DRIVE_ID = "REDACTED_DRIVE_ID"

CACHE_DIR = Path(__file__).parent / ".cache"

# Documents to download (root of the drive)
DOCUMENTS = [
    "01_Financial_Audit_Report_FY2024.pdf",
    "03_Client_Contract_Apex_Financial.pdf",
    "04_IT_Security_Assessment_2024.pdf",
    "05_MA_Due_Diligence_Project_Starlight.pdf",
    "Governance_Risk_Advisory_Report_FY2024.docx",
]


class GraphClient:
    def __init__(self, token: str = ""):
        self.token = token
        self._headers = {"Authorization": f"Bearer {token}"} if token else {}

    def download_file(self, filename: str) -> bytes:
        """Download a file from the SharePoint drive root."""
        # Check cache first
        cached = CACHE_DIR / filename
        if cached.exists():
            return cached.read_bytes()

        # Also check for pre-parsed .md version
        md_cached = CACHE_DIR / (Path(filename).stem + ".md")
        if md_cached.exists():
            return md_cached.read_bytes()

        if not self.token:
            raise FileNotFoundError(
                f"No cached file for {filename} and no auth token. "
                "Run: uv run python download_docs.py"
            )

        endpoint = f"{GRAPH_BASE}/drives/{DRIVE_ID}/root:/{filename}:/content"
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            resp = client.get(endpoint, headers=self._headers)
            resp.raise_for_status()
            # Cache the downloaded file
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(resp.content)
            return resp.content

    def download_all(self) -> dict[str, bytes]:
        """Download all benchmark documents. Returns {filename: bytes}.

        Skips files that are not cached and have no auth token.
        """
        results = {}
        for doc in DOCUMENTS:
            try:
                results[doc] = self.download_file(doc)
            except FileNotFoundError:
                pass  # Skip uncached files when no token
            except Exception as e:
                print(f"\n    ⚠ Skipping {doc}: {e}")
        return results
