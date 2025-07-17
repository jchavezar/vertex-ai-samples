#%%
import json
import pandas as pd
from google import genai
from google.genai import types
from google.cloud import bigquery

project_id = "vtxdemos"

gem_client = genai.Client(
    vertexai=True,
    project=project_id,
    location="us-central1",
)

bq_client = bigquery.Client(
    project=project_id
)

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE"
)

# Transactions Fintech Data
## Synthetic schema to generate a synthetic table
transactions_schema = [
    {"name": "customer_name", "type": "STRING", "description": "Name of the customer associated with the transaction, for demo purposes."},
    {"name": "account_name", "type": "STRING", "description": "User-friendly name of the account involved in the transaction, for demo purposes."},
    {"name": "transaction_type", "type": "STRING", "description": "Type of transaction (e.g., 'BUY', 'SELL', 'DEPOSIT', 'WITHDRAWAL', 'DIVIDEND')."},
    {"name": "transaction_date", "type": "TIMESTAMP", "description": "Date and time when the transaction occurred."},
    {"name": "asset_class", "type": "STRING", "description": "Category of the asset involved (e.g., 'EQUITY', 'BOND', 'ETF', 'CRYPTO', 'OPTION', 'ALTERNATIVE')."},
    {"name": "symbol", "type": "STRING", "description": "Ticker symbol or unique identifier of the asset (e.g., 'AAPL', 'BTC', 'GOOG')."},
    {"name": "quantity", "type": "NUMERIC", "description": "Number of units of the asset involved in the transaction."},
    {"name": "price_per_unit", "type": "NUMERIC", "description": "Price per unit of the asset at the time of the transaction."},
    {"name": "amount", "type": "NUMERIC", "description": "Total monetary value of the transaction."},
    {"name": "currency", "type": "STRING", "description": "Currency in which the transaction was conducted (e.g., 'USD', 'EUR')."},
    {"name": "status", "type": "STRING", "description": "Current status of the transaction (e.g., 'COMPLETED', 'PENDING', 'FAILED', 'CANCELLED')."},
    {"name": "fee_amount", "type": "NUMERIC", "description": "Any fees charged for the transaction (e.g., regulatory fees, exchange fees)."},
    {"name": "execution_venue", "type": "STRING", "description": "The market or venue where the trade was executed (e.g., 'NYSE', 'NASDAQ', 'OTC')."},
    {"name": "order_type", "type": "STRING", "description": "The type of order placed (e.g., 'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')."},
    {"name": "commission_amount", "type": "NUMERIC", "description": "Commission charged by the broker for executing the transaction, if applicable."},
    {"name": "settlement_date", "type": "DATE", "description": "The date when the transaction is expected to be settled and funds/assets exchanged."},
    {"name": "correlation_id", "type": "STRING", "description": "An identifier used to link multiple related transactions or to an originating order."},
    {"name": "regulatory_reporting_status", "type": "STRING", "description": "Status of the transaction's regulatory reporting requirements (e.g., 'REPORTED', 'PENDING_REPORT')."},
    {"name": "source_system", "type": "STRING", "description": "The internal system or application that initiated or processed the transaction (e.g., 'OMS', 'InvestorApp', 'API')."},
    {"name": "notes", "type": "STRING", "description": "Any additional free-form notes or comments related to the transaction."}
]

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

system_instruction = """
Your main mission is to generate reliable synthetic tables based on the schema provided.
- A 60% of randomness is important or whatever you think is best to create a table close to reality.
- Repeating identifiers are also important to do some sql operation for example, aggregations over specific 
customers or account_name.
- Be creative with names (close to reality)

Output in json format .
"""

config = types.GenerateContentConfig(
    max_output_tokens=65535,
    system_instruction=system_instruction,
    response_mime_type="application/json",
    response_schema=api_schema
)

#%%
## Generate Synthetic Table
table_id = "vtxdemos.demos.fintech_data"

re = gem_client.models.generate_content(
    model="gemini-2.5-pro",
    config=config,
    contents=f"From the following schema create 200 rows: {transactions_schema}"
)

