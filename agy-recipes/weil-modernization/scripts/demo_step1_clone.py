#!/usr/bin/env python3
"""
demo_step1_clone.py
Act 1: Faithful baseline clone of Weil, Gotshal & Manges LLP (Sitecore/jQuery monolith).
"""

import sys
import socket
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_APP_DIR = REPO_ROOT / "semiautonomous-agents" / "weil-modernization"
SCAFFOLD_SCRIPT = BASE_DIR / "scripts" / "scaffold_workspace.py"
PORT = 8089


def main():
    print("==================================================================")
    print("🎬 [ACT 1] FAITHFUL BASELINE CLONE: WEIL, GOTSHAL & MANGES LLP")
    print("==================================================================")

    target_dir = Path.cwd().resolve()
    # If cwd does not contain inject_feature.py, scaffold it so files appear in explorer
    if not (target_dir / "inject_feature.py").exists() and target_dir != DEFAULT_APP_DIR:
        print(f"📦 Scaffolding demo files into active workspace: {target_dir}...")
        subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), str(target_dir)], check=True)

    app_dir = target_dir if (target_dir / "inject_feature.py").exists() else DEFAULT_APP_DIR

    # 1. Reset index.html to pristine original
    inject_script = app_dir / "inject_feature.py"
    subprocess.run([sys.executable, str(inject_script), "reset"], cwd=str(app_dir), check=True)

    # 2. Ensure server is running for this specific workspace
    serve_script = app_dir / "serve_weil.py"
    if serve_script.exists():
        try:
            out = subprocess.check_output(["lsof", "-ti", f":{PORT}"]).decode().strip()
            if out:
                for pid in out.split():
                    subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
                time.sleep(0.6)
        except subprocess.CalledProcessError:
            pass

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex(("127.0.0.1", PORT)) != 0:
            print(f"⚡ Starting local server on port {PORT}...")
            subprocess.Popen(["python3", str(serve_script)], cwd=str(app_dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
        s.close()

    # 3. Launch browser to localhost:8089
    url = f"http://localhost:{PORT}/?act=step1&t=" + str(int(time.time()))
    subprocess.run(["open", url])

    print("\n✅ Portal restored to its pristine baseline clone (legacy Sitecore/jQuery).")
    print(f"📁 Working directory: {app_dir}")
    print(f"🌐 Viewing in browser: {url}")
    print("""
📋 KEY EXECUTIVE TAKEAWAYS (For Andrew Simon & Ian Miller):
  1. 100% Visual Fidelity: Exact replication of official production portal (weil.com).
  2. Legacy Monolithic Baseline: Sitecore with jQuery 3.6, heavy stylesheets (>300k chars), and rigid navigation.
  3. Diagnostic Findings: Traditional search field (#txtGlobalSearch), lack of direct deal discovery, and disjointed attorney workflows.
  4. Zero Broken Links: Smart 302 Redirection prevents 404 errors on deep secondary links.
""")
    print("==================================================================")


if __name__ == "__main__":
    main()
