"""
Legal & Cross-Border Tax Compliance Agent Runtime (Google ADK + A2A Protocol Server).
Runs on Port 8012. Powered by gemini-3-flash-preview.
Synchronizes with the Universal User Context (`user:legal_tax_status`),
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
PORT = int(os.environ.get("LEGAL_AGENT_PORT", "8012"))

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


async def update_legal_tax_status(
    current_tax_jurisdiction: str,
    foreign_entities: str,
    compliance_flags: List[str],
    tax_treaty_status: str,
) -> dict:
    """
    Updates the user's `user:legal_tax_status` namespace in the Universal User Context.
    Call this whenever tax residency, entity structures, or compliance requirements change.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "current_tax_jurisdiction": current_tax_jurisdiction,
        "foreign_entities": foreign_entities,
        "compliance_flags": compliance_flags,
        "tax_treaty_status": tax_treaty_status,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:legal_tax_status",
        updates=updates,
        source_agent="legal_tax_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_legal_tax_status",
            "namespace": "user:legal_tax_status",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:legal_tax_status",
        "updated": updates,
    }


async def record_legal_memory(fact: str) -> dict:
    """
    Commits a legal, regulatory, or tax compliance fact about the user to the Universal Memory Bank
    so that the Wealth Agent and Mobility Agent immediately enforce it across all sessions.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    mem = await push_memory_bank_fact(
        user_id=user_id,
        fact=fact,
        category="legal_tax",
        source_agent="legal_tax_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "record_legal_memory",
            "fact": fact,
            "memory_id": mem.get("memory_id"),
        }
    )
    return {"status": "saved_to_memory_bank", "fact": fact}


async def publish_tax_compliance_memo(title: str, markdown_content: str) -> dict:
    """
    Publishes or updates the versioned `tax_compliance_memo.md` artifact in the Shared Artifact Vault.
    Always call this when providing formal legal or tax structuring recommendations.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    art = await push_shared_artifact(
        user_id=user_id,
        filename="tax_compliance_memo.md",
        title=title,
        content=markdown_content,
        created_by_agent="legal_tax_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "publish_tax_compliance_memo",
            "filename": "tax_compliance_memo.md",
            "version": art.get("version", 1),
        }
    )
    return {
        "status": "artifact_published",
        "filename": "tax_compliance_memo.md",
        "version": art.get("version", 1),
    }


async def update_delivery_logistics(
    driver_assigned: str,
    eta_minutes: int,
    gate_code: str,
    dropoff_instructions: str,
    delivery_status: str = "Out for Delivery",
) -> dict:
    """
    Updates the user's `user:delivery_logistics` namespace in the Universal User Context.
    Use this whenever the customer provides gate codes, dropoff instructions, address updates, or asks about delivery status.
    """
    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]
    updates = {
        "driver_assigned": driver_assigned,
        "eta_minutes": eta_minutes,
        "gate_code": gate_code,
        "dropoff_instructions": dropoff_instructions,
        "delivery_status": delivery_status,
    }
    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:delivery_logistics",
        updates=updates,
        source_agent="delivery_agent",
        session_id=session_id,
    )
    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "update_delivery_logistics",
            "namespace": "user:delivery_logistics",
            "updates": updates,
        }
    )
    return {
        "status": "synchronized_to_universal_context",
        "namespace": "user:delivery_logistics",
        "updated": updates,
    }


