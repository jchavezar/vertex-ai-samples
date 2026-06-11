"""FastMCP StreamableHTTP server exposing the Firestore RAG system.

Exposes high-fidelity grounding tools to Gemini Enterprise.

Endpoints:
  GET  /healthz   — unauthenticated health check
  *    /mcp/      — MCP streamable-HTTP transport (auth required)
"""
from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

from auth import GoogleBearerAuth
from firestore_search import list_pdfs, vector_search

mcp = FastMCP(
    "docparse-firestore-mcp",
    instructions=(
        "Use search_docs to perform high-fidelity semantic vector searches over the PDF corpus. "
        "Each result contains text, a citation, GCS PDF URI, and HTTPS PDF URL grounding links. "
        "Use list_documents to list distinct PDF files currently indexed."
    ),
    stateless_http=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8080")),
)


@mcp.tool()
def search_docs(query: str, page: str | None = None, pdf_name: str | None = None, top_k: int = 5) -> list[dict]:
    """Semantic vector search over the docparse PDF knowledge base with optional page/document filtering.

    Args:
        query: Natural language question or search query.
        page: Optional logical/printed page number filter (e.g. '1', 'ix', '9').
        pdf_name: Optional document name substring filter (case-insensitive, e.g. 'accenture').
        top_k: Number of relevant chunks to retrieve (1-25, default 5).

    Returns:
        List of chunks with text, PDF name, page number, GCS URI, HTTPS grounding URL, and position indicators.
    """
    return vector_search(query=query, page=page, pdf_name=pdf_name, top_k=top_k)


@mcp.tool()
def list_documents() -> list[dict]:
    """List the distinct PDF documents indexed in the Firestore RAG database."""
    return list_pdfs()


async def healthz(request):
    return PlainTextResponse("ok")


def build_app() -> Starlette:
    mcp_app = mcp.streamable_http_app()
    app = Starlette(
        routes=[
            Route("/healthz", healthz),
            Mount("/", app=mcp_app),
        ],
        lifespan=mcp_app.router.lifespan_context,
    )
    app.add_middleware(GoogleBearerAuth)
    return app


app = build_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
