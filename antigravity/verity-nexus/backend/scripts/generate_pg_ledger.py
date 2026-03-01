import os
import json
import psycopg2
from google.genai import Client
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv("../.env")

# PostgreSQL Connection settings (Local Docker)
DB_HOST = "localhost"
DB_PORT = "5433" # Mapped port
DB_USER = "auditor"
DB_PASS = "nexus"
DB_NAME = "ledger"

# Initialize Gemini Client
# It will automatically pick up Vertex AI configuration from .env
client = Client()

# Initialize Gemini Client
client = Client()

def setup_database():
    """Creates the ledger_transactions table if it doesn't exist."""
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    cur = conn.cursor()

    print("Creating ledger_transactions table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ledger_transactions (
            id SERIAL PRIMARY KEY,
            trans_id VARCHAR(50) UNIQUE NOT NULL,
            date DATE NOT NULL,
            vendor_name VARCHAR(255) NOT NULL,
            amount_usd DECIMAL(15, 2) NOT NULL,
            department VARCHAR(100) NOT NULL,
            description TEXT,
            approval_status VARCHAR(50) NOT NULL,
            jurisdiction VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()
    return conn, cur

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
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "temperature": 0.8, # Add some variance
            "response_mime_type": "application/json"
        }
    )
    return response.text

def insert_batch(conn, cur, batch_data: str):
    """Parses JSON and inserts into Postgres."""
    try:
        transactions = json.loads(batch_data)
        for txn in transactions:
            cur.execute("""
                INSERT INTO ledger_transactions 
                (trans_id, date, vendor_name, amount_usd, department, description, approval_status, jurisdiction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trans_id) DO NOTHING
            """, (
                txn['trans_id'],
                txn['date'],
                txn['vendor_name'],
                txn['amount_usd'],
                txn['department'],
                txn['description'],
                txn['approval_status'],
                txn['jurisdiction']
            ))
        conn.commit()
        print(f"  Inserted {len(transactions)} rows.")
    except Exception as e:
        print(f"Error parsing or inserting batch: {e}")
        conn.rollback()

if __name__ == "__main__":
    conn, cur = setup_database()
    
    total_rows = 1000
    batch_size = 50
    num_batches = total_rows // batch_size
    
    print(f"Starting generation of {total_rows} rows in {num_batches} batches...")
    
    for i in range(num_batches):
        batch_json = generate_transaction_batch(i + 1)
        insert_batch(conn, cur, batch_json)
        
    cur.close()
    conn.close()
    print("Database population complete.")
