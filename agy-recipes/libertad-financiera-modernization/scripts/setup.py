# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "python-dotenv>=1.0.0",
#     "google-cloud-discoveryengine>=0.13.0",
#     "google-genai>=1.0.0",
# ]
# ///
"""
setup.py
Idempotent setup and state verification script for Libertad Financiera 3-Act Modernization Demo.
"""

import os
import sys
import json
import time
import socket
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT", "vtxdemos")
BASE_DIR = Path(__file__).resolve().parent.parent
TRACKER_FILE = BASE_DIR / "last_setup_resources.json"
REPO_ROOT = BASE_DIR.parent.parent
APP_DIR = REPO_ROOT / "semiautonomous-agents" / "app-modernization"
PORT = 8088

def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0

def ensure_server_running():
    if is_port_open(PORT):
        print(f"✅ Port {PORT} is already active and serving.")
        return True

    print(f"⚡ Starting multi-threaded serve_libertad.py on port {PORT}...")
    server_script = APP_DIR / "serve_libertad.py"
    if not server_script.exists():
        print(f"❌ Error: {server_script} not found.")
        return False

    proc = subprocess.Popen(
        [sys.executable, str(server_script)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)
    if is_port_open(PORT):
        print(f"✅ Local server started successfully (PID: {proc.pid}) on http://localhost:{PORT}/")
        return True
    else:
        print(f"⚠️ Warning: Server process spawned, waiting on port {PORT}...")
        return False

def main():
    print("===============================================================")
    print("🚀 [SETUP] Libertad Financiera Modernization Demo (3 Actos)")
    print("===============================================================")
    print(f"GCP Project:        {PROJECT_ID}")
    print(f"Application Path:   {APP_DIR}")
    print(f"Target Port:        {PORT}")

    if not APP_DIR.exists():
        print(f"❌ Error: App directory {APP_DIR} does not exist!")
        sys.exit(1)

    server_ready = ensure_server_running()

    resources = {
        "project_id": PROJECT_ID,
        "engine_id": "libertad-search-navigator",
        "data_store_id": "libertad-web-store",
        "model_id": "gemini-3.5-flash-lite",
        "port": PORT,
        "server_status": "RUNNING" if server_ready else "STOPPED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "steps": [
            "Paso 1: Clonado Fiel Tal Cual (Baseline idéntico AEM)",
            "Paso 2: Modernización UI/UX (Mega-Menú Glassmorphism)",
            "Paso 3: Feature de IA (Vertex AI Search + Gemini 3.5 Flash Lite)"
        ]
    }

    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)

    print(f"✅ State tracker recorded at: {TRACKER_FILE}")
    print("===============================================================")
    print("🌟 Entorno listo para presentar los 3 actos de la demo.")
    print("===============================================================")

if __name__ == "__main__":
    main()
