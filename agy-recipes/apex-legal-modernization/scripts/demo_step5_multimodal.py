#!/usr/bin/env python3
"""
demo_step5_multimodal.py
Act 5: AI Feature 3 — Multimodal Credit Agreement Covenant Extraction & Ethical Wall Pre-Clearance.
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
    print("[ACT 5] AI FEATURE 3: MULTIMODAL TERM SHEET PRE-CLEARANCE & ETHICAL WALL")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR and target_dir != REPO_ROOT:
        print(f"Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "ai_multimodal_deal"], cwd=str(app_dir), check=True)

    url = f"http://localhost:{PORT}/?act=step5&t=" + str(int(time.time()))
    open_browser_safe(url)

    print("\nMultimodal Analysis Modal injected successfully.")
    print(f"Working directory: {app_dir}")
    print(f"Viewing in browser: {url}")
    print("""
KEY EXECUTIVE TAKEAWAYS:
  1. 1-Click Launch: Click the top-right gold button 'Pre-Clear Term Sheet'.
  2. Multimodal Laser-Scan Effect: Visual parsing with Gemini 3.8 Flash Vision across 14 pages of an $850M Senior Secured Facility term sheet.
  3. Structured Financial Covenant Extraction:
     - Total Net Leverage Ratio (Max 4.75x with holiday) -> COMPLIANT
     - Interest Coverage Ratio (Min 3.00x EBITDA) -> COMPLIANT
     - Negative Pledge / Basket -> FLAG FOR PARTNER REVIEW
  4. Deterministic Ethical Wall Harness:
     - Automatic conflict verification against adverse parties.
     - Generates cryptographic audit token: APEX-NY-2026-CLEARANCE-PASS.
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