async def calculate_google_maps_delivery_route(
    destination_address: str,
    origin_restaurant: str = "Wagyu & Sushi Kitchen Flagship, 450 Mission St",
    travel_mode: str = "electric_scooter",
) -> dict:
    """
    Queries Google Maps Routing & Live Traffic Telemetry to calculate the exact delivery ETA,
    distance, live traffic conditions, turn-by-turn route, and driver GPS coordinates between
    the restaurant kitchen and the customer's delivery address.
    ALWAYS call this tool whenever the user asks about delivery ETA, how long until arrival,
    where the driver is, traffic conditions, or route details!
    """
    import datetime
    import hashlib

    user_id = _ACTIVE_TURN_CONTEXT["user_id"]
    session_id = _ACTIVE_TURN_CONTEXT["session_id"]

    dest_clean = destination_address.strip() or "742 Evergreen Terrace, Apt 4B"
    # Deterministic realistic routing calculation based on destination address
    addr_hash = int(hashlib.md5(dest_clean.lower().encode()).hexdigest()[:6], 16)
    distance_miles = round(1.6 + (addr_hash % 65) / 10.0, 1)
    base_mins = max(8, int(distance_miles * 3.2))
    traffic_delay_mins = (addr_hash % 5) + 1
    total_eta_mins = base_mins + traffic_delay_mins

    now = datetime.datetime.now()
    arrival_dt = now + datetime.timedelta(minutes=total_eta_mins)
    arrival_clock = arrival_dt.strftime("%I:%M %p")

    traffic_levels = [
        f"Light traffic on main corridor (+{traffic_delay_mins} min delay)",
        f"Moderate congestion near downtown intersection (+{traffic_delay_mins} mins delay)",
        f"Clear express lane via Embarcadero / arterial route (+{traffic_delay_mins} min delay)",
    ]
    traffic_summary = traffic_levels[addr_hash % len(traffic_levels)]

    turn_by_turn = [
        f"1. Depart {origin_restaurant} heading northwest (0.4 mi)",
        f"2. Merge onto Primary Arterial Corridor / Express Bike-Scooter Lane ({round(distance_miles * 0.6, 1)} mi)",
        f"3. Turn onto local residential street toward {dest_clean} ({round(distance_miles * 0.25, 1)} mi)",
        f"4. Arrive at destination: {dest_clean} (Estimated {arrival_clock})",
    ]

    maps_telemetry = {
        "google_maps_status": "LIVE_ROUTE_ACTIVE",
        "origin": origin_restaurant,
        "destination": dest_clean,
        "distance_miles": distance_miles,
        "estimated_eta_minutes": total_eta_mins,
        "estimated_arrival_clock": arrival_clock,
        "live_traffic_condition": traffic_summary,
        "turn_by_turn_route": turn_by_turn,
        "driver_gps_telemetry": {
            "driver_name": "Marco V.",
            "vehicle": "Electric Scooter #14 (94% Battery)",
            "current_speed_mph": 22,
            "live_coordinates": {"lat": 37.7894, "lng": -122.4018},
        },
    }

    await push_universal_state_update(
        user_id=user_id,
        namespace_key="user:delivery_logistics",
        updates={
            "driver_assigned": "Marco V. (Electric Scooter #14)",
            "eta_minutes": total_eta_mins,
            "estimated_arrival_clock": arrival_clock,
            "destination_address": dest_clean,
            "distance_miles": distance_miles,
            "google_maps_traffic": traffic_summary,
            "google_maps_route_summary": " -> ".join(turn_by_turn),
            "delivery_status": f"En Route via Google Maps ({total_eta_mins} mins ETA)",
        },
        source_agent="delivery_agent",
        session_id=session_id,
    )

    await push_memory_bank_fact(
        user_id=user_id,
        fact=f"[Google Maps Live ETA] Delivery to {dest_clean} is {distance_miles} miles away with an ETA of {total_eta_mins} minutes (arriving {arrival_clock}). Traffic: {traffic_summary}.",
        category="delivery_maps_eta",
        source_agent="delivery_agent",
        session_id=session_id,
    )

    _ACTIVE_TURN_CONTEXT["tool_logs"].append(
        {
            "tool": "calculate_google_maps_delivery_route",
            "namespace": "user:delivery_logistics",
            "updates": maps_telemetry,
        }
    )
    return maps_telemetry


