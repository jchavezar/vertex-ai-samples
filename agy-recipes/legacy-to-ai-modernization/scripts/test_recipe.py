# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "python-dotenv>=1.0.0",
#     "fastapi>=0.115.0",
#     "pydantic>=2.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Verification test script for Legacy to AI Modernization Hub."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Locate backend app
recipe_dir = Path(__file__).resolve().parent.parent
hub_dir = recipe_dir.parent.parent / "semiautonomous-agents" / "legacy-to-ai-modernization-hub" / "backend"
sys.path.insert(0, str(hub_dir))

load_dotenv(override=True)

from fastapi.testclient import TestClient
from rich.console import Console
from rich.panel import Panel
from app.main import app

console = Console()
client = TestClient(app)

def test_endpoints():
    console.print(Panel.fit("[bold blue]🧪 Testing Legacy to AI Modernization Hub In-Process & API Engine[/bold blue]"))

    # 1. Health Check
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed with {r.status_code}"
    console.print(f"[green]✓[/green] /api/health -> 200 OK (Model: [bold]{r.json().get('model_target')}[/bold])")

    # 2. Legacy Query Endpoint
    r = client.post("/api/legacy/query", json={
        "page": 1,
        "page_size": 5,
        "simulate_slow_query_ms": 10
    })
    assert r.status_code == 200
    data = r.json()
    assert data["total_records"] > 0
    console.print(f"[green]✓[/green] /api/legacy/query -> 200 OK (Returned [bold]{len(data['data'])}[/bold] records across 20 relational columns)")

    # 3. Shock Engine Calculation
    r = client.post("/api/shock/calculate", json={
        "interest_rate_bps": 75.0,
        "inflation_rate_pct": 3.5,
        "supply_chain_stress_index": 45.0,
        "tariff_volatility_pct": 10.0,
        "supplier_default_risk_pct": 2.0
    })
    assert r.status_code == 200
    shock_data = r.json()
    assert "value_at_risk_99_m" in shock_data
    console.print(f"[green]✓[/green] /api/shock/calculate -> 200 OK (VaR 99%: [bold]${shock_data['value_at_risk_99_m']}M[/bold] in {shock_data['calculation_latency_ms']}ms)")

    # 4. Agent NL Query
    r = client.post("/api/agent/query", json={
        "query": "Simulate 75bps rate hike and APAC shipping crisis"
    })
    assert r.status_code == 200
    agent_res = r.json()
    assert "synthesis_markdown" in agent_res
    console.print(f"[green]✓[/green] /api/agent/query -> 200 OK (Autonomous Synthesis generated in {agent_res['latency_ms']}ms)")

    # 5. Executive Board Memo
    r = client.post("/api/agent/board-memo", json={
        "query_context": "Simulate 75bps rate hike and APAC shipping crisis",
        "shock_params": {
            "interest_rate_bps": 75.0,
            "inflation_rate_pct": 3.5,
            "supply_chain_stress_index": 45.0,
            "tariff_volatility_pct": 10.0,
            "supplier_default_risk_pct": 2.0
        }
    })
    assert r.status_code == 200
    memo_data = r.json()
    assert "full_markdown" in memo_data
    console.print(f"[green]✓[/green] /api/agent/board-memo -> 200 OK (Generated Cryptographic Board Memo in {memo_data['generation_time_ms']}ms)")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ All 5 Modernization Hub Endpoints & Calculation Engines Passed![/bold green]")
    console.print("="*60)

if __name__ == "__main__":
    test_endpoints()
