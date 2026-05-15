"""FastMCP StreamableHTTP server exposing the Firestore knowledge base as MCP tools.

Endpoints:
  GET  /healthz   — unauthenticated health check
  *    /mcp/      — MCP streamable-HTTP transport (auth required)

Tools:
  search_docs(query, top_k)   — semantic vector search across PDFs
  list_documents()            — list distinct PDFs in the collection
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
    "firestore-rag-mcp",
    instructions=(
        "Use search_docs to retrieve grounded passages from the indexed PDF knowledge base "
        "(returns text + PDF URI + page). Use list_documents to enumerate the corpus."
    ),
    stateless_http=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8080")),
)


@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search over the indexed PDF knowledge base.

    Args:
        query: Natural-language question or keywords.
        top_k: Number of chunks to return (1-25, default 5).

    Returns:
        List of {id, text, pdf_name, page, pdf_uri, citation} ordered by relevance.
    """
    return vector_search(query, top_k)


@mcp.tool()
def list_documents() -> list[dict]:
    """List the distinct PDFs currently indexed (name, gs URI, page count)."""
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
