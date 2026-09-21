#!/usr/bin/env python3
"""
setup.py
Prepares and validates the environment for the Weil Modernization Showcase.
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
MASTER_DIR = REPO_ROOT / "semiautonomous-agents" / "weil-modernization"


def main():
    print("==================================================================")
    print("🔧 PREPARING WEIL MODERNIZATION SHOWCASE ENVIRONMENT")
    print("==================================================================")

    # 1. Check Python version
    py_ver = sys.version.split()[0]
    print(f"• Python Version: {py_ver}")

    # 2. Check master directory
    if not (MASTER_DIR / "site" / "index.html").exists():
        print("• Master site not found. Running clone_weil.py...")
        subprocess.run([sys.executable, str(MASTER_DIR / "clone_weil.py")], cwd=str(MASTER_DIR), check=True)
    else:
        print("• Master site already cloned and verified.")

    # 3. Test compilation of server and injector
    subprocess.run([sys.executable, "-m", "py_compile", str(MASTER_DIR / "serve_weil.py")], check=True)
    subprocess.run([sys.executable, "-m", "py_compile", str(MASTER_DIR / "inject_feature.py")], check=True)
    print("• Compiled serve_weil.py and inject_feature.py with 0 errors.")

    print("\n✅ Environment ready! You can now execute any demo step or say 'demo weil'.")
    print("==================================================================")


if __name__ == "__main__":
    main()
