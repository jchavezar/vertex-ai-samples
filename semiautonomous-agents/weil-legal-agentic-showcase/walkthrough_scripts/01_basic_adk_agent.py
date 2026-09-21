"""
Step 1: Building a Foundational Agent with Google ADK
------------------------------------------------------
This concise script demonstrates how to define a specialized legal agent using
Google's Agent Development Kit (ADK) and Gemini 3.8 Flash.

Core Concepts Introduced:
1. Agent definition (name, model, instruction)
2. Native FunctionTool definition with automatic schema generation
3. Lifecycle callbacks (before_agent_callback) for Zero-Trust context injection
4. Local execution via ADK Runner
"""

import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Define a Deterministic Python Tool
#    (ADK automatically extracts JSON schema from type hints and docstrings)
# ---------------------------------------------------------------------------
def check_client_clearance(client_name: str, target_company: str) -> dict:
    """Verifies whether an engagement passes conflicts and ethical wall clearance.
    
    Args:
        client_name: The prospective corporate client name.
        target_company: The target or counterparty entity.
    """
    print(f"\n⚡ [TOOL CALL] Executing check_client_clearance for '{client_name}' -> '{target_company}'...")
    
    # Deterministic rule lookup
    restricted_targets = ["AlphaCorp", "Initech Global", "Omni Consumer Products"]
    if target_company in restricted_targets:
        return {
            "status": "CLEARANCE_DENIED",
            "reason": f"Active Ethical Wall: Weil represents {target_company} in parallel regulatory filings.",
            "action_required": "Refer to Weil Conflicts Committee for partner review."
        }
    
    return {
        "status": "CLEARANCE_GRANTED",
        "matter_id": f"MATTER-2026-{abs(hash(client_name)) % 10000}",
        "billing_code": "CORP-MA-8820",
        "authorized_partners": ["E. Vance", "M. Ross"]
    }

clearance_tool = FunctionTool(func=check_client_clearance)

# ---------------------------------------------------------------------------
# 2. Lifecycle Callback: Zero-Trust Security / Matter Injection
# ---------------------------------------------------------------------------
async def inject_matter_context(callback_context: CallbackContext) -> None:
    """Injects authenticated partner identity before the agent executes."""
    state = callback_context.state
    if "session_operator" not in state:
        state["session_operator"] = "Partner Andrew Simon (Weil Tech Committee)"
    print(f"🔒 [CALLBACK] Injected Zero-Trust Session Context: {state['session_operator']}")

# ---------------------------------------------------------------------------
# 3. Instantiate the Google ADK Agent
# ---------------------------------------------------------------------------
legal_onboarding_agent = Agent(
    name="weil_onboarding_agent",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil Legal Engagement & Intake Agent.
    Your mandate:
    1. Always verify conflict clearance using the `check_client_clearance` tool before proceeding.
    2. If clearance is denied, immediately report the Ethical Wall conflict and halt drafting.
    3. If clearance is granted, summarize the engagement parameters clearly for the partner.
    Keep explanations professional, precise, and structured.
    """,
    tools=[clearance_tool],
    before_agent_callback=inject_matter_context,
)

# ---------------------------------------------------------------------------
# 4. Local Execution Demo
# ---------------------------------------------------------------------------
async def main():
    print("=" * 70)
    print("🚀 Google ADK Basics — Running Agent Locally with gemini-3.8-flash")
    print("=" * 70)
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="weil_showcase",
        user_id="partner_001",
        session_id="session_test_01"
    )
    
    runner = Runner(
        agent=legal_onboarding_agent,
        session_service=session_service,
        app_name="weil_showcase"
    )
    
    # Test Query
    prompt = "Please run intake for prospective client 'Nexus Capital' acquiring 'Zephyr Robotics'."
    print(f"\n👤 [USER PROMPT]: {prompt}")
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )
    
    print("\n🤖 [AGENT EXECUTION]:")
    async for event in runner.run_async(
        user_id="partner_001",
        session_id=session.id,
        new_message=content
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
    print("\n\n✅ Execution Complete.")

if __name__ == "__main__":
    asyncio.run(main())
