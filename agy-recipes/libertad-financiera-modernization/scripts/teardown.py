# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
teardown.py
Teardown and cleanup script for Libertad Financiera 3-Act Modernization Demo.
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TRACKER_FILE = BASE_DIR / "last_setup_resources.json"
REPO_ROOT = BASE_DIR.parent.parent
APP_DIR = REPO_ROOT / "semiautonomous-agents" / "app-modernization"
PORT = 8088

def kill_port(port: int):
    try:
        out = subprocess.check_output(["lsof", "-t", f"-i:{port}"], text=True).strip()
        if out:
            pids = out.split("\n")
            for pid in pids:
                if pid:
                    os.system(f"kill -9 {pid} 2>/dev/null")
            print(f"🛑 Killed processes on port {port} (PIDs: {', '.join(pids)})")
    except Exception:
        pass

def main():
    print("===============================================================")
    print("🧹 [TEARDOWN] Libertad Financiera Modernization Demo")
    print("===============================================================")

    # 1. Reset index.html to pristine original
    inject_script = APP_DIR / "inject_feature.py"
    if inject_script.exists():
        try:
            subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(APP_DIR), check=True)
            print("✅ Restored original pristine index.html.")
        except Exception as e:
            print(f"⚠️ Note on reset: {e}")

    # 2. Terminate background server on port 8088
    kill_port(PORT)
    print(f"✅ Cleaned up port {PORT}.")

    # 3. Remove tracker file
    if TRACKER_FILE.exists():
        TRACKER_FILE.unlink()
        print(f"✅ Removed state tracker: {TRACKER_FILE}")

    print("===============================================================")
    print("🌟 Teardown complete. Workspace and port 8088 are clean.")
    print("===============================================================")

if __name__ == "__main__":
    main()
