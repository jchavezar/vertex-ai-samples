import requests
import json
import time

url = "http://localhost:8145/ingest"

# 1. Send a normal event
requests.post(url, json={
    "tag": "portal",
    "event": {"message": "User logged in", "user_id": "user_123"}
})

time.sleep(1)

# 2. Send an error event
requests.post(url, json={
    "type": "error",
    "tag": "sharepoint",
    "event": "Failed to connect to SharePoint: 401 Unauthorized. check credentials."
})

print("Events sent to Nexus.")
