"""Minimal legacy-dms MCP server. FastMCP mounted at /mcp.

Two tools:
  - list_documents: returns the catalog (read-only — good target for a CEL condition).
  - get_document: returns a single document by id.

Nothing here talks to a real DMS. The point is to exercise the gateway path.
"""

from __future__ import annotations

import os
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("legacy-dms")

_CATALOG: dict[str, dict[str, Any]] = {
    "DMS-001": {"title": "Loan agreement template v3", "owner": "ops@example.com", "pages": 12},
    "DMS-002": {"title": "Income verification SOP",      "owner": "ops@example.com", "pages": 4},
    "DMS-003": {"title": "Customer onboarding checklist", "owner": "ops@example.com", "pages": 2},
}


@mcp.tool(annotations={"iap.googleapis.com/mcp.tool.isReadOnly": True})
def list_documents() -> list[dict[str, Any]]:
    """List every document in the legacy DMS catalog. Read-only."""
    return [{"id": k, **v} for k, v in _CATALOG.items()]


@mcp.tool(annotations={"iap.googleapis.com/mcp.tool.isReadOnly": True})
def get_document(document_id: str) -> dict[str, Any]:
    """Fetch one document by ID. Read-only."""
    doc = _CATALOG.get(document_id)
    if not doc:
        return {"error": f"no document with id {document_id}"}
    return {"id": document_id, **doc}


# FastMCP exposes an HTTP app at /mcp; uvicorn entrypoint serves it on :8080.
app = mcp.http_app(path="/mcp")


if __name__ == "__main__":  # local sanity run
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
