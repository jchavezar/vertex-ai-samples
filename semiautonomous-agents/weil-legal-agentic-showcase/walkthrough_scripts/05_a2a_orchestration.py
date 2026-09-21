"""
Step 5: True Agent-to-Agent (A2A) Distributed Protocol & Practice Federation
-----------------------------------------------------------------------------
BigLaw transactions require multi-practice coordination across specialized departments
(Antitrust, Tax, M&A) that operate as distinct organizational units with separate
security boundaries, domain knowledge, and deployment lifecycles.

Instead of monolithic in-process coupling (`AgentTool`), this script implements TRUE
Agent-to-Agent (A2A) protocol federation using the official Google ADK A2A primitives:

1. Autonomous Practice Microservices (A2A Servers):
   - Antitrust Specialist Service: Hosted independently on http://127.0.0.1:8094
   - Tax & Corporate Structuring Service: Hosted independently on http://127.0.0.1:8095
   - Both expose the open A2A specification with standardized `AgentCard` discovery:
     `http://127.0.0.1:8094/.well-known/agent-card.json`
     `http://127.0.0.1:8095/.well-known/agent-card.json`

2. Capability Discovery & Remote Invocations (A2A Clients):
   - The Lead M&A Partner Agent does NOT import or execute subagent Python code.
   - It discovers and invokes remote specialists across the network using `RemoteA2aAgent`.
   - Communication flows through standardized A2A JSON-RPC over HTTP/SSE.

3. Cross-Practice Executive Deal Synthesis:
   - Lead Partner orchestrates multi-agent delegation and synthesizes specialized advice
     into a client-ready legal memorandum.
"""

import os
import sys
import json
import time
import asyncio
import threading
import functools
import httpx
import uvicorn
from typing import Any, Dict

# Force unbuffered streaming output
print = functools.partial(print, flush=True)

# Enforce target environment configuration
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["BIGQUERY_PROJECT"] = "vtxdemos"
os.environ["BIGQUERY_LOCATION"] = "US"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Dedicated non-conflicting local ports for A2A services
ANTITRUST_PORT = 8094
TAX_PORT = 8095
ANTITRUST_HOST = "127.0.0.1"
TAX_HOST = "127.0.0.1"

# ---------------------------------------------------------------------------
# 1. Define Standalone Practice Group Agents
# ---------------------------------------------------------------------------
antitrust_agent = Agent(
    name="antitrust_specialist",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil Senior Antitrust & Competition Practice Specialist (Washington D.C. office).
    Your mandate:
    1. Analyze Hart-Scott-Rodino (HSR) premerger notification thresholds for large-scale acquisitions.
    2. Provide statutory waiting period requirements (30 days) and FTC/DOJ Second Request risks.
    3. Recommend regulatory efforts covenants (e.g. Reasonable Best Efforts vs. Hell-or-High-Water vs. Reverse Breakup Fees).
    Provide concise, highly rigorous legal guidance with statutory references.
    """
)

tax_agent = Agent(
    name="tax_specialist",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil Senior Tax & Transactional Structuring Specialist (New York office).
    Your mandate:
    1. Analyze asset purchase vs. stock purchase tax step-up dynamics under IRC Section 338(h)(10) / Section 336(e).
    2. Detail buyer depreciation benefits versus seller double-taxation friction.
    3. Provide actionable structuring guidance for domestic tech acquisition holding vehicles.
    Provide concise, highly analytical legal guidance.
    """
)

# ---------------------------------------------------------------------------
# 2. Server Lifecycle Manager: Run Standalone A2A Microservices
# ---------------------------------------------------------------------------
class A2AServiceRunner:
    """Manages background uvicorn servers hosting the A2A microservices."""
    def __init__(self):
        self.servers = []
        self.threads = []

    def start_service(self, agent: Agent, host: str, port: int, service_name: str):
        print(f"🚀 [A2A SERVICE LAUNCH] Booting {service_name} on http://{host}:{port}...")
        app = to_a2a(agent=agent, host=host, port=port)
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        self.servers.append(server)
        self.threads.append(thread)
        return f"http://{host}:{port}"

    def stop_all(self):
        print("\n🛑 [A2A TEARDOWN] Gracefully shutting down distributed practice microservices...")
        for s in self.servers:
            s.should_exit = True
        for t in self.threads:
            t.join(timeout=3)
        print("✅ All A2A service endpoints stopped.")


