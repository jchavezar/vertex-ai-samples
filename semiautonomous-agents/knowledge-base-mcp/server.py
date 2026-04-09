"""Knowledge Base MCP Server.

Semantic search over Claude Code conversation transcripts.
Supports cleaning, extraction, and retrieval of problem-solution patterns.
"""

import os
import logging
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("knowledge-base-mcp")

# Initialize FastMCP server
mcp = FastMCP("Knowledge Base MCP Server")

# Initialize shared services (lazy)
from firestore_client import FirestoreClient
import embeddings as embedding_service

firestore_client = FirestoreClient()

# Register tools
from tools.search import register_search_tools
from tools.ingest import register_ingest_tools
from tools.stats import register_stats_tools
from tools.manage import register_manage_tools

register_search_tools(mcp, firestore_client, embedding_service)
register_ingest_tools(mcp, firestore_client, embedding_service)
register_stats_tools(mcp, firestore_client)
register_manage_tools(mcp, firestore_client)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")

    logger.info("[MCP] Starting Knowledge Base MCP Server")
    logger.info(f"[MCP] Transport: {transport}")
    logger.info(f"[MCP] Port: {port}")

    mcp.run(
        transport=transport,
        host="0.0.0.0",
        port=port,
    )
