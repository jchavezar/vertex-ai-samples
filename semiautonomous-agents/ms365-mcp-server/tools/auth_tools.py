"""
Authentication Tools for Microsoft 365 MCP Server
"""
import logging
from auth import get_auth_manager, get_pending_flow, set_pending_flow

logger = logging.getLogger("ms365-mcp.tools.auth")


def login() -> str:
    """
    Start the Microsoft 365 login process using device code flow.

    Returns instructions for the user to complete authentication.
    After authenticating in the browser, call 'complete_login' to finish.
    """
    try:
        auth_manager = get_auth_manager()

        # Check if already authenticated
        if auth_manager.is_authenticated():
            account = auth_manager.get_account_info()
            return f"Already logged in as: {account.get('username', 'Unknown')}\n\nTo switch accounts, run 'logout' first."

        # Start device code flow
        flow = auth_manager.start_device_code_flow()
        set_pending_flow(flow)

        user_code = flow.get("user_code", "")
        verification_uri = flow.get("verification_uri", "https://microsoft.com/devicelogin")

        return f"""## Microsoft 365 Login

**Step 1:** Open this URL in your browser:
{verification_uri}

**Step 2:** Enter this code:
`{user_code}`

**Step 3:** Sign in with your Microsoft 365 account

**Step 4:** After signing in, run the `complete_login` tool to finish authentication."""

    except Exception as e:
        logger.error(f"[Auth] Login failed: {e}")
        return f"Login failed: {str(e)}"


def complete_login() -> str:
    """
    Complete the Microsoft 365 login after user has authenticated in browser.

    Must be called after 'login' and after user has completed browser authentication.
    """
    try:
        flow = get_pending_flow()
        if not flow:
            return "No pending login. Please run 'login' first to start authentication."

        auth_manager = get_auth_manager()
        account = auth_manager.complete_device_code_flow(flow)
        set_pending_flow(None)

        return f"""## Login Successful!

**Account:** {account.get('username', 'Unknown')}
**Name:** {account.get('name', 'Unknown')}

You can now use Microsoft 365 tools to access your:
- SharePoint sites and documents
- OneDrive files
- Outlook mail
- Calendar events
- Teams channels and chats"""

    except Exception as e:
        logger.error(f"[Auth] Complete login failed: {e}")
        set_pending_flow(None)
        return f"Login completion failed: {str(e)}\n\nPlease run 'login' again to restart."


def logout() -> str:
    """
    Log out from Microsoft 365 and clear all cached tokens.
    """
    try:
        auth_manager = get_auth_manager()
        account = auth_manager.get_account_info()
        username = account.get("username", "Unknown") if account else "Unknown"

        auth_manager.logout()
        set_pending_flow(None)

        return f"Logged out successfully. Cleared tokens for: {username}"

    except Exception as e:
        logger.error(f"[Auth] Logout failed: {e}")
        return f"Logout failed: {str(e)}"


def verify_login() -> str:
    """
    Verify current Microsoft 365 authentication status.
    """
    try:
        auth_manager = get_auth_manager()

        if not auth_manager.is_authenticated():
            return "Not logged in. Run 'login' to authenticate with Microsoft 365."

        account = auth_manager.get_account_info()
        return f"""## Authentication Status: Active

**Account:** {account.get('username', 'Unknown')}
**Name:** {account.get('name', 'Unknown')}
**Tenant:** {account.get('tenant_id', 'Unknown')}"""

    except Exception as e:
        logger.error(f"[Auth] Verify login failed: {e}")
        return f"Status check failed: {str(e)}"
