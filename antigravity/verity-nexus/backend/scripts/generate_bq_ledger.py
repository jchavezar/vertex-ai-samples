import os
import json
from google.cloud import bigquery
from google.genai import Client
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv("../.env")

# Initialize Gemini Client
# It will automatically pick up Vertex AI configuration from .env
genai_client = Client()

BQ_DATASET = "verity_nexus_ledger"
BQ_TABLE = "ledger_transactions"

def setup_database():
    """Creates the ledger_transactions table in BigQuery if it doesn't exist."""
    print("Connecting to BigQuery...")
    client = bigquery.Client()
    dataset_id = f"{client.project}.{BQ_DATASET}"
    
    try:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30, exists_ok=True)
        print("Dataset ready: {}.{}".format(client.project, dataset.dataset_id))
    except Exception as e:
        print(f"Dataset creation error: {e}")
        
    table_id = f"{dataset_id}.{BQ_TABLE}"
    
    schema = [
        bigquery.SchemaField("trans_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount_usd", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("department", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("approval_status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("jurisdiction", "STRING", mode="REQUIRED"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=True)
    print("Table ready: {}.{}.{}".format(table.project, table.dataset_id, table.table_id))
    
    return client, table_id

def generate_transaction_batch(batch_num: int) -> str:
    """Uses Gemini 2.5 Flash to generate a batch of highly realistic synthetic transactions."""
    
    prompt = f"""
    You are a data engineer generating synthetic but highly realistic corporate financial transaction data for a Tier-1 audit simulation.
    Generate a JSON array of 50 transaction records.

    **CRITICAL REQUIREMENTS:**
    1. Output MUST be ONLY a raw JSON array. Do not include markdown formatting like ```json ... ```. 
    2. The JSON array must contain exactly 50 objects.

    **Schema for each object:**
    - trans_id: String (e.g., "TXN-2026-001")
    - date: String (YYYY-MM-DD, within the year 2026)
    - vendor_name: String (Realistic company names: IT vendors, consulting firms, law firms, suppliers)
    - amount_usd: Float (Varying from small expenses like 50.00 to massive CapEx like 3500000.00)
    - department: String (e.g., "IT", "Legal", "Procurement", "Marketing", "R&D")
    - description: String (Realistic business rationale)
    - approval_status: String (Usually "L1-APPROVED", "L2-APPROVED", or "CFO-APPROVED", but occasionally "AUTO-APPROVE")
    - jurisdiction: String (e.g., "US", "UK", "Germany", "Japan", occasionally non-treaty like "Cayman Islands", "Panama")

    **Anomaly Seeding (Crucial for the demo):**
    Ensure roughly 5-10% of the transactions include these specific anomalies:
    - **Anomaly 1**: amount_usd > 1500000.00 (High value)
    - **Anomaly 2**: amount_usd ends exactly in .00 and is a multiple of 1000 (Round numbers, e.g. 50000.00)
    - **Anomaly 3**: approval_status is exactly "AUTO-APPROVE"
    - **Anomaly 4**: jurisdiction is a non-treaty tax haven (e.g., "Cayman Islands", "Panama", "Seychelles")
    - **Specific Targets**: Include a few transactions for "Baker McKenzie" or "Enterprise LLP" or "INNOVATE LLC CONSULTING GROUP" that are very high value ($100k - $2M) and marked "AUTO-APPROVE".
    """

    print(f"Requesting batch {batch_num} from Gemini 2.5 Flash...")
    response = genai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "temperature": 0.8, # Add some variance
            "response_mime_type": "application/json"
        }
    )
    return response.text

def insert_batch(client, table_id, batch_data: str):
    """Parses JSON and inserts into BigQuery."""
    try:
        transactions = json.loads(batch_data)
        # BigQuery expects DATE fields to be formatted as strings 'YYYY-MM-DD', which we have.
        errors = client.insert_rows_json(table_id, transactions)
        if errors == []:
            print(f"  Inserted {len(transactions)} rows.")
        else:
            print(f"Encountered errors while inserting rows: {errors}")
    except Exception as e:
        print(f"Error parsing or inserting batch: {e}")

if __name__ == "__main__":
    client, table_id = setup_database()
    
    total_rows = 500
    batch_size = 50
    num_batches = total_rows // batch_size
    
    print(f"Starting generation of {total_rows} rows in {num_batches} batches...")
    
    for i in range(num_batches):
        batch_json = generate_transaction_batch(i + 1)
        insert_batch(client, table_id, batch_json)
        
    print("BigQuery population complete.")
