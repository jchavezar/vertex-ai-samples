api_schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "description": "Represents a single financial transaction.",
        "properties": {
            "customer_name": {
                "type": "STRING",
                "description": "Name of the customer associated with the transaction, for demo purposes.",
                "example": "Alice Wonderland"
            },
            "account_name": {
                "type": "STRING",
                "description": "User-friendly name of the account involved in the transaction, for demo purposes.",
                "example": "Primary Checking"
            },
            "transaction_type": {
                "type": "STRING",
                "description": "Type of transaction (e.g., 'BUY', 'SELL', 'DEPOSIT', 'WITHDRAWAL', 'DIVIDEND').",
                "enum": [
                    "BUY",
                    "SELL",
                    "DEPOSIT",
                    "WITHDRAWAL",
                    "DIVIDEND"
                ],
                "example": "BUY"
            },
            "transaction_date": {
                "type": "STRING",
                "format": "date-time",
                "description": "Date and time when the transaction occurred.",
                "example": "2023-10-26T10:00:00Z"
            },
            "asset_class": {
                "type": "STRING",
                "description": "Category of the asset involved (e.g., 'EQUITY', 'BOND', 'ETF', 'CRYPTO', 'OPTION', 'ALTERNATIVE').",
                "enum": [
                    "EQUITY",
                    "BOND",
                    "ETF",
                    "CRYPTO",
                    "OPTION",
                    "ALTERNATIVE"
                ],
                "example": "EQUITY"
            },
            "symbol": {
                "type": "STRING",
                "description": "Ticker symbol or unique identifier of the asset (e.g., 'AAPL', 'BTC', 'GOOG').",
                "example": "AAPL"
            },
            "quantity": {
                "type": "NUMBER",
                "format": "float",
                "description": "Number of units of the asset involved in the transaction.",
                "example": 10.5
            },
            "price_per_unit": {
                "type": "NUMBER",
                "format": "float",
                "description": "Price per unit of the asset at the time of the transaction.",
                "example": 150.25
            },
            "amount": {
                "type": "NUMBER",
                "format": "float",
                "description": "Total monetary value of the transaction.",
                "example": 1577.63
            },
            "currency": {
                "type": "STRING",
                "description": "Currency in which the transaction was conducted (e.g., 'USD', 'EUR').",
                "enum": [
                    "USD",
                    "EUR",
                    "GBP",
                    "JPY",
                    "CAD"
                ],
                "example": "USD"
            },
            "status": {
                "type": "STRING",
                "description": "Current status of the transaction (e.g., 'COMPLETED', 'PENDING', 'FAILED', 'CANCELLED').",
                "enum": [
                    "COMPLETED",
                    "PENDING",
                    "FAILED",
                    "CANCELLED"
                ],
                "example": "COMPLETED"
            },
            "fee_amount": {
                "type": "NUMBER",
                "format": "float",
                "description": "Any fees charged for the transaction (e.g., regulatory fees, exchange fees).",
                "example": 2.50
            },
            "execution_venue": {
                "type": "STRING",
                "description": "The market or venue where the trade was executed (e.g., 'NYSE', 'NASDAQ', 'OTC').",
                "enum": [
                    "NYSE",
                    "NASDAQ",
                    "OTC",
                    "LSE",
                    "TSE"
                ],
                "example": "NASDAQ"
            },
            "order_type": {
                "type": "STRING",
                "description": "The type of order placed (e.g., 'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT').",
                "enum": [
                    "MARKET",
                    "LIMIT",
                    "STOP",
                    "STOP_LIMIT"
                ],
                "example": "MARKET"
            },
            "commission_amount": {
                "type": "NUMBER",
                "format": "float",
                "description": "Commission charged by the broker for executing the transaction, if applicable.",
                "example": 7.99
            },
            "settlement_date": {
                "type": "STRING",
                "format": "date",
                "description": "The date when the transaction is expected to be settled and funds/assets exchanged.",
                "example": "2023-10-28"
            },
            "correlation_id": {
                "type": "STRING",
                "description": "An identifier used to link multiple related transactions or to an originating order.",
                "example": "txn-12345-abcde"
            },
            "regulatory_reporting_status": {
                "type": "STRING",
                "description": "Status of the transaction's regulatory reporting requirements (e.g., 'REPORTED', 'PENDING_REPORT').",
                "enum": [
                    "REPORTED",
                    "PENDING_REPORT",
                    "EXEMPT"
                ],
                "example": "REPORTED"
            },
            "source_system": {
                "type": "STRING",
                "description": "The internal system or application that initiated or processed the transaction (e.g., 'OMS', 'InvestorApp', 'API').",
                "enum": [
                    "OMS",
                    "InvestorApp",
                    "API",
                    "BackOffice"
                ],
                "example": "InvestorApp"
            },
            "notes": {
                "type": "STRING",
                "description": "Any additional free-form notes or comments related to the transaction.",
                "nullable": True,
                "example": "Purchased for long-term hold."
            }
        },
        "required": [
            "customer_name",
            "account_name",
            "transaction_type",
            "transaction_date",
            "asset_class",
            "symbol",
            "quantity",
            "price_per_unit",
            "amount",
            "currency",
            "status",
            "fee_amount",
            "execution_venue",
            "order_type",
            "commission_amount",
            "settlement_date",
            "correlation_id",
            "regulatory_reporting_status",
            "source_system"
        ]
    }
}