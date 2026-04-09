import os
import json
import logging
from typing import Optional, List, Dict
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from mcp_sharepoint import SharePointMCP

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_sharepoint_server")

# Initialize FastMCP
mcp = FastMCP("SharePoint-MCP")


def _extract_token_from_context(ctx: Context) -> Optional[str]:
    headers = None
    if ctx and hasattr(ctx, "request_context") and ctx.request_context:
        request = getattr(ctx.request_context, "request", None)
        if request and hasattr(request, "headers"):
            headers = request.headers
    if headers is None:
        try:
            from fastmcp.server.dependencies import get_http_request
            http_request = get_http_request()
            headers = http_request.headers
        except Exception:
            pass

    if headers is None:
        return None

    user_token = headers.get("x-user-token") or headers.get("X-User-Token")
    if user_token and user_token.startswith("eyJ"):
        return user_token

    auth_header = headers.get("authorization") or headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        if token.startswith("eyJ"):
            return token

    return None

def _get_sharepoint_client(ctx: Context = None) -> SharePointMCP:
    token = _extract_token_from_context(ctx)
    if not token:
        logger.warning("No token found. Attempting to use local environment fallback for testing if available, otherwise expects delegated token.")
        # If testing locally, might use an env var token.
        token = os.environ.get("LOCAL_TEST_TOKEN")
        if not token:
            raise ValueError("No authentication credentials available in context.")
    return SharePointMCP(token=token)

@mcp.tool()
def search_documents(query: str, limit: int = 5, ctx: Context = None) -> str:
    """
    Search SharePoint for documents using a text query.
    """
    try:
        sp = _get_sharepoint_client(ctx)
        docs = sp.search_documents(query=query, limit=limit)
        if not docs:
            return "No documents found matching the query."
        output = f"### Found {len(docs)} documents\n\n"
        for d in docs:
            output += f"- **{d.get('name')}** (ID: `{d.get('id')}`)\n  Link: {d.get('webUrl')}\n  Summary: {d.get('summary', 'N/A')}\n"
        return output
    except Exception as e:
        logger.error(f"search_documents error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def read_document(item_id: str, ctx: Context = None) -> str:
    """
    Read the extracted markdown content of a document by its item ID.
    """
    try:
        sp = _get_sharepoint_client(ctx)
        content = sp.get_document_content(item_id)
        return content
    except Exception as e:
        logger.error(f"read_document error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def list_folder_contents(folder_id: str = "root", ctx: Context = None) -> str:
    """
    List contents of a SharePoint folder. Default is 'root'.
    """
    try:
        sp = _get_sharepoint_client(ctx)
        items = sp.list_folder_contents(folder_id)
        if not items:
            return f"Folder {folder_id} is empty."
        output = f"### Folder: {folder_id}\n"
        for i in items:
            output += f"- [{i['type'].upper()}] {i['name']} (ID: `{i['id']}`)\n"
        return output
    except Exception as e:
        logger.error(f"list_folder_contents error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def update_document(item_id: str, content: str, ctx: Context = None) -> str:
    """
    Update the text content of a document on SharePoint (creates a backup automatically).
    """
    try:
        sp = _get_sharepoint_client(ctx)
        sp.update_document_content(item_id, content)
        return f"Document {item_id} successfully updated."
    except Exception as e:
        logger.error(f"update_document error: {e}")
        return f"Error updating document: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    logger.info(f"Starting SharePoint MCP Server on port {port} via {transport}")
    mcp.run(transport=transport, host="0.0.0.0", port=port)