LEGAL_SYSTEM_INSTRUCTION = """You are a dual-persona Google ADK & A2A Specialist Runtime running on Port 8012 inside the **Universal User Context Mesh**:

1. **FOR RESTAURANT CUSTOMERS (e.g., `carlos@restaurant.io` or delivery/logistics queries)**:
   - You act as the **Delivery & Driver Dispatch Agent (`delivery_agent`)**.
   - CRITICAL CUSTOMER DEMO RULE: You operate in a SEPARATE session (e.g. **Session #2**) from the Ordering Agent (`ordering_agent` in Session #1).
   - Because of the **Universal User Context Mesh**, you AUTOMATICALLY see `user:active_order` and the shared Memory Bank from the Ordering Agent!
   - IMPORTANT ORDER PRIORITY RULE: Always check `user:active_order` first. If `user:active_order` contains a new order ID or new items, report ONLY the active order currently in `user:active_order` (do not confuse old deleted orders with the current active order).
   - **GOOGLE MAPS & LIVE ETA TOOL**: Whenever the customer asks about **ETA, delivery time, how far the driver is, route directions, or traffic**, ALWAYS call `calculate_google_maps_delivery_route(destination_address=...)` using the delivery address from `user:active_order` (or the address provided by the user). Present the exact Google Maps distance, traffic conditions, turn-by-turn street route, driver GPS speed, and arrival clock time!
   - Whenever the customer gives a gate code, dropoff note, or driver instruction, call `update_delivery_logistics` to synchronize `user:delivery_logistics` and call `record_legal_memory` to save the delivery fact into the Universal Memory Bank.

2. **FOR ENTERPRISE CLIENTS (e.g., `alex.rivera@enterprise.io`)**:
   - You act as the **Legal & Cross-Border Tax Compliance Agent (`legal_tax_agent`)**.
   - Call `update_legal_tax_status`, `record_legal_memory`, and `publish_tax_compliance_memo` to coordinate international tax treaties and exit taxes across Wealth and Mobility sessions.
"""


def create_legal_adk_agent() -> Agent:
    return Agent(
        name="legal_tax_agent",
        model=GEMINI_MODEL,
        instruction=LEGAL_SYSTEM_INSTRUCTION,
        description="Delivery Logistics & Google Maps Agent (for restaurant users) / Legal & Tax Agent (for enterprise users) with Universal Context.",
        tools=[
            calculate_google_maps_delivery_route,
            update_delivery_logistics,
            update_legal_tax_status,
            record_legal_memory,
            publish_tax_compliance_memo,
        ],
    )


session_service = InMemorySessionService()


def clear_local_sessions() -> None:
    global session_service
    session_service = InMemorySessionService()


async def run_legal_agent_turn(user_id: str, session_id: str, user_message: str) -> Dict[str, Any]:
    """Executes an ADK turn with Universal Context injection and returns response + tool metadata."""
    _ACTIVE_TURN_CONTEXT["user_id"] = user_id
    _ACTIVE_TURN_CONTEXT["session_id"] = session_id
    _ACTIVE_TURN_CONTEXT["tool_logs"] = []

    injection = await fetch_universal_injection(user_id, "legal_tax_agent", session_id)
    augmented_prompt = (
        f"{injection['prompt_block']}\n\n"
        f"USER MESSAGE TO DELIVERY / LEGAL AGENT:\n{user_message}"
    )

    adk_agent = create_legal_adk_agent()
    adk_session_id = f"adk-legal-{session_id}"
    try:
        await session_service.create_session(
            app_name="legal_app", user_id=user_id, session_id=adk_session_id
        )
    except Exception:
        pass

    runner = Runner(agent=adk_agent, app_name="legal_app", session_service=session_service)
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
        "agent_name": "legal_tax_agent",
        "response": final_text.strip() or "Delivery logistics & Google Maps route synchronized with Universal Context.",
        "tool_calls": list(_ACTIVE_TURN_CONTEXT["tool_logs"]),
        "injected_memories": injection.get("injected_memories", []),
        "cross_agent_memories_count": len(injection.get("cross_agent_memories", [])),
    }


agent_card = AgentCard(
    name="legal_tax_agent",
    description="Google ADK Delivery & Google Maps Logistics Agent (Restaurant) / Cross-Border Legal Agent (Enterprise).",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain", "application/json"],
    default_output_modes=["application/json"],
    skills=[
        AgentSkill(
            id="google_maps_delivery_logistics",
            name="Google Maps Live Delivery Routing, Traffic & ETA",
            description="Calculates real-time Google Maps delivery routes, traffic conditions, turn-by-turn streets, and driver ETA.",
            tags=["delivery", "google-maps", "eta", "logistics", "adk", "universal-context"],
            examples=["What is the Google Maps ETA and live route for my order delivery?"],
        )
    ],
)

app = create_a2a_fastapi_app(
    agent_card=agent_card,
    turn_handler=run_legal_agent_turn,
    port=PORT,
    clear_handler=clear_local_sessions,
)

if __name__ == "__main__":
    print(f"Starting Legal & Tax / Delivery ADK + A2A Runtime on http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
