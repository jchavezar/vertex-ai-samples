#!/usr/bin/env python3
"""
scaffold_workspace.py
Scaffolds the Apex Global Law LLP synthetic portal demo files directly into the active workspace directory.
Ensures files immediately appear in the IDE file tree (Explorer).
"""

import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
MASTER_DIR = REPO_ROOT / "semiautonomous-agents" / "apex-legal-portal-modernization"


def main():
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    print(f"Scaffolding Apex Global Law LLP demo files into: {target_dir}")

    if not MASTER_DIR.exists():
        print(f"Error: Master directory {MASTER_DIR} does not exist.")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy site folder
    target_site = target_dir / "site"
    master_site = MASTER_DIR / "site"
    if master_site.exists():
        if target_site.exists():
            shutil.rmtree(target_site)
        shutil.copytree(master_site, target_site)
        print("  - Copied site/ synthetic portal HTML.")

    # 2. Copy serve_portal.py
    shutil.copy2(MASTER_DIR / "serve_portal.py", target_dir / "serve_portal.py")
    print("  - Copied serve_portal.py (ThreadingHTTPServer + Vertex AI Gemini 3.8 Flash APIs).")

    # 3. Copy inject_feature.py
    shutil.copy2(MASTER_DIR / "inject_feature.py", target_dir / "inject_feature.py")
    print("  - Copied inject_feature.py (Modular Feature Injector).")

    # 4. Ensure site starts in pristine baseline
    inject_script = target_dir / "inject_feature.py"
    if inject_script.exists():
        subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(target_dir), stdout=subprocess.DEVNULL, check=True)
        print("  - Initialized pristine synthetic corporate baseline (index.html).")

    print(f"\nAll Apex Global Law LLP demo files successfully scaffolded in {target_dir}!")


if __name__ == "__main__":
    main()
