import os
import datetime
from google.cloud import logging

def fetch_recent_logs():
    client = logging.Client(project="vtxdemos")
    
    query = 'textPayload:"ReasoningEngine" OR resource.type="aiplatform.googleapis.com/ReasoningEngine" OR logName=~"ReasoningEngine"'
    
    entries = client.list_entries(order_by=logging.DESCENDING, max_results=50, filter_=query)
    for entry in entries:
        print(f"[{entry.timestamp}] {entry.log_name} | {entry.payload} | {entry.resource.type}")

if __name__ == "__main__":
    fetch_recent_logs()
