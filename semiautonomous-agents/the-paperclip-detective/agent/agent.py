"""
The Paperclip Detective — forensic agent for the Gemini Enterprise file-upload mystery.

Question: when a user clicks the GE chat paperclip and uploads a file, does the
file arrive at the agent as an INLINE Part (model sees it natively) or as an
ADK ARTIFACT (requires `load_artifacts` to fetch)?

This agent never tries to "answer" anything. It only inspects what it received
and writes a structured forensic report back to the user.
"""
import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext, load_artifacts

logger = logging.getLogger("paperclip-detective")
logger.setLevel(logging.INFO)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _summarize_part(part: Any) -> dict:
    """Extract the shape of a single google.genai.types.Part without leaking bytes."""
    out: dict = {}
    if getattr(part, "text", None):
        out["kind"] = "text"
        text = part.text
        out["text_len"] = len(text)
        out["text_preview"] = text[:120] + ("…" if len(text) > 120 else "")
        return out
    inline = getattr(part, "inline_data", None)
    if inline is not None:
        data = getattr(inline, "data", b"") or b""
        out["kind"] = "inline_data"
        out["mime_type"] = getattr(inline, "mime_type", None)
        out["byte_size"] = len(data)
        return out
    file_data = getattr(part, "file_data", None)
    if file_data is not None:
        out["kind"] = "file_data"
        out["mime_type"] = getattr(file_data, "mime_type", None)
        out["file_uri"] = getattr(file_data, "file_uri", None)
        return out
    func_call = getattr(part, "function_call", None)
    if func_call is not None:
        out["kind"] = "function_call"
        out["name"] = getattr(func_call, "name", None)
        return out
    func_resp = getattr(part, "function_response", None)
    if func_resp is not None:
        out["kind"] = "function_response"
        out["name"] = getattr(func_resp, "name", None)
        return out
    out["kind"] = "unknown"
    return out


# -----------------------------------------------------------------------------
# Tool 1: inspect the inline Parts the model is currently looking at
# -----------------------------------------------------------------------------
def inspect_inline_parts(tool_context: ToolContext) -> dict:
    """Inspect the user's current message Parts (what the LLM sees inline RIGHT NOW).

    Reads `tool_context.user_content.parts` and returns a structured snapshot
    of every Part — text, inline_data, file_data, function_call, etc.

    Use this to find out whether a file the user just attached arrived as an
    INLINE Part (mime_type=application/pdf, byte_size>0) or NOT (in which case
    you must check the artifact service via inspect_artifact_store).
    """
    user_content = getattr(tool_context, "user_content", None)
    if user_content is None:
        snapshot = {"present": False, "reason": "tool_context.user_content is None"}
        logger.info("INSPECT_INLINE: %s", snapshot)
        return snapshot

    parts = list(getattr(user_content, "parts", []) or [])
    snapshot = {
        "present": True,
        "role": getattr(user_content, "role", None),
        "part_count": len(parts),
        "parts": [_summarize_part(p) for p in parts],
    }
    snapshot["has_inline_file"] = any(p.get("kind") == "inline_data" and p.get("mime_type") for p in snapshot["parts"])
    snapshot["has_file_data_uri"] = any(p.get("kind") == "file_data" for p in snapshot["parts"])
    logger.info("INSPECT_INLINE: %s", snapshot)
    return snapshot


# -----------------------------------------------------------------------------
# Tool 2: inspect ADK's artifact service for this session
# -----------------------------------------------------------------------------
async def inspect_artifact_store(tool_context: ToolContext) -> dict:
    """Inspect the ADK artifact service for this session.

    Lists artifact names registered for the current session, then loads each
    one to capture mime type + byte size. Use this to find out whether the
    file the user uploaded landed in the artifact store (in which case the
    `load_artifacts` tool — also registered on this agent — would surface it).
    """
    snapshot: dict = {"available": True, "artifact_names": [], "artifacts": []}
    try:
        names = await tool_context.list_artifacts()
    except Exception as exc:  # noqa: BLE001 — diagnostic, want every failure mode
        snapshot["available"] = False
        snapshot["error"] = f"list_artifacts() raised: {type(exc).__name__}: {exc}"
        logger.info("INSPECT_ARTIFACTS: %s", snapshot)
        return snapshot

    snapshot["artifact_names"] = list(names or [])
    for name in snapshot["artifact_names"]:
        try:
            artifact = await tool_context.load_artifact(name)
            snapshot["artifacts"].append({
                "name": name,
                "summary": _summarize_part(artifact) if artifact is not None else None,
            })
        except Exception as exc:  # noqa: BLE001
            snapshot["artifacts"].append({"name": name, "error": f"{type(exc).__name__}: {exc}"})

    logger.info("INSPECT_ARTIFACTS: %s", snapshot)
    return snapshot


# -----------------------------------------------------------------------------
# Agent
# -----------------------------------------------------------------------------
INSTRUCTION = """\
You are The Paperclip Detective. Your ONLY job is forensic: figure out HOW any
file the user just attached arrived at this agent.

Procedure — follow EVERY step on EVERY turn, no exceptions:

1. Call `inspect_inline_parts` to see what Parts are in the user's current
   message (the inline view the model itself is looking at).
2. Call `inspect_artifact_store` to see what artifacts ADK has stored for
   this session.
3. (Optional) Call `load_artifacts` if `inspect_artifact_store` reported any
   artifact names — this confirms the standard ADK retrieval path works.
4. Write a verdict in this exact markdown shape and return it as your final
   reply:

   ## Verdict
   - Inline parts present: <yes/no>
     - If yes, list each part's `kind`, `mime_type`, `byte_size`.
   - Artifact store entries: <count>
     - If >0, list each artifact name + mime + byte_size.
   - **Routing path:** one of `INLINE_ONLY`, `ARTIFACT_ONLY`, `BOTH`, `NEITHER`.
   - **Implication:** one short sentence explaining what this means for an ADK
     agent that wants to read the file.

NEVER answer the user's question about the file's contents. NEVER summarize the
attachment. The point is to expose the routing — not to use the file. If the
user asks "what's in this file", reply with the verdict above plus the line
"(I am a forensic agent — I do not read file contents.)"
"""


root_agent = LlmAgent(
    name="paperclip_detective",
    model="gemini-2.5-flash",
    instruction=INSTRUCTION,
    tools=[inspect_inline_parts, inspect_artifact_store, load_artifacts],
)
