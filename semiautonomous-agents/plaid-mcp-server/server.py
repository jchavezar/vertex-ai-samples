"""
Plaid Finance MCP Server

Provides access to bank accounts via Plaid:
- List and search transactions
- Detect recurring subscriptions
- View account balances
- Spending summaries by category
"""
import os
import logging
from fastmcp import FastMCP

from plaid_client import PlaidManager
from tools.transactions import register_transaction_tools
from tools.accounts import register_account_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plaid-mcp")

# Initialize FastMCP server
mcp = FastMCP("Plaid Finance MCP")

# Initialize Plaid manager
plaid_manager = PlaidManager(
    client_id=os.getenv("PLAID_CLIENT_ID", ""),
    secret=os.getenv("PLAID_SECRET", ""),
    env=os.getenv("PLAID_ENV", "sandbox"),
)


@mcp.tool()
def plaid_connect() -> str:
    """
    Start the Plaid Link process to connect a bank account.
    Returns a link token to use with Plaid Link.

    For Sandbox testing, use: username 'user_good', password 'pass_good'
    """
    try:
        link_data = plaid_manager.create_link_token()

        return f"""## Connect Bank Account

**Link Token:** `{link_data['link_token']}`
**Expires:** {link_data['expiration']}

### How to connect:

**Option 1 — Plaid Quickstart (recommended for testing):**
1. Go to the Plaid Quickstart page in your dashboard
2. Use the link token above

**Option 2 — Direct API call:**
Open this in a browser or use the Plaid Link SDK with the token above.

**Sandbox credentials:** username `user_good`, password `pass_good`

After connecting, run `plaid_exchange_token` with the public_token you receive.
"""
    except Exception as e:
        logger.error(f"Link token creation failed: {e}")
        return f"Error creating link token: {str(e)}"


@mcp.tool()
def plaid_exchange_token(public_token: str) -> str:
    """
    Exchange a public token from Plaid Link for an access token.

    Args:
        public_token: The public_token received after completing Plaid Link
    """
    try:
        result = plaid_manager.exchange_public_token(public_token)
        if result:
            accounts = plaid_manager.state.accounts
            account_list = "\n".join(
                f"- **{acc['name']}** ({acc['type']}) ****{acc['mask']}"
                for acc in accounts
            )
            return f"""## Connected Successfully!

**Institution:** {plaid_manager.state.institution_name or 'Connected'}

### Linked Accounts:
{account_list}

You can now use:
- `plaid_list_transactions` — View recent transactions
- `plaid_find_subscriptions` — Detect recurring charges
- `plaid_search_transactions` — Search by merchant
- `plaid_spending_summary` — Category breakdown
- `plaid_get_balances` — Account balances
"""
        else:
            return "Token exchange failed. Check the public_token and try again."
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return f"Error exchanging token: {str(e)}"


@mcp.tool()
def plaid_status() -> str:
    """Check current Plaid connection status."""
    if plaid_manager.is_connected():
        accounts = plaid_manager.state.accounts
        account_list = "\n".join(
            f"- **{acc['name']}** ({acc['type']}) ****{acc['mask']}"
            for acc in accounts
        )
        return f"""## Connected

**Institution:** {plaid_manager.state.institution_name or 'Unknown'}
**Environment:** {plaid_manager.env}

### Accounts:
{account_list}
"""
    else:
        return f"Not connected. Environment: {plaid_manager.env}. Run `plaid_connect` to link a bank account."


@mcp.tool()
def plaid_disconnect() -> str:
    """Disconnect from Plaid and clear stored tokens."""
    plaid_manager.disconnect()
    return "Disconnected successfully."


# Register tool modules
register_transaction_tools(mcp, plaid_manager)
register_account_tools(mcp, plaid_manager)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")

    logger.info(f"Starting Plaid Finance MCP Server on port {port}")
    logger.info(f"Transport: {transport}")
    logger.info(f"Plaid environment: {plaid_manager.env}")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        mcp.run()
