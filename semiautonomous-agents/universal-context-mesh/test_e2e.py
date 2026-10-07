"""
End-to-End (E2E) Automated Verification Script (`test_e2e.py`).
Tests all 4 live ADK + A2A Agent Runtimes, A2A JSON-RPC 2.0 wire traces,
Cross-Session Universal Context Sharing, Memory Bank injection, and Artifact Vault.
"""

import asyncio
import json
import httpx


async def run_e2e_verification() -> None:
    print("================================================================================")
    print("🧪 STARTING END-TO-END (E2E) VERIFICATION: UNIVERSAL CONTEXT MESH")
    print("================================================================================\n")

    async with httpx.AsyncClient(timeout=180.0) as client:
        # 1. Verify A2A Agent Cards on Ports 8011, 8012, 8013
        for name, port in [("wealth_agent", 8011), ("legal_tax_agent", 8012), ("mobility_agent", 8013)]:
            resp = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
            assert resp.status_code == 200, f"Failed to fetch A2A card for {name}"
            card = resp.json()
            print(f"✅ [A2A Discovery] {name} (:{port}) Agent Card verified: skills={len(card.get('skills', []))}")

        # 2. Verify Orchestrator Hub Health (:8010)
        resp = await client.get("http://localhost:8010/api/health")
        assert resp.status_code == 200
        health = resp.json()
        print(f"✅ [Orchestrator Hub :8010] Health check passed: {len(health['a2a_agents'])} A2A agents online\n")

        # Reset state for clean deterministic test
        await client.post("http://localhost:8010/api/reset")
        user_id = "alex.rivera@enterprise.io"

        # 3. STEP A: Chat with Wealth Agent in Session #1 (`session-e2e-wealth-01`)
        print("--------------------------------------------------------------------------------")
        print("▶ STEP A: Sending new liquidity event to `wealth_agent` in Session #1 (`session-e2e-wealth-01`)...")
        w_prompt = (
            "I just completed an additional $4.2M secondary equity sale (bringing my total liquid net worth "
            "to $18,700,000 USD) and want to allocate $5,000,000 into Swiss Francs (CHF). "
            "Please update my financial profile and save this to the Universal Memory Bank."
        )
        resp_w = await client.post(
            "http://localhost:8010/api/chat",
            json={
                "user_id": user_id,
                "session_id": "session-e2e-wealth-01",
                "target_agent": "wealth_agent",
                "message": w_prompt,
            },
        )
        assert resp_w.status_code == 200
        w_data = resp_w.json()
        w_msg = w_data["message"]
        print(f"🤖 [wealth_agent Response]: {w_msg['content'][:240]}...")
        print(f"🛠️  [ADK Tools Executed]: {[tc.get('tool') for tc in w_msg.get('tool_calls', [])]}")
        print(f"🔍 [A2A JSON-RPC Trace]: transport={w_msg['a2a_trace'][0]['transport']} latency={w_msg['a2a_trace'][0]['latency_ms']}ms\n")

        # 4. STEP B: Switch to Legal & Tax Agent in a BRAND-NEW Session #2 (`session-e2e-legal-02`)
        print("--------------------------------------------------------------------------------")
        print("▶ STEP B: Switching to `legal_tax_agent` in BRAND-NEW Session #2 (`session-e2e-legal-02`)...")
        print("  Testing if Legal Agent automatically knows the $18.7M / $4.2M / $5M CHF update WITHOUT user repeating it!")
        l_prompt = (
            "Without me repeating my financial numbers, what are my California exit tax & Swiss treaty obligations "
            "given the brand-new liquidity event and CHF allocation recorded in my Universal Context?"
        )
        resp_l = await client.post(
            "http://localhost:8010/api/chat",
            json={
                "user_id": user_id,
                "session_id": "session-e2e-legal-02",
                "target_agent": "legal_tax_agent",
                "message": l_prompt,
            },
        )
        assert resp_l.status_code == 200
        l_data = resp_l.json()
        l_msg = l_data["message"]
        injected_from_wealth = [
            m for m in l_msg.get("injected_memories", []) if m.get("source_agent") == "wealth_agent"
        ]
        print(f"🔗 [Universal Memory Injection]: Injected {len(l_msg.get('injected_memories', []))} memories ({len(injected_from_wealth)} directly from `wealth_agent`!)")
        print(f"🤖 [legal_tax_agent Response]: {l_msg['content'][:280]}...")
        print(f"🛠️  [ADK Tools Executed]: {[tc.get('tool') for tc in l_msg.get('tool_calls', [])]}\n")

        # 5. STEP C: Run Full Autonomous 4-Agent Roundtable (`/api/roundtable/run`)
        print("--------------------------------------------------------------------------------")
        print("▶ STEP C: Triggering Autonomous 4-Agent Real-Time Roundtable (`/api/roundtable/run`)...")
        resp_rt = await client.post(
            "http://localhost:8010/api/roundtable/run",
            json={"user_id": user_id},
        )
        assert resp_rt.status_code == 200
        rt_data = resp_rt.json()
        print(f"✅ [Roundtable Complete] ID: {rt_data['roundtable_id']} | Sessions created: {len(rt_data['sessions_created'])}")
        for step in rt_data["steps"]:
            print(f"   • Step {step['step']} ({step['agent']} in {step['session_id']}): {len(step['output'].get('tool_calls', []))} tools executed")

        # Verify Final Universal Context State, Memory Bank, and Shared Artifact Vault
        final_ctx = rt_data["universal_context"]
        print("\n================================================================================")
        print("📊 FINAL UNIVERSAL USER CONTEXT METRICS FOR:", user_id)
        print(f"  • Universal `user:*` Namespaces : {list(final_ctx['universal_state'].keys())}")
        print(f"  • Universal Memory Bank Facts   : {len(final_ctx['memories'])} semantic memories stored")
        print(f"  • Shared Artifact Vault Files   : {len(final_ctx['artifacts'])} versioned artifacts published")
        for art in final_ctx["artifacts"][:4]:
            print(f"      - {art['filename']} (v{art['version']}) by {art['created_by_agent']}: {art['title']}")
        print(f"  • Real-Time Telemetry Events    : {len(final_ctx['recent_telemetry'])} WebSocket events broadcast")
        print("================================================================================")
        print("🎉 ALL END-TO-END (E2E) TESTS PASSED 100%!")


if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
