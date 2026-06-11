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
    
    # Let's query Google Cloud Logging for docparse-firestore-mcp service entries in the last 10 minutes
    now = datetime.utcnow()
    ten_mins_ago = (now - timedelta(minutes=60)).isoformat() + "Z"
    
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
    
    print(f"Querying logs from {ten_mins_ago}...")
    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        print(f"Error querying logs: {r.status_code} - {r.text}")
        return
        
    entries = r.json().get("entries", [])
    print(f"Found {len(entries)} log entries.")
    
    if entries:
        print("\n--- Verbatim Cloud Run Log Entries ---")
        for entry in entries[:50]:
            payload = entry.get("textPayload", "")
            json_payload = entry.get("jsonPayload", {})
            ts = entry.get("timestamp", "")
            p_str = payload or json.dumps(json_payload)
            print(f"[{ts}] {p_str}")
    else:
        print("\nNo log entries found in the Cloud Run logs.")

if __name__ == "__main__":
    main()
