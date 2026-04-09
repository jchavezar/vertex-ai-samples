"""
Google Workspace MCP Server

Provides access to Google Workspace APIs:
- Gmail (read, send, search emails)
- Google Drive (list, upload, download files)
- Google Calendar (list, create, delete events)
- Google Docs (read, create documents)
- Google Sheets (read, write spreadsheets)
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastmcp import FastMCP

from auth import GoogleAuthManager
from tools.gmail import register_gmail_tools
from tools.drive import register_drive_tools
from tools.calendar import register_calendar_tools
from tools.docs import register_docs_tools
from tools.sheets import register_sheets_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gworkspace-mcp")

# Initialize FastMCP server
mcp = FastMCP("Google Workspace MCP")

# Initialize auth manager
auth_manager = GoogleAuthManager(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),  # Optional for TVs type
)


@mcp.tool()
def gworkspace_login() -> str:
    """
    Start the Google Workspace login process.
    Returns a URL that the user must open to authenticate.
    """
    try:
        auth_data = auth_manager.start_auth_flow()

        return f"""## Google Workspace Login

**Step 1:** Open this URL in your browser:
{auth_data['auth_url']}

**Step 2:** Sign in with your Google Workspace account and grant permissions

**Step 3:** After granting permissions, Google will show you an authorization code. Copy it.

**Step 4:** Run the `gworkspace_complete_login` tool with the code:
```
gworkspace_complete_login(code="paste-your-code-here")
```
"""
    except Exception as e:
        logger.error(f"Login start failed: {e}")
        return f"Error starting login: {str(e)}"


@mcp.tool()
def gworkspace_complete_login(code: str) -> str:
    """
    Complete the Google Workspace login with the authorization code.

    Args:
        code: The authorization code from Google after signing in
    """
    try:
        result = auth_manager.exchange_code(code)
        if result:
            user_info = auth_manager.get_user_info()
            return f"""## Login Successful!

**Account:** {user_info.get('email', 'Unknown')}
**Name:** {user_info.get('name', 'Unknown')}

You can now use Google Workspace tools to access your:
- Gmail messages
- Google Drive files
- Calendar events
- Google Docs
- Google Sheets
"""
        else:
            return "Login failed. Please check the authorization code and try again."
    except Exception as e:
        logger.error(f"Login completion failed: {e}")
        return f"Error completing login: {str(e)}"


@mcp.tool()
def gworkspace_verify_login() -> str:
    """Verify current Google Workspace authentication status."""
    if auth_manager.is_authenticated():
        user_info = auth_manager.get_user_info()
        return f"""## Authenticated

**Account:** {user_info.get('email', 'Unknown')}
**Name:** {user_info.get('name', 'Unknown')}
**Token expires:** {auth_manager.get_token_expiry()}
"""
    else:
        return "Not authenticated. Please run `gworkspace_login` first."


@mcp.tool()
def gworkspace_logout() -> str:
    """Log out from Google Workspace and clear tokens."""
    auth_manager.logout()
    return "Logged out successfully."


# Register all tool modules
register_gmail_tools(mcp, auth_manager)
register_drive_tools(mcp, auth_manager)
register_calendar_tools(mcp, auth_manager)
register_docs_tools(mcp, auth_manager)
register_sheets_tools(mcp, auth_manager)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")

    logger.info(f"Starting Google Workspace MCP Server on port {port}")
    logger.info(f"Transport: {transport}")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        mcp.run()
