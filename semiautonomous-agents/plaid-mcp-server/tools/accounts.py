"""
Account Tools for Plaid MCP Server
"""
import logging

logger = logging.getLogger("plaid-mcp.accounts")


def register_account_tools(mcp, plaid_manager):
    """Register account tools with the MCP server."""

    @mcp.tool()
    def plaid_get_accounts() -> str:
        """List all connected bank accounts with details."""
        try:
            accounts = plaid_manager.get_accounts()

            if not accounts:
                return "No accounts found."

            results = []
            results.append("## Connected Accounts\n")

            for acc in accounts:
                name = acc["official_name"] or acc["name"]
                results.append(
                    f"- **{name}** ({acc['type']}/{acc['subtype']})\n"
                    f"  - Mask: ****{acc['mask']}\n"
                )

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Accounts error: {e}")
            return f"Error getting accounts: {str(e)}"

    @mcp.tool()
    def plaid_get_balances() -> str:
        """Get current balances for all connected accounts."""
        try:
            balances = plaid_manager.get_balances()

            if not balances:
                return "No accounts found."

            results = []
            results.append("## Account Balances\n")
            results.append("| Account | Type | Current | Available | Limit |")
            results.append("|---------|------|---------|-----------|-------|")

            for bal in balances:
                current = f"${bal['current']:,.2f}" if bal["current"] is not None else "N/A"
                available = f"${bal['available']:,.2f}" if bal["available"] is not None else "N/A"
                limit = f"${bal['limit']:,.2f}" if bal["limit"] is not None else "N/A"
                currency = bal["currency"] or "USD"

                results.append(
                    f"| {bal['name']} (****{bal['mask']}) | {bal['type']} | "
                    f"{current} | {available} | {limit} |"
                )

            return "\n".join(results)

        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Balances error: {e}")
            return f"Error getting balances: {str(e)}"
