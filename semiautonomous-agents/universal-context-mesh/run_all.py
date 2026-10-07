"""
Multi-Runtime Process Launcher (`run_all.py`).
Starts all 4 Google ADK + A2A Runtimes concurrently:
  - Port 8011: Wealth & Portfolio ADK + A2A Server Runtime
  - Port 8012: Legal & Tax Compliance ADK + A2A Server Runtime
  - Port 8013: Global Mobility ADK + A2A Server Runtime
  - Port 8010: Universal Context Orchestrator & WebSocket Hub + UI Server
  - Port 5173: Frontend Static Server Mirror
"""

import asyncio
import os
import signal
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
PYTHON_BIN = str(ROOT_DIR / ".venv" / "bin" / "python")


async def run_all_services() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    env["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    env["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
    env["GOOGLE_CLOUD_LOCATION"] = "global"

    procs = []
    services = [
        ("Wealth A2A (:8011)", [PYTHON_BIN, "-m", "backend.agents.wealth_agent"]),
        ("Legal A2A (:8012)", [PYTHON_BIN, "-m", "backend.agents.legal_tax_agent"]),
        ("Mobility A2A (:8013)", [PYTHON_BIN, "-m", "backend.agents.mobility_agent"]),
        ("Orchestrator Hub & UI (:8010)", [PYTHON_BIN, "-m", "backend.orchestrator_service"]),
    ]

    for label, cmd in services:
        print(f"🚀 Starting {label}...")
        p = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(ROOT_DIR),
            env=env,
        )
        procs.append((label, p))

    print("\n================================================================================")
    print("✅ UNIVERSAL CONTEXT MESH — ALL RUNTIMES ACTIVE")
    print("  • Orchestrator Hub & Workbench UI : http://localhost:8010")
    print("  • Frontend Mirror UI              : http://localhost:5173")
    print("  • Wealth A2A Server Card          : http://localhost:8011/.well-known/agent-card.json")
    print("  • Legal/Tax A2A Server Card       : http://localhost:8012/.well-known/agent-card.json")
    print("  • Mobility A2A Server Card        : http://localhost:8013/.well-known/agent-card.json")
    print("================================================================================\n")

    try:
        await asyncio.gather(*(p.wait() for _, p in procs))
    except asyncio.CancelledError:
        pass
    finally:
        for label, p in procs:
            if p.returncode is None:
                p.terminate()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_services())
    except KeyboardInterrupt:
        print("\nShutting down Universal Context Mesh runtimes...")
