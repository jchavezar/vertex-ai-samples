#!/usr/bin/env python3
"""
setup.py
Prepares and validates the environment for the Apex Global Law LLP Portal Modernization Showcase.
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
MASTER_DIR = REPO_ROOT / "semiautonomous-agents" / "apex-legal-portal-modernization"


def main():
    print("==================================================================")
    print("PREPARING APEX GLOBAL LAW PORTAL MODERNIZATION ENVIRONMENT")
    print("==================================================================")

    py_ver = sys.version.split()[0]
    print(f"- Python Version: {py_ver}")

    if not (MASTER_DIR / "site" / "index.html").exists():
        print("- Master site/index.html not initialized. Running inject_feature.py reset...")
        subprocess.run([sys.executable, str(MASTER_DIR / "inject_feature.py"), "reset"], cwd=str(MASTER_DIR), check=True)
    else:
        print("- Master synthetic portal baseline verified.")

    subprocess.run([sys.executable, "-m", "py_compile", str(MASTER_DIR / "serve_portal.py")], check=True)
    subprocess.run([sys.executable, "-m", "py_compile", str(MASTER_DIR / "inject_feature.py")], check=True)
    print("- Compiled serve_portal.py and inject_feature.py with 0 errors.")

    print("\nEnvironment ready! Execute any demo step or say 'demo apex legal'.")
    print("==================================================================")


if __name__ == "__main__":
    main()
