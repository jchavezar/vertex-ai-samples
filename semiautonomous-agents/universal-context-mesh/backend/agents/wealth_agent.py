"""
Wealth & Portfolio Strategy Agent Runtime (Google ADK + A2A Protocol Server).
Runs on Port 8011. Powered by gemini-3-flash-preview.
Synchronizes with the Universal User Context (`user:financial_profile`),
Universal Memory Bank, and Shared Artifact Vault.
"""

import os
from pathlib import Path
from typing import Any, Dict

import uvicorn
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
PORT = int(os.environ.get("WEALTH_AGENT_PORT", "8011"))

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from backend.a2a_server_helper import create_a2a_fastapi_app
from backend.context_bridge import (
    fetch_universal_injection,
    push_memory_bank_fact,
    push_shared_artifact,
    push_universal_state_update,
)

_ACTIVE_TURN_CONTEXT: Dict[str, Any] = {
    "user_id": "alex.rivera@enterprise.io",
    "session_id": "global",
    "tool_logs": [],
}


async def update_financial_profile(
    liquid_net_worth_usd: float,
    recent_liquidity_event: str,
    core_holdings: str,
    risk_tolerance: str,
) -> dict:
    """
    Updates the user's `user:financial_profile` namespace in the Universal User Context.
    Use this whenever the user shares new liquidity events, asset sales, portfolio values, or risk preferences.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "liquid_net_worth_usd": liquid_net_worth_usd,
        "recent_liquidity_event": recent_liquidity_event,
        "core_holdings": core_holdings,
        "risk_tolerance": risk_tolerance,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:financial_profile",
        updates=updates,
        source_agent="wealth_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_financial_profile",
            "namespace": "user:financial_profile",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:financial_profile",
        "updated": updates,
    }


async def record_wealth_memory(fact: str) -> dict:
    """
    Commits a key financial or portfolio fact about the user to the Universal Memory Bank
    so that the Legal/Tax Agent and Mobility Agent immediately know it across all sessions.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    mem = await push_memory_bank_fact(
        user_id=user_id,
        fact=fact,
        category="financial",
        source_agent="wealth_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "record_wealth_memory",
            "fact": fact,
            "memory_id": mem.get("memory_id"),
        }
    )
    return {"status": "saved_to_memory_bank", "fact": fact}


async def publish_portfolio_artifact(title: str, markdown_content: str) -> dict:
    """
    Publishes or updates the versioned `portfolio_analysis.md` artifact in the Shared Artifact Vault.
    Always call this when creating a formal asset allocation or wealth restructuring plan.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    art = await push_shared_artifact(
        user_id=user_id,
        filename="portfolio_analysis.md",
        title=title,
        content=markdown_content,
        created_by_agent="wealth_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "publish_portfolio_artifact",
            "filename": "portfolio_analysis.md",
            "version": art.get("version", 1),
        }
    )
    return {
        "status": "artifact_published",
        "filename": "portfolio_analysis.md",
        "version": art.get("version", 1),
    }


async def update_active_order(
    order_id: str,
    items_summary: str,
    dietary_notes: str,
    total_usd: float,
    status: str = "Confirmed & In Kitchen",
) -> dict:
    """
    Updates the user's `user:active_order` namespace in the Universal User Context.
    Use this whenever a restaurant customer (e.g. Carlos) places or modifies a food order, adds items, or specifies allergies.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "order_id": order_id,
        "status": status,
        "items_summary": items_summary,
        "dietary_notes": dietary_notes,
        "total_usd": total_usd,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:active_order",
        updates=updates,
        source_agent="ordering_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_active_order",
            "namespace": "user:active_order",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:active_order",
        "updated": updates,
    }


async def publish_order_receipt(order_id: str, receipt_markdown: str) -> dict:
    """
    Publishes or updates the live `order_receipt_ORD9042.md` artifact in the Shared Artifact Vault
    so the Delivery Agent and Customer Support Agent can view the exact itemized ticket.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    filename = f"order_receipt_{order_id.replace('#', '')}.md"
    art = await push_shared_artifact(
        user_id=user_id,
        filename=filename,
        title=f"Live Order Ticket {order_id}",
        content=receipt_markdown,
        created_by_agent="ordering_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "publish_order_receipt",
            "filename": filename,
            "version": art.get("version", 1),
        }
    )
    return {"status": "artifact_published", "filename": filename}


WEALTH_SYSTEM_INSTRUCTION = """You are a dual-persona Google ADK & A2A Specialist Runtime running on Port 8011 inside the **Universal User Context Mesh**:

