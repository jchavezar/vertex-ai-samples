import os
from google.cloud import bigquery
from datetime import datetime, timezone

# Project context directly loaded via user auth triggers
PROJECT_ID = "vtxdemos"
DATASET_ID = "openrouter_metrics"
TABLE_ID = "performance_history"

def get_client():
    return bigquery.Client(project=PROJECT_ID)

def create_dataset_if_not_exists():
    client = get_client()
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except Exception:
        print(f"Creating dataset {DATASET_ID}...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Dataset {DATASET_ID} created.")

def create_table_if_not_exists():
    client = get_client()
    table_ref = bigquery.TableReference(bigquery.DatasetReference(PROJECT_ID, DATASET_ID), TABLE_ID)
    
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("model_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("provider", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("context_length", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("modality", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("pricing_prompt", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("pricing_completion", "FLOAT", mode="NULLABLE"),
        
        # Capability Matrix
        bigquery.SchemaField("max_completion_tokens", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("supports_vision", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("supports_tools", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("supports_structured_output", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("supports_reasoning", "BOOLEAN", mode="NULLABLE"),
        
        bigquery.SchemaField("latency_sec", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("throughput_tps", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("uptime_pct", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("pull_timestamp", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("date_only", "DATE", mode="NULLABLE"),
    ]
    
    try:
        table = client.get_table(table_ref)
        print(f"Table {TABLE_ID} already exists. Updating schema metadata...")
        table.schema = schema
        client.update_table(table, ["schema"])
    except Exception:

        print(f"Creating table {TABLE_ID}...")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"Table {TABLE_ID} created.")


# Helper Parsers to keep BigQuery data pure-numeric for dashboards filters
def parse_float(val_str):
    if not val_str or val_str.lower() in ["-", "n/a", "none", ""]:
        return None
    try:
        # Strip unit chars like 's', 'tps', '%'
        clean_str = val_str.replace("s", "").replace("tps", "").replace("%", "").strip()
        return float(clean_str)
    except ValueError:
        return None

def insert_rows(rows_data, pull_time=None):
    """
    rows_data: list of dicts with keys (model_id, provider, latency, throughput, uptime)
    Returns count of items inserted
    """
    client = get_client()
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    create_dataset_if_not_exists()
    create_table_if_not_exists()
    
    rows_to_insert = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for item in rows_data:
        latency = parse_float(item.get("latency"))

        throughput = parse_float(item.get("throughput"))
        uptime = parse_float(item.get("uptime"))
        
        # Parse Pricing separately safely
        p_prompt = parse_float(item.get("pricing_prompt"))
        p_completion = parse_float(item.get("pricing_completion"))
        context_length = item.get("context_length")
        
        max_completion_tokens = item.get("max_completion_tokens")
        
        rows_to_insert.append({
            "timestamp": now_iso,
            "model_id": item.get("model_id"),
            "provider": item.get("provider"),
            "name": item.get("name"),
            "context_length": int(context_length) if context_length else None,
            "modality": item.get("modality"),
            "pricing_prompt": p_prompt,
            "pricing_completion": p_completion,
            
            # Capability Matrix
            "max_completion_tokens": int(max_completion_tokens) if max_completion_tokens else None,
            "supports_vision": item.get("supports_vision"),
            "supports_tools": item.get("supports_tools"),
            "supports_structured_output": item.get("supports_structured_output"),
            "supports_reasoning": item.get("supports_reasoning"),
            
            "latency_sec": latency,

            "throughput_tps": throughput,
            "uptime_pct": uptime,
            "pull_timestamp": pull_time if pull_time else now_iso,
            "date_only": datetime.now(timezone.utc).date().isoformat()
        })

            
    if not rows_to_insert:
        print("No BigQuery rows to insert.")
        return 0
        
    print(f"Inserting {len(rows_to_insert)} rows into BigQuery...")
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"BigQuery Insert Errors: {errors}")
    else:
        print("BigQuery insert absolute insert stream successful.")
    return len(rows_to_insert)


if __name__ == "__main__":
    # Test layout creation
    create_dataset_if_not_exists()
    create_table_if_not_exists()
