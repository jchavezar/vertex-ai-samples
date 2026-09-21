#!/usr/bin/env python3
"""
demo_step3_ai.py
Act 3: AI Feature 1 — Intelligent Precedent Navigator (<10ms Autocomplete & Gemini 3.8 Flash).
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_APP_DIR = REPO_ROOT / "semiautonomous-agents" / "apex-legal-portal-modernization"
SCAFFOLD_SCRIPT = BASE_DIR / "scripts" / "scaffold_workspace.py"
PORT = 8089


def open_browser_safe(url: str):
    opener = shutil.which("open") or shutil.which("xdg-open")
    if opener:
        subprocess.run([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def main():
    print("==================================================================")
    print("[ACT 3] AI FEATURE 1: PRECEDENT NAVIGATOR (AUTOCOMPLETE & GEMINI 3.8 FLASH)")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR and target_dir != REPO_ROOT:
        print(f"Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ai"], cwd=str(app_dir), check=True)

    url = f"http://localhost:{PORT}/?act=step3&t=" + str(int(time.time()))
    open_browser_safe(url)

    print("\nIntelligent Precedent Navigator activated successfully.")
    print(f"Working directory: {app_dir}")
    print(f"Viewing in browser: {url}")
    print("""
KEY EXECUTIVE TAKEAWAYS:
  1. Dual-Track Search-As-You-Type:
     - Track A (<10ms): Instant autocomplete in compact dock (480px).
     - Track B: Fluid expansion to 760px with real-time executive synthesis.
  2. Grounded Precedent Intelligence with Gemini 3.8 Flash:
     - Invite Marcus Vance or Elena Rostova to type 'carve-out', 'syndicated facility', or 'Schrems II'.
     - Produces a real-time executive structuring brief with representative mandates.
  3. Zero Broken Links: Result cards resolve cleanly to local synthetic authority pages.
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
