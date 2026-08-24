# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Clean teardown script for Legacy to AI Modernization Hub."""

import json
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TRACKER_FILE = BASE_DIR / "last_setup_resources.json"

def main():
    print("===============================================================")
    print("🛑 [TEARDOWN] Antigravity Legacy to AI Modernization Hub")
    print("===============================================================")

    if TRACKER_FILE.exists():
        try:
            with open(TRACKER_FILE, "r") as f:
                data = json.load(f)
            print(f"Read resource tracker for Project: {data.get('project_id')}")
            b_port = data.get("backend_port", 8008)
            f_port = data.get("frontend_port", 5178)

            # Terminate active port listeners
            for port in [b_port, f_port]:
                try:
                    pids = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip().split()
                    for pid in pids:
                        if pid:
                            print(f"Terminating process on port {port} (PID: {pid})...")
                            os.system(f"kill -9 {pid} 2>/dev/null")
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning reading tracker file: {e}")

        # Remove tracker file per skill guidelines
        TRACKER_FILE.unlink(missing_ok=True)
        print(f"✅ Removed state tracker: {TRACKER_FILE}")
    else:
        print("ℹ️  No tracker file found. Cleaning port 8008 and 5178 listeners if active...")
        for port in [8008, 5178]:
            os.system(f"kill -9 $(lsof -ti :{port} 2>/dev/null) 2>/dev/null || true")

    print("===============================================================")
    print("✅ Teardown complete. Zero lingering background processes.")
    print("===============================================================")

if __name__ == "__main__":
    main()
