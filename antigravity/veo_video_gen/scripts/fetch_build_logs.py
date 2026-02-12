import os
import datetime
from google.cloud import logging

def fetch_recent_logs():
    client = logging.Client(project="vtxdemos")
    
    # query for build logs in the last 20 minutes
    now = datetime.datetime.utcnow()
    past = now - datetime.timedelta(minutes=20)
    timestamp_filter = past.isoformat() + "Z"
    
    query = f'resource.type="build" AND timestamp >= "{timestamp_filter}"'
    
    entries = client.list_entries(order_by=logging.DESCENDING, max_results=50, filter_=query)
    for entry in entries:
        print(f"[{entry.timestamp}] {entry.log_name} | {entry.payload}")

if __name__ == "__main__":
    fetch_recent_logs()
