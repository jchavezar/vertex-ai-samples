#!/usr/bin/env python3
"""
Lego Block 1: Daily Read-Only Harvester & Incremental Supermemory Indexer
Runs on `jesus.c.googlers.com` (inside BeyondCorp perimeter).

1. Queries CSA CLI (`CHAT`, `GMAIL`, `DRIVE`) and `gcalendar` for any new messages, space threads, docs, or calendar events involving Selene Song (`selenesong@google.com`) [READ-ONLY]
2. Runs `rebuild_complete_supermemory.py` to deduplicate, chronologically sort, tag with Mark Manson Models & Topic Graph, and update `gemini-embedding-001` vectors
3. Pushes updated `ground_truth.db` outbound to `gs://vtxdemos-companion-memory/ground_truth.db`
"""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ground_truth.db"
GCS_BUCKET = os.environ.get("GCS_MEMORY_BUCKET", "gs://vtxdemos-companion-memory")
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
VENV_PY = "/usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/.venv/bin/python"


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] [Supermemory-Sync] {msg}", flush=True)


def refresh_csa_and_calendars():
    csa_bin = "/google/bin/releases/csa-cli/csa_cli.par"
    gcal_bin = "/google/bin/releases/gemini-agents-gcalendar/gcalendar"

    if os.path.exists(csa_bin):
        log("Refreshing Google Chat DM & Multi-Space threads via CSA CLI...")
        with open("/tmp/csa_selene_spaces.txt", "w") as f:
            subprocess.run(
                [
                    csa_bin,
                    "--allowed_corpora=CHAT,GMAIL,DRIVE",
                    "--max_output_tokens=50000",
                    "--user_prompt=Find all recent Google Chat messages, group spaces, threads, emails, and documents involving Selene Song (selenesong@google.com)",
                ],
                stdout=f,
                stderr=subprocess.STDOUT,
                check=False,
            )

    if os.path.exists(gcal_bin):
        log("Refreshing Google Calendar events for jesusarguelles@google.com and selenesong@google.com...")
        for user, out_p in [("jesusarguelles@google.com", "/tmp/cal_jesus_2.json"), ("selenesong@google.com", "/tmp/cal_selene_2.json")]:
            with open(out_p, "w") as f:
                subprocess.run(
                    [
                        gcal_bin, "readonly", "events",
                        "--cal", user,
                        "--start", datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z"),
                        "--end", "2027-03-31T23:59:59Z",
                        "--max", "500", "--json",
                    ],
                    stdout=f,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )


def push_db_to_gcs():
    if not DB_PATH.exists():
        log(f"ERROR: {DB_PATH} does not exist!")
        return False

    log(f"Uploading {DB_PATH} to {GCS_BUCKET}/ground_truth.db ...")
    res = subprocess.run(
        ["gcloud", "storage", "cp", str(DB_PATH), f"{GCS_BUCKET}/ground_truth.db", f"--project={PROJECT_ID}", "--quiet"],
        capture_output=True,
        text=True,
    )
    if res.returncode == 0:
        log("Successfully pushed updated ground_truth.db to GCS!")
        status_payload = (
            f'{{"sync_requested_at": null, "last_synced_at": "{datetime.now(timezone.utc).isoformat()}", '
            f'"host": "{os.uname().nodename}", "status": "completed"}}'
        )
        subprocess.run(
            ["gcloud", "storage", "cp", "-", f"{GCS_BUCKET}/sync_trigger.json", f"--project={PROJECT_ID}", "--quiet"],
            input=status_payload,
            text=True,
        )
        return True
    log(f"GCS upload failed: {res.stderr}")
    return False


def run_sync():
    log(f"Starting Read-Only Daily Sync on host={os.uname().nodename}...")
    refresh_csa_and_calendars()
    rebuild_script = BASE_DIR / "scripts" / "rebuild_complete_supermemory.py"
    if rebuild_script.exists() and os.path.exists(VENV_PY):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR / "scripts")
        subprocess.run([VENV_PY, str(rebuild_script)], env=env, check=False)
    push_db_to_gcs()
    log("Daily sync cycle complete.")


if __name__ == "__main__":
    run_sync()
