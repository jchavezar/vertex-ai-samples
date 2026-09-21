#!/usr/bin/env python3
"""
teardown.py
Stops any running Apex Global Law portal server and restores the baseline.
"""

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_APP_DIR = REPO_ROOT / "semiautonomous-agents" / "apex-legal-portal-modernization"
PORT = 8089


def main():
    print("==================================================================")
    print("TEARDOWN: APEX GLOBAL LAW PORTAL MODERNIZATION SHOWCASE")
    print("==================================================================")

    try:
        out = subprocess.check_output(["lsof", "-ti", f":{PORT}"], stderr=subprocess.DEVNULL).decode().strip()
        if out:
            for pid in out.split():
                print(f"- Terminating process {pid} on port {PORT}...")
                subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
            time.sleep(0.4)
            print(f"Port {PORT} released successfully.")
        else:
            print(f"- Port {PORT} is already free.")
    except Exception:
        print(f"- Port {PORT} is already free.")

    target_dir = Path.cwd().resolve()
    inject_script = target_dir / "inject_feature.py"
    if not inject_script.exists():
        inject_script = DEFAULT_APP_DIR / "inject_feature.py"
        target_dir = DEFAULT_APP_DIR

    if inject_script.exists():
        print(f"- Resetting {target_dir} to pristine synthetic baseline...")
        subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(target_dir), stdout=subprocess.DEVNULL, check=True)
        print("Directory restored to pristine synthetic baseline.")

    print("\nTeardown complete. Zero lingering background processes.")
    print("==================================================================")


if __name__ == "__main__":
    main()
