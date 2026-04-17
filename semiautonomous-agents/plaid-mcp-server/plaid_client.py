"""
Plaid API Client Manager
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

logger = logging.getLogger("plaid-mcp.client")

PLAID_ENVS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": "https://development.plaid.com",
    "production": plaid.Environment.Production,
}


@dataclass
class ConnectionState:
    """Holds the current Plaid connection state."""
    access_token: Optional[str] = None
    item_id: Optional[str] = None
    institution_name: Optional[str] = None
    accounts: List[Dict[str, Any]] = field(default_factory=list)


class PlaidManager:
    """Manages Plaid API connections and data retrieval."""

    def __init__(self, client_id: str, secret: str, env: str = "sandbox"):
        self.client_id = client_id
        self.secret = secret
        self.env = env
        self.state = ConnectionState()

        configuration = plaid.Configuration(
            host=PLAID_ENVS.get(env, plaid.Environment.Sandbox),
            api_key={
                "clientId": client_id,
                "secret": secret,
            },
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def create_link_token(self) -> Dict[str, str]:
        """Create a Link token for Plaid Link initialization."""
        try:
            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="Plaid MCP Server",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(client_user_id="mcp-user"),
            )
            response = self.client.link_token_create(request)
            return {
                "link_token": response.link_token,
                "expiration": str(response.expiration),
            }
        except Exception as e:
            logger.error(f"Link token creation failed: {e}")
            raise

    def exchange_public_token(self, public_token: str) -> bool:
        """Exchange a public token from Link for an access token."""
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token,
            )
            response = self.client.item_public_token_exchange(request)
            self.state.access_token = response.access_token
            self.state.item_id = response.item_id

            # Fetch accounts to store connection info
            self._fetch_accounts()
            logger.info("Plaid connection established")
            return True
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return False

    def _fetch_accounts(self):
        """Fetch and cache account information."""
        if not self.state.access_token:
            return
        try:
            request = AccountsGetRequest(access_token=self.state.access_token)
            response = self.client.accounts_get(request)
            self.state.accounts = [
                {
                    "id": acc.account_id,
                    "name": acc.name,
                    "official_name": acc.official_name,
                    "type": str(acc.type),
                    "subtype": str(acc.subtype) if acc.subtype else None,
                    "mask": acc.mask,
                }
                for acc in response.accounts
            ]
            item = response.item
            self.state.institution_name = item.institution_id
        except Exception as e:
            logger.error(f"Failed to fetch accounts: {e}")

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """Get transactions for a date range. Handles pagination."""
        if not self.state.access_token:
            raise ValueError("Not connected. Run plaid_connect first.")

        transactions = []
        offset = 0
        batch_size = 100

        while True:
            request = TransactionsGetRequest(
                access_token=self.state.access_token,
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
                options=TransactionsGetRequestOptions(
                    count=batch_size,
                    offset=offset,
                ),
            )
            response = self.client.transactions_get(request)

            for txn in response.transactions:
                transactions.append({
                    "date": str(txn.date),
                    "name": txn.name,
                    "merchant_name": txn.merchant_name,
                    "amount": txn.amount,
                    "category": txn.category,
                    "pending": txn.pending,
                    "account_id": txn.account_id,
                })

            if len(transactions) >= response.total_transactions:
                break
            offset += batch_size

        return transactions

    def get_accounts(self) -> List[Dict]:
        """Get linked account information."""
        if not self.state.access_token:
            raise ValueError("Not connected. Run plaid_connect first.")

        request = AccountsGetRequest(access_token=self.state.access_token)
        response = self.client.accounts_get(request)
        return [
            {
                "name": acc.name,
                "official_name": acc.official_name,
                "type": str(acc.type),
                "subtype": str(acc.subtype) if acc.subtype else None,
                "mask": acc.mask,
            }
            for acc in response.accounts
        ]

    def get_balances(self) -> List[Dict]:
        """Get account balances."""
        if not self.state.access_token:
            raise ValueError("Not connected. Run plaid_connect first.")

        request = AccountsBalanceGetRequest(access_token=self.state.access_token)
        response = self.client.accounts_balance_get(request)
        return [
            {
                "name": acc.name,
                "type": str(acc.type),
                "mask": acc.mask,
                "available": acc.balances.available,
                "current": acc.balances.current,
                "limit": acc.balances.limit,
                "currency": acc.balances.iso_currency_code,
            }
            for acc in response.accounts
        ]

    def is_connected(self) -> bool:
        """Check if we have a valid access token."""
        return self.state.access_token is not None

    def disconnect(self):
        """Clear connection state."""
        self.state = ConnectionState()
