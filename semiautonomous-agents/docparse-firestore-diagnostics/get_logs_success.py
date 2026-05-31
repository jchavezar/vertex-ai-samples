import google.auth
import google.auth.transport.requests
import requests
import json
from datetime import datetime, timedelta

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # Query for logs in the last 5 minutes
    start_time = (datetime.utcnow() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_filter = (
        f'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="docparse-firestore-mcp" '
        f'AND timestamp >= "{start_time}"'
    )
    
    url = "https://logging.googleapis.com/v2/entries:list"
    body = {
        "projectIds": ["vtxdemos"],
        "filter": log_filter,
        "orderBy": "timestamp asc",
        "pageSize": 100
    }
    
    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        print(f"Error: {r.status_code} - {r.text}")
        return
        
    entries = r.json().get("entries", [])
    print(f"Found {len(entries)} Cloud Run log entries in the last 5 minutes.")
    for entry in entries:
        ts = entry.get("timestamp", "")
        payload = entry.get("textPayload", "")
        json_payload = entry.get("jsonPayload", {})
        msg = payload or json.dumps(json_payload)
        print(f"[{ts}] {msg}")

if __name__ == "__main__":
    main()
