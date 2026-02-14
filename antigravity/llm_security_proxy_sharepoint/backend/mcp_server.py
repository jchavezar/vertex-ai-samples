import os
import json
from fastmcp import FastMCP
from mcp_sharepoint import SharePointMCP

# Initialize MCP Server
mcp = FastMCP(
    "SharePoint Security Proxy MCP"
)

# Initialize the internal logic
# Env vars are expected to be set for the container
sharepoint = SharePointMCP()

@mcp.tool()
def search_sharepoint(query: str, limit: int = 5) -> str:
    """
    Search SharePoint documents for matching content using the Microsoft Graph API.
    
    Args:
        query: The search keywords or phrases. Use '*' for all documents.
        limit: Max number of documents to return.
    """
    try:
        results = sharepoint.search_documents(query, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching SharePoint: {str(e)}"

@mcp.tool()
def read_document_content(item_id: str) -> str:
    """
    Reads the full text content of a specified SharePoint document (e.g. PDF, Word).
    
    Args:
        item_id: The unique identifier of the file from SharePoint.
    """
    try:
        return sharepoint.get_document_content(item_id)
    except Exception as e:
        return f"Error reading document: {str(e)}"

if __name__ == "__main__":
    # Always use streamable-http for Cloud Run
    import os
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    port = int(os.environ.get("PORT", 8080))
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    
    mcp.run(transport="sse", port=port, host="0.0.0.0", middleware=middleware)