df = pd.DataFrame(json.loads(re.text))

## Load into BigQuery
job = bq_client.load_table_from_dataframe(
    df, table_id, job_config=job_config
)

#%%
# Transactions Fintech Semantic KnowledgeBase
semantic_search_documents_schema = [
    {"name": "document_id", "type": "STRING", "description": "Unique identifier for the document."},
    {"name": "title", "type": "STRING", "description": "Title or headline of the document/content."},
    {"name": "category", "type": "STRING", "description": "Category or topic of the content (e.g., 'Market News', 'Regulatory Update', 'Product Guide')."},
    {"name": "publish_date", "type": "DATE", "description": "Date when the content was published or last updated."},
    {"name": "source", "type": "STRING", "description": "Origin of the document (e.g., 'Internal Research', 'Bloomberg', 'Customer Chat')."},
    {"name": "content_text", "type": "STRING", "description": "The main, longer text content of the document from which embeddings would be generated."},
    {"name": "embedding_vector", "type": "ARRAY<FLOAT>", "description": "The pre-computed embedding vector of the 'content_text' field, used for similarity search. (This would be generated by an ML model)."}
]

api_schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "description": "Represents a single document or long text segment for semantic search within a financial context.",
        "properties": {
            "document_id": {
                "type": "STRING",
                "description": "Unique identifier for the document.",
                "example": "DOC001"
            },
            "title": {
                "type": "STRING",
                "description": "Title or headline of the document/content.",
                "example": "Fed Hints at Rate Hold Amidst Inflation Concerns"
            },
            "category": {
                "type": "STRING",
                "description": "Category or topic of the content.",
                "enum": [
                    "Market News",
                    "Regulatory Update",
                    "Product Guide",
                    "Company Analysis",
                    "Economic Report",
                    "Customer Support"
                ],
                "example": "Market News"
            },
            "publish_date": {
                "type": "STRING",
                "format": "date",
                "description": "Date when the content was published or last updated.",
                "example": "2025-07-01"
            },
            "source": {
                "type": "STRING",
                "description": "Origin of the document.",
                "enum": [
                    "Reuters",
                    "Internal Research",
                    "SEC Filings",
                    "Apex Support Portal",
                    "IMF Report",
                    "Customer Chat Transcript"
                ],
                "example": "Reuters"
            },
            "content_text": {
                "type": "STRING",
                "description": "The main, longer text content of the document from which embeddings would be generated.",
                "example": "The Federal Reserve's latest statement suggests a cautious approach to interest rate adjustments, indicating a potential pause in hikes despite persistent inflation pressures. Analysts are closely watching upcoming CPI data for further cues on monetary policy. This decision aims to balance economic growth with price stability."
            },
            "embedding_vector": {
                "type": "ARRAY",
                "items": {
                    "type": "NUMBER",
                    "format": "float"
                },
                "description": "The pre-computed embedding vector of the 'content_text' field, used for similarity search. This would be generated by an ML model.",
                "example": [
                    0.123,
                    -0.456,
                    0.789,
                    0.321,
                    -0.654
                ]
            }
        },
        "required": [
            "document_id",
            "title",
            "category",
            "publish_date",
            "source",
            "content_text",
            "embedding_vector"
        ]
    }
}

system_instruction = """
Your main mission is to generate reliable synthetic tables based on the schema provided.
- A 60% of randomness is important or whatever you think is best to create a table close to reality.
- Be creative.

Output in json format.
"""

config = types.GenerateContentConfig(
    max_output_tokens=65535,
    system_instruction=system_instruction,
    response_mime_type="application/json",
    response_schema=api_schema
)

#%%
## Generate Synthetic Table
table_id = "vtxdemos.demos.fintech_semantic_knowledge"

re = gem_client.models.generate_content(
    model="gemini-2.5-pro",
    config=config,
    contents=f"From the following schema create 200 rows: {semantic_search_documents_schema}"
)

df = pd.DataFrame(json.loads(re.text))

## Load into BigQuery
job = bq_client.load_table_from_dataframe(
    df, table_id, job_config=job_config
)