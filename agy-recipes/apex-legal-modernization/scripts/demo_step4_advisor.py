#!/usr/bin/env python3
"""
demo_step4_advisor.py
Act 4: AI Feature 2 — 24/7 Floating Apex Deal & Regulatory AI Advisor (Gemini 3.8 Flash).
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
    print("[ACT 4] AI FEATURE 2: 24/7 APEX DEAL & REGULATORY AI ADVISOR")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR and target_dir != REPO_ROOT:
        print(f"Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "inject", "ai_advisor"], cwd=str(app_dir), check=True)

    url = f"http://localhost:{PORT}/?act=step4&t=" + str(int(time.time()))
    open_browser_safe(url)

    print("\n24/7 Apex Deal AI Advisor injected in bottom-right corner.")
    print(f"Working directory: {app_dir}")
    print(f"Viewing in browser: {url}")
    print("""
KEY EXECUTIVE TAKEAWAYS:
  1. Omnipresent Single-Pane Access: Gold/Navy floating badge with live green status indicator.
  2. Conversational Drawer with Instant Query Chips:
     - 'Analyze Delaware MAE standards for pending buyout'
     - 'Check Schrems II cross-border data transfer clause'
     - 'Summarize cov-lite syndicated debt protections'
  3. Institutional Legal & Financial Reasoning via Gemini 3.8 Flash:
     - Structured responses formatted for General Counsels and Private Equity principals.
     - Grounded in Delaware corporate jurisprudence and regulatory frameworks.
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
