"""MCP Server — exposes Amex statement data and AI-enriched analytics as tools."""

import logging
import os
import sys

# Add parent dir so we can import amex_job and enrichment packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError("Install fastmcp: pip install fastmcp")

from tools import statements, ingestion, categories, subscriptions, insights, search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amex-mcp-server")

mcp = FastMCP(
    "amex-statements",
    instructions=(
        "Query and analyze American Express credit card statements. "
        "Data is enriched with AI-powered categorization, subscription detection, "
        "Gmail receipt matching for ambiguous charges, and spending insights. "
        "Statements are synced automatically on the 1st of each month."
    ),
)

# Register all tool modules
statements.register(mcp)
ingestion.register(mcp)
categories.register(mcp)
subscriptions.register(mcp)
insights.register(mcp)
search.register(mcp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")

    logger.info(f"Starting Amex MCP Server on port {port}")
    logger.info(f"Transport: {transport}")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        mcp.run()
