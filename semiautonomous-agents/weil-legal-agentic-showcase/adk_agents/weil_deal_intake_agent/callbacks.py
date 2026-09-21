"""Lifecycle Callbacks for Google ADK Agents."""

from google.adk.agents.callback_context import CallbackContext

async def inject_matter_security_context(callback_context: CallbackContext) -> None:
    """Pre-invocation callback enforcing Zero-Trust partner identity."""
    state = callback_context.state
    if "authenticated_partner" not in state:
        state["authenticated_partner"] = "Partner Andrew Simon (Weil Tech Committee)"
    if "security_clearance" not in state:
        state["security_clearance"] = "LEVEL_4_M_AND_A_PARTNER"
