#!/usr/bin/env python3
"""
demo_step1_clone.py
Act 1: Scaffolds and serves the synthetic baseline corporate portal of Apex Global Law LLP (apexgloballaw.example.com).
100% standalone & offline — zero external scraping or customer domains.
"""

import shutil
import socket
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
    print("[ACT 1] BASELINE CORPORATE PORTAL: APEX GLOBAL LAW LLP")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR and target_dir != REPO_ROOT:
        print(f"Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Reset index.html to pristine synthetic baseline
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(app_dir), check=True)

    # 2. Ensure serve_portal.py is running on port 8089
    serve_script = app_dir / "serve_portal.py"
    if serve_script.exists():
        try:
            out = subprocess.check_output(["lsof", "-ti", f":{PORT}"], stderr=subprocess.DEVNULL).decode().strip()
            if out:
                for pid in out.split():
                    subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
                time.sleep(0.5)
        except Exception:
            pass

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex(("127.0.0.1", PORT)) != 0:
            print(f"Starting local synthetic portal server on port {PORT}...")
            subprocess.Popen(
                [sys.executable, str(serve_script)],
                cwd=str(app_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.2)
        s.close()

    url = f"http://localhost:{PORT}/?act=step1&t=" + str(int(time.time()))
    open_browser_safe(url)

    print("\nPortal restored to its pristine baseline (synthetic legacy CMS monolith).")
    print(f"Working directory: {app_dir}")
    print(f"Viewing in browser: {url}")
    print("""
KEY EXECUTIVE TAKEAWAYS (For Marcus Vance & Elena Rostova):
  1. 100% Standalone Synthetic Baseline: Self-contained corporate portal (apexgloballaw.example.com).
  2. Legacy Monolithic Baseline: Rigid top navigation and static keyword search (#txtGlobalSearch).
  3. Diagnostic Findings: Disjointed practice silos without real-time precedent or covenant intelligence.
  4. Zero External Dependencies: Local authority briefs eliminate 404 errors with zero external redirects.
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
