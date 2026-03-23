import os
import logging
from fastmcp import FastMCP

# We import the mcp instance directly from mcp_server
# Note: In the container, we need to ensure the python path includes the backend dir
from mcp_service.mcp_server import mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server_sharepoint_sse")

if __name__ == "__main__":
    # Get port from environment (Cloud Run sets this to 8080 by default)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting SharePoint MCP SSE server on port {port}")
    
    # Run using SSE transport
    # Note: We set host to 0.0.0.0 for Cloud Run
    mcp.run(transport="sse", port=port, host="0.0.0.0")
