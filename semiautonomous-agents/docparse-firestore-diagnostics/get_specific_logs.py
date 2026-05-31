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
    
    # Query Google Cloud Logging for docparse-firestore-mcp service entries around 04:49:35
    log_filter = (
        'resource.type="cloud_run_revision" '
        'AND resource.labels.service_name="docparse-firestore-mcp" '
        'AND timestamp >= "2026-05-31T04:49:00Z" '
        'AND timestamp <= "2026-05-31T04:50:00Z"'
    )
    
    url = "https://logging.googleapis.com/v2/entries:list"
    body = {
        "projectIds": ["vtxdemos"],
        "filter": log_filter,
        "orderBy": "timestamp asc",
        "pageSize": 200
    }
    
    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        print(f"Error: {r.status_code} - {r.text}")
        return
        
    entries = r.json().get("entries", [])
    print(f"Found {len(entries)} log entries.")
    for entry in entries:
        ts = entry.get("timestamp", "")
        payload = entry.get("textPayload", "")
        json_payload = entry.get("jsonPayload", {})
        msg = payload or json.dumps(json_payload)
        print(f"[{ts}] {msg}")

if __name__ == "__main__":
    main()
