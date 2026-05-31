import google.auth
import google.auth.transport.requests
import requests
import json
from datetime import datetime, timedelta, timezone

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
    
    now = datetime.now(timezone.utc)
    ten_mins_ago = (now - timedelta(minutes=10)).isoformat()
    
    log_filter = (
        f'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="docparse-firestore-mcp" '
        f'AND timestamp >= "{ten_mins_ago}"'
    )
    
    url = "https://logging.googleapis.com/v2/entries:list"
    body = {
        "projectIds": ["vtxdemos"],
        "filter": log_filter,
        "orderBy": "timestamp desc",
        "pageSize": 200
    }
    
    r = requests.post(url, headers=headers, json=body)
    entries = r.json().get("entries", [])
    print(f"Total entries: {len(entries)}")
    for e in entries:
        ts = e.get("timestamp")
        payload = e.get("textPayload") or json.dumps(e.get("jsonPayload")) or json.dumps(e.get("httpRequest"))
        print(f"[{ts}] {payload}")

if __name__ == "__main__":
    main()
