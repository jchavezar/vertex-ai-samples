#!/usr/bin/env python3
"""
teardown.py
Stops any running Weil demo server and restores the current directory baseline.
"""

import sys
import time
import subprocess
from pathlib import Path

PORT = 8089


def main():
    print("==================================================================")
    print("🧹 TEARDOWN: WEIL MODERNIZATION SHOWCASE")
    print("==================================================================")

    # 1. Kill any running server on port 8089
    try:
        out = subprocess.check_output(["lsof", "-ti", f":{PORT}"]).decode().strip()
        if out:
            for pid in out.split():
                print(f"• Terminating process {pid} on port {PORT}...")
                subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            print(f"✅ Port {PORT} released successfully.")
        else:
            print(f"• Port {PORT} is already free.")
    except subprocess.CalledProcessError:
        print(f"• Port {PORT} is already free.")

    # 2. Reset local directory if inject_feature.py is present
    target_dir = Path.cwd().resolve()
    inject_script = target_dir / "inject_feature.py"
    if inject_script.exists():
        print(f"• Resetting {target_dir} to pristine baseline...")
        subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(target_dir), stdout=subprocess.DEVNULL)
        print("✅ Directory restored to pristine clone baseline.")

    print("\n✅ Teardown complete. Zero lingering background processes.")
    print("==================================================================")


if __name__ == "__main__":
    main()
