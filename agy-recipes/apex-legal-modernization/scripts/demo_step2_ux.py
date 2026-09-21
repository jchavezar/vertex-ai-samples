#!/usr/bin/env python3
"""
demo_step2_ux.py
Act 2: UX/UI Modernization (Glassmorphic Deal Mega-Menu & Precedent Ticker) for Apex Global Law LLP.
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
    print("[ACT 2] UX/UI MODERNIZATION: DEAL INTELLIGENCE MEGA-MENU & TICKER")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR and target_dir != REPO_ROOT:
        print(f"Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "modern_header_ux"], cwd=str(app_dir), check=True)

    url = f"http://localhost:{PORT}/?act=step2&t=" + str(int(time.time()))
    open_browser_safe(url)

    print("\nPortal modernized with corporate glassmorphic navigation.")
    print(f"Working directory: {app_dir}")
    print(f"Viewing in browser: {url}")
    print("""
KEY EXECUTIVE TAKEAWAYS:
  1. Visual Desaturation & Executive Hierarchy: Replaces legacy masthead with an interactive glassmorphic header (backdrop-filter: blur(16px)).
  2. Transactional Specialization across Core Apex Global Law Pillars:
     - Banking & Finance (Syndicated loans, direct lending, cov-lite facilities)
     - M&A & Private Equity (Public takeovers, sponsor carve-outs, Delaware Chancery standards)
     - Restructuring & Special Situations (Chapter 11, liability management)
  3. Real-Time Deal Ticker: Highlights marquee mandates ($12.4B Carve-Out, $8.5B Syndicated Facility, Schrems II AI Standard).
  4. 100% Reversible: Instant rollback in one command (`inject_feature.py reset`).
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
