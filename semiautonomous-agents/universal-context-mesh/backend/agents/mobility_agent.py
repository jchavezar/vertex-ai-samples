"""
Global Mobility & Lifestyle Concierge Agent Runtime (Google ADK + A2A Protocol Server).
Runs on Port 8013. Powered by gemini-3-flash-preview.
Synchronizes with the Universal User Context (`user:mobility_plan`),
Universal Memory Bank, and Shared Artifact Vault.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
PORT = int(os.environ.get("MOBILITY_AGENT_PORT", "8013"))

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


async def update_mobility_plan(
    target_destinations: List[str],
    preferred_timeline: str,
    schengen_days_used_rolling_180: int,
    visa_pathway: str,
) -> dict:
    """
    Updates the user's `user:mobility_plan` namespace in the Universal User Context.
    Call this whenever travel plans, relocation cities, Schengen day counts, or visa pathways are discussed.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "target_destinations": target_destinations,
        "preferred_timeline": preferred_timeline,
        "schengen_days_used_rolling_180": schengen_days_used_rolling_180,
        "schengen_days_remaining": max(0, 90 - schengen_days_used_rolling_180),
        "visa_pathway": visa_pathway,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:mobility_plan",
        updates=updates,
        source_agent="mobility_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_mobility_plan",
            "namespace": "user:mobility_plan",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:mobility_plan",
        "updated": updates,
    }


async def record_mobility_memory(fact: str) -> dict:
    """
    Commits a mobility, visa, or residency day-count fact about the user to the Universal Memory Bank
    so that the Wealth Agent and Legal Agent immediately factor it into tax and budget plans.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    mem = await push_memory_bank_fact(
        user_id=user_id,
        fact=fact,
        category="mobility",
        source_agent="mobility_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "record_mobility_memory",
            "fact": fact,
            "memory_id": mem.get("memory_id"),
        }
    )
    return {"status": "saved_to_memory_bank", "fact": fact}


async def publish_relocation_dossier(title: str, markdown_content: str) -> dict:
    """
    Publishes or updates the versioned `relocation_dossier.md` artifact in the Shared Artifact Vault.
    Always call this when creating an international relocation or visa execution roadmap.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    art = await push_shared_artifact(
        user_id=user_id,
        filename="relocation_dossier.md",
        title=title,
        content=markdown_content,
        created_by_agent="mobility_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "publish_relocation_dossier",
            "filename": "relocation_dossier.md",
            "version": art.get("version", 1),
        }
    )
    return {
        "status": "artifact_published",
        "filename": "relocation_dossier.md",
        "version": art.get("version", 1),
    }


async def update_support_ticket(
    ticket_id: str,
    resolution_notes: str,
    kitchen_verified: bool = True,
    vip_credit_usd: float = 0.0,
) -> dict:
    """
    Updates the user's `user:support_ticket` namespace in the Universal User Context.
    Use this whenever resolving customer support questions, verifying allergy safety with the kitchen, or issuing VIP credits.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "ticket_id": ticket_id,
        "resolution_notes": resolution_notes,
        "kitchen_verified": kitchen_verified,
        "vip_credit_usd": vip_credit_usd,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:support_ticket",
        updates=updates,
        source_agent="support_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_support_ticket",
            "namespace": "user:support_ticket",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:support_ticket",
        "updated": updates,
    }


MOBILITY_SYSTEM_INSTRUCTION = """You are a dual-persona Google ADK & A2A Specialist Runtime running on Port 8013 inside the **Universal User Context Mesh**:

