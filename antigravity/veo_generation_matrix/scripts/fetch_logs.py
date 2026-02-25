import os
from google.cloud import logging

def fetch_recent_logs():
    client = logging.Client(project="vtxdemos")
    # Query for build logs or reasoning engine logs
    query = 'resource.type="build" OR resource.type="aiplatform.googleapis.com/ReasoningEngine" OR resource.type="cloud_run_revision"'
    
    # Just get the last 50 logs
    entries = client.list_entries(order_by=logging.DESCENDING, max_results=50, filter_=query)
    for entry in entries:
        print(f"[{entry.timestamp}] {entry.log_name} | {entry.payload}")

if __name__ == "__main__":
    fetch_recent_logs()
