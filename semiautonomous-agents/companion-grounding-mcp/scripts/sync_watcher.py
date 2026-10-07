#!/usr/bin/env python3
"""
Outbound Sync Watcher Daemon for `jesus.c.googlers.com`
Polls `gs://vtxdemos-companion-memory/sync_trigger.json` every 30 seconds.
When the user triggers `trigger_live_sync` from the Claude Phone App or Pocket Coach PWA,
this daemon detects `sync_requested_at != null` and immediately runs `daily_sync_pipeline.py`.
"""

import os
import json
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GCS_BUCKET = os.environ.get("GCS_MEMORY_BUCKET", "gs://vtxdemos-companion-memory")
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")


def check_trigger() -> bool:
    try:
        res = subprocess.run(
            ["gcloud", "storage", "cat", f"{GCS_BUCKET}/sync_trigger.json", f"--project={PROJECT_ID}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout.strip())
            return bool(data.get("sync_requested_at"))
    except Exception:
        pass
    return False


def main():
    print(f"[SyncWatcher] Listening for phone sync requests on {GCS_BUCKET}/sync_trigger.json ...")
    while True:
        if check_trigger():
            print("[SyncWatcher] Phone sync request detected! Executing daily_sync_pipeline.py ...")
            subprocess.run(["python3", str(BASE_DIR / "scripts" / "daily_sync_pipeline.py")])
        time.sleep(30)


if __name__ == "__main__":
    main()