# ---------------------------------------------------------------------------
# 3. Main A2A Walkthrough
# ---------------------------------------------------------------------------
async def run_a2a_walkthrough():
    print("=" * 82)
    print("🌐 [A2A PROTOCOL] True Agent-to-Agent Distributed Practice Federation")
    print("=" * 82)
    print("Architecture:")
    print(f"  • Antitrust A2A Endpoint : http://{ANTITRUST_HOST}:{ANTITRUST_PORT} (Autonomous Service)")
    print(f"  • Tax A2A Endpoint       : http://{TAX_HOST}:{TAX_PORT} (Autonomous Service)")
    print("  • Discovery Protocol     : Standardized `AgentCard` (/.well-known/agent-card.json)")
    print("  • Communication Protocol : A2A JSON-RPC over HTTP/SSE")
    print("  • Lead Orchestrator      : Lead M&A Partner Agent (Remote Consumer)")
    print("  • Core Model Engine      : gemini-3.8-flash (Global Vertex AI)")
    print("=" * 82 + "\n")

    service_manager = A2AServiceRunner()

    try:
        # Step A: Boot the Standalone A2A Practice Microservices
        antitrust_url = service_manager.start_service(
            agent=antitrust_agent,
            host=ANTITRUST_HOST,
            port=ANTITRUST_PORT,
            service_name="Weil Antitrust Practice Service"
        )
        tax_url = service_manager.start_service(
            agent=tax_agent,
            host=TAX_HOST,
            port=TAX_PORT,
            service_name="Weil Tax Practice Service"
        )

        # Allow servers to bind and initialize
        await asyncio.sleep(2.0)

        # Step B: Capability Discovery via Standardized `AgentCard`
        print("\n" + "=" * 82)
        print("🔍 [A2A DISCOVERY] Fetching Remote Practice Group `AgentCard` Specifications...")
        print("=" * 82)

        async with httpx.AsyncClient() as client:
            card_antitrust_res = await client.get(f"{antitrust_url}{AGENT_CARD_WELL_KNOWN_PATH}")
            card_tax_res = await client.get(f"{tax_url}{AGENT_CARD_WELL_KNOWN_PATH}")

            if card_antitrust_res.status_code == 200:
                card = card_antitrust_res.json()
                print(f"📄 Antitrust AgentCard Discovered (v{card.get('protocolVersion', '0.3.0')}):")
                print(f"   • Name        : {card.get('name')}")
                print(f"   • Description : {card.get('description')}")
                print(f"   • Endpoint    : {card.get('url')}")
                print(f"   • Transport   : {card.get('preferredTransport')}")
                print(f"   • Skills      : {[s.get('id') for s in card.get('skills', [])]}")
            else:
                print(f"⚠️ Failed to retrieve Antitrust card: {card_antitrust_res.status_code}")

            print()

            if card_tax_res.status_code == 200:
                card = card_tax_res.json()
                print(f"📄 Tax AgentCard Discovered (v{card.get('protocolVersion', '0.3.0')}):")
                print(f"   • Name        : {card.get('name')}")
                print(f"   • Description : {card.get('description')}")
                print(f"   • Endpoint    : {card.get('url')}")
                print(f"   • Transport   : {card.get('preferredTransport')}")
                print(f"   • Skills      : {[s.get('id') for s in card.get('skills', [])]}")
            else:
                print(f"⚠️ Failed to retrieve Tax card: {card_tax_res.status_code}")

        # Step C: Instantiate Remote A2A Proxies (Zero Python Code Dependency)
        print("\n" + "=" * 82)
        print("🔗 [A2A CLIENT PROXY] Connecting Lead Partner to Remote Microservices...")
        print("=" * 82)
        
        remote_antitrust = RemoteA2aAgent(
            name="antitrust_specialist",
            description="Remote Weil Antitrust Practice Service offering HSR clearance and regulatory covenant analysis.",
            agent_card=f"{antitrust_url}{AGENT_CARD_WELL_KNOWN_PATH}"
        )
        remote_tax = RemoteA2aAgent(
            name="tax_specialist",
            description="Remote Weil Tax Practice Service offering Section 338(h)(10) and transaction structuring analysis.",
            agent_card=f"{tax_url}{AGENT_CARD_WELL_KNOWN_PATH}"
        )

        # Step D: Lead M&A Partner Orchestrator
        lead_partner_agent = Agent(
            name="lead_ma_partner_agent",
            model="gemini-3.8-flash",
            instruction="""
            You are the Lead M&A Relationship Partner at Weil, Gotshal & Manges.
            When an acquisition deal structure is presented:
            1. Delegate antitrust filing requirements and regulatory covenants to the remote `antitrust_specialist` via A2A.
            2. Delegate tax structuring (asset step-up vs stock purchase) to the remote `tax_specialist` via A2A.
            3. Synthesize both specialist outputs into a unified, high-level Executive Transaction Strategy Memorandum for the client's Investment Committee.
            Format with professional headings, bulleted action items, and partner-level legal precision.
            """,
            sub_agents=[remote_antitrust, remote_tax]
        )

        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="weil_a2a_platform",
            user_id="lead_partner_ebc",
            session_id="a2a_matter_2026_01"
        )
        runner = Runner(
            agent=lead_partner_agent,
            session_service=session_service,
            app_name="weil_a2a_platform"
        )

        # Transaction Scenario
        deal_prompt = (
            "Client Nexus Capital is structuring the $2.3B acquisition of Zephyr Robotics in a mixed cash/stock transaction. "
            "Consult our Antitrust Practice for HSR filing triggers and regulatory covenants, and consult our Tax Practice "
            "for optimal structuring between a Section 338 asset step-up vs a straight stock purchase. "
            "Synthesize both specialist recommendations into a unified Executive Deal Memorandum."
        )

        print(f"\n👤 [LEAD M&A PARTNER PROMPT]:\n{deal_prompt}\n")
        print("=" * 82)
        print("📡 [LIVE A2A FEDERATION STREAM] Delegating across network boundaries...")
        print("=" * 82 + "\n")

        msg = types.Content(role="user", parts=[types.Part.from_text(text=deal_prompt)])

        async for event in runner.run_async(user_id="lead_partner_ebc", session_id=session.id, new_message=msg):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text, end="", flush=True)

        print("\n\n" + "=" * 82)
        print("💡 WHY TRUE A2A MATTERS TO WEIL")
        print("=" * 82)
        print("1. Practice Group Autonomy: The Antitrust group in D.C. and Tax group in N.Y. maintain,")
        print("   test, and deploy their own agents independently without touching M&A repo code.")
        print("2. Open Discovery Standard: Agents dynamically publish capabilities via standardized")
        print("   `AgentCard` schemas (/.well-known/agent-card.json) — no hardcoded monolithic imports.")
        print("3. Zero Process Bleed: Separate network boundaries ensure client confidentiality and")
        print("   ethical wall perimeters remain completely isolated across departments.")
        print("4. Cross-Organization Readiness: Ready to federate with co-counsel, investment banks,")
        print("   or client in-house legal departments over secure mTLS A2A connections.")
        print("=" * 82)
        print("✅ Step 5 True A2A Multi-Agent Orchestration Walkthrough Complete.\n")

    finally:
        service_manager.stop_all()


if __name__ == "__main__":
    asyncio.run(run_a2a_walkthrough())
