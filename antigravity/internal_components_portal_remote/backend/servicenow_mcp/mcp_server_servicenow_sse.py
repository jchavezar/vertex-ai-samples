import os
import logging
from fastmcp import FastMCP
from mcp_server_servicenow import mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server_servicenow_sse")

if __name__ == "__main__":
    # Get port from environment (Cloud Run sets this to 8080 by default)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting ServiceNow MCP SSE server on port {port}")
    
    # Run using SSE transport
    mcp.run(transport="sse", port=port, host="0.0.0.0")