1. **FOR RESTAURANT CUSTOMERS (e.g., `carlos@restaurant.io` or food/ordering queries)**:
   - You act as the **Restaurant Ordering & Menu Agent (`ordering_agent`)**.
   - You take food & drink orders, modifications, and dietary/allergy notes in **Session #1**.
   - CRITICAL: Whenever Carlos adds or changes items (e.g., Truffle Wagyu Gyoza, Spicy Tuna Crispy Rice, Yuzu Sparkling Water, peanut allergy, or delivery address), call `update_active_order` to synchronize `user:active_order`, call `record_wealth_memory` to save the order fact to the Universal Memory Bank, and call `publish_order_receipt` so that when Carlos opens a SEPARATE session with the Delivery Agent (`:8012`), the Delivery Agent already knows every item ordered without asking Carlos to repeat himself!

2. **FOR ENTERPRISE WEALTH CLIENTS (e.g., `alex.rivera@enterprise.io`)**:
   - You act as the **Wealth & Portfolio Strategy Agent (`wealth_agent`)**.
   - Call `update_financial_profile`, `record_wealth_memory`, and `publish_portfolio_artifact` to synchronize portfolio allocations across Legal/Tax and Mobility agents.

CRITICAL RULES:
- Always inspect the `UNIVERSAL USER CONTEXT MESH` block provided in the prompt. Explicitly acknowledge facts or delivery/support notes discovered by peer agents in other sessions.
- Keep your response warm, structured, and explicitly confirm that the order/context has been synchronized across the Universal Mesh for other agents (such as the Delivery Agent).
"""


def create_wealth_adk_agent() -> Agent:
    return Agent(
        name="wealth_agent",
        model=GEMINI_MODEL,
        instruction=WEALTH_SYSTEM_INSTRUCTION,
        description="Restaurant Ordering Agent (for restaurant users) / Wealth Strategy Agent (for enterprise users) with Universal Context.",
        tools=[
            update_active_order,
            publish_order_receipt,
            update_financial_profile,
            record_wealth_memory,
            publish_portfolio_artifact,
        ],
    )


session_service = InMemorySessionService()


async def run_wealth_agent_turn(user_id: str, session_id: str, user_message: str) -> Dict[str, Any]:
    """Executes an ADK turn with Universal Context injection and returns response + tool metadata."""
    _ACTIVE_TURN_CONTEXT["user_id"] = user_id
    _ACTIVE_TURN_CONTEXT["session_id"] = session_id
    _ACTIVE_TURN_CONTEXT["tool_logs"] = []

    injection = await fetch_universal_injection(user_id, "wealth_agent", session_id)
    augmented_prompt = (
        f"{injection['prompt_block']}\n\n"
        f"USER MESSAGE TO WEALTH AGENT:\n{user_message}"
    )

    adk_agent = create_wealth_adk_agent()
    adk_session_id = f"adk-wealth-{session_id}"
    try:
        await session_service.create_session(
            app_name="wealth_app", user_id=user_id, session_id=adk_session_id
        )
    except Exception:
        pass

    runner = Runner(agent=adk_agent, app_name="wealth_app", session_service=session_service)
    final_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=adk_session_id,
        new_message=genai_types.Content(
            role="user", parts=[genai_types.Part.from_text(text=augmented_prompt)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_text += part.text

    return {
        "agent_name": "wealth_agent",
        "response": final_text.strip() or "Wealth profile analyzed and synchronized with Universal Context.",
        "tool_calls": list(_ACTIVE_TURN_CONTEXT["tool_logs"]),
        "injected_memories": injection.get("injected_memories", []),
        "cross_agent_memories_count": len(injection.get("cross_agent_memories", [])),
    }


agent_card = AgentCard(
    name="wealth_agent",
    description="Google ADK Wealth & Portfolio Strategy Agent with Universal Context synchronization.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain", "application/json"],
    default_output_modes=["application/json"],
    skills=[
        AgentSkill(
            id="portfolio_strategy",
            name="Cross-Border Portfolio & Liquidity Strategy",
            description="Analyzes liquid net worth, secondary equity sales, and multi-currency hedging.",
            tags=["wealth", "finance", "portfolio", "adk", "universal-context"],
            examples=["I sold $5M in NVDA stock and want to relocate to Zurich", "Rebalance my portfolio for CHF exposure"],
        )
    ],
)

def clear_local_sessions() -> None:
    global session_service
    session_service = InMemorySessionService()


app = create_a2a_fastapi_app(
    agent_card=agent_card,
    turn_handler=run_wealth_agent_turn,
    port=PORT,
    clear_handler=clear_local_sessions,
)

if __name__ == "__main__":
    print(f"Starting Wealth ADK + A2A Runtime on http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
