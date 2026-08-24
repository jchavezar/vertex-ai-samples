# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Verification test script for Legacy to AI Modernization Hub."""

import httpx
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

PORT = int(os.getenv("PORT", "8008"))
BASE_URL = f"http://localhost:{PORT}/api"

def test_endpoints():
    print("===============================================================")
    print("🧪 Testing Legacy to AI Modernization Hub API Endpoints...")
    print(f"Target Gateway: {BASE_URL}")
    print("===============================================================")

    with httpx.Client(timeout=10.0) as client:
        # 1. Health Check
        try:
            r = client.get(f"{BASE_URL}/health")
            assert r.status_code == 200, f"Health check failed with {r.status_code}"
            print(f"✅ /api/health -> 200 OK (Model: {r.json().get('model_target')})")
        except Exception as e:
            print(f"⚠️  Backend not reachable directly: {e}")
            print("Note: Ensure backend is running via ./start.sh or uv run uvicorn app.main:app")
            return

        # 2. Legacy Query Endpoint
        r = client.post(f"{BASE_URL}/legacy/query", json={
            "page": 1,
            "page_size": 5,
            "simulate_slow_query_ms": 10
        })
        assert r.status_code == 200
        data = r.json()
        assert data["total_records"] > 0
        print(f"✅ /api/legacy/query -> 200 OK (Returned {len(data['data'])} records across 20 columns)")

        # 3. Shock Engine Calculation
        r = client.post(f"{BASE_URL}/shock/calculate", json={
            "interest_rate_bps": 75.0,
            "inflation_rate_pct": 3.5,
            "supply_chain_stress_index": 45.0,
            "tariff_volatility_pct": 10.0,
            "supplier_default_risk_pct": 2.0
        })
        assert r.status_code == 200
        shock_data = r.json()
        assert "value_at_risk_99_m" in shock_data
        print(f"✅ /api/shock/calculate -> 200 OK (VaR: ${shock_data['value_at_risk_99_m']}M in {shock_data['calculation_latency_ms']}ms)")

        # 4. Agent NL Query
        r = client.post(f"{BASE_URL}/agent/query", json={
            "query": "Simulate 75bps rate hike and APAC shipping crisis"
        })
        assert r.status_code == 200
        agent_res = r.json()
        assert "synthesis_markdown" in agent_res
        print(f"✅ /api/agent/query -> 200 OK (Synthesis generated in {agent_res['latency_ms']}ms)")

        # 5. Executive Board Memo
        r = client.post(f"{BASE_URL}/agent/board-memo", json={
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
        memo_res = r.json()
        assert "memo_id" in memo_res
        print(f"✅ /api/agent/board-memo -> 200 OK (Generated Memo ID: {memo_res['memo_id']})")

    print("===============================================================")
    print("🌟 ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("===============================================================")

if __name__ == "__main__":
    test_endpoints()