1. **FOR RESTAURANT CUSTOMERS (e.g., `carlos@restaurant.io` or support/allergy/kitchen queries)**:
   - You act as the **Kitchen & VIP Customer Support Agent (`support_agent`)**.
   - CRITICAL CUSTOMER DEMO RULE: You operate in a SEPARATE session (e.g. **Session #3**) from BOTH the Ordering Agent (`Session #1`) and the Delivery Agent (`Session #2`).
   - Because of the **Universal User Context Mesh**, you AUTOMATICALLY see BOTH `user:active_order` (from Ordering Agent) and `user:delivery_logistics` (from Delivery Agent), plus the shared Memory Bank!
   - When Carlos contacts you, proactively confirm the exact items he ordered in Session #1 AND the gate code/driver instructions he gave to the Delivery Agent in Session #2 without asking him to repeat them!
   - Call `update_support_ticket` and `record_mobility_memory` to record kitchen allergy checks or VIP credits.

2. **FOR ENTERPRISE CLIENTS (e.g., `alex.rivera@enterprise.io`)**:
   - You act as the **Global Mobility & Lifestyle Concierge Agent (`mobility_agent`)**.
   - Call `update_mobility_plan`, `record_mobility_memory`, and `publish_relocation_dossier` to coordinate visas and relocation timelines across Wealth and Legal sessions.

CRITICAL RULES:
- Always inspect the `UNIVERSAL USER CONTEXT MESH` block in the prompt and explicitly highlight how context created in other sessions (e.g., Ordering Session #1 and Delivery Session #2) was automatically shared with your session.
"""


def create_mobility_adk_agent() -> Agent:
    return Agent(
        name="mobility_agent",
        model=GEMINI_MODEL,
        instruction=MOBILITY_SYSTEM_INSTRUCTION,
        description="Kitchen & VIP Support Agent (for restaurant users) / Global Mobility Agent (for enterprise users) with Universal Context.",
        tools=[
            update_support_ticket,
            update_mobility_plan,
            record_mobility_memory,
            publish_relocation_dossier,
        ],
    )


session_service = InMemorySessionService()


async def run_mobility_agent_turn(user_id: str, session_id: str, user_message: str) -> Dict[str, Any]:
    """Executes an ADK turn with Universal Context injection and returns response + tool metadata."""
    _ACTIVE_TURN_CONTEXT["user_id"] = user_id
    _ACTIVE_TURN_CONTEXT["session_id"] = session_id
    _ACTIVE_TURN_CONTEXT["tool_logs"] = []

    injection = await fetch_universal_injection(user_id, "mobility_agent", session_id)
    augmented_prompt = (
        f"{injection['prompt_block']}\n\n"
        f"USER MESSAGE TO GLOBAL MOBILITY AGENT:\n{user_message}"
    )

    adk_agent = create_mobility_adk_agent()
    adk_session_id = f"adk-mobility-{session_id}"
    try:
        await session_service.create_session(
            app_name="mobility_app", user_id=user_id, session_id=adk_session_id
        )
    except Exception:
        pass

    runner = Runner(agent=adk_agent, app_name="mobility_app", session_service=session_service)
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
        "agent_name": "mobility_agent",
        "response": final_text.strip() or "Global Mobility plan updated and synchronized with Universal Context.",
        "tool_calls": list(_ACTIVE_TURN_CONTEXT["tool_logs"]),
        "injected_memories": injection.get("injected_memories", []),
        "cross_agent_memories_count": len(injection.get("cross_agent_memories", [])),
    }


agent_card = AgentCard(
    name="mobility_agent",
    description="Google ADK Global Mobility & Lifestyle Concierge Agent with Universal Context synchronization.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain", "application/json"],
    default_output_modes=["application/json"],
    skills=[
        AgentSkill(
            id="global_mobility",
            name="International Relocation & Visa Pathways",
            description="Plans Swiss Permit B, Golden Visas, Schengen 90/180 day compliance, and executive family relocation.",
            tags=["mobility", "relocation", "visa", "adk", "universal-context"],
            examples=["Plan my family relocation to Zurich in Q1 2027 while keeping Schengen days compliant"],
        )
    ],
)

def clear_local_sessions() -> None:
    global session_service
    session_service = InMemorySessionService()


app = create_a2a_fastapi_app(
    agent_card=agent_card,
    turn_handler=run_mobility_agent_turn,
    port=PORT,
    clear_handler=clear_local_sessions,
)

if __name__ == "__main__":
    print(f"Starting Global Mobility ADK + A2A Runtime on http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
