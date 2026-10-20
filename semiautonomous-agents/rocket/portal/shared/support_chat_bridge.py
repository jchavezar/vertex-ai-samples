# -*- coding: utf-8 -*-
"""Rocket × Google Cloud Portal — Bottom-Right AI + Live Human Google Chat Support Bridge.

Connects the Unified Portal (`/`, `/glossary`, `/docs/*`, `/square/*`) directly to:
1. Vertex AI `gemini-3.8-flash` (Portal-Grounded AI Support Assistant)
2. Internal Google Workspace Chat Space:
   `spaces/AAQA9IvwTUs` ("Detroit Dream Team: Halloween Hackathon")
   with real-time 2-way thread synchronization so Rocket participants can talk to
   Jesus Chavez, Sundar Chellappa, Angela Kavanaugh, Joris Wynendaele, Luis Lopez,
   and Ricky Merrefield directly from the bottom-right overlay!
"""

import json
import os
import time
import urllib.parse
import urllib.request
import uuid
from typing import Any, Dict, List, Optional

# Default target space: "Detroit Dream Team: Halloween Hackathon"
DEFAULT_GCHAT_SPACE = os.environ.get("ROCKET_GCHAT_SPACE", "spaces/AAQA9IvwTUs")
DEFAULT_GCHAT_SPACE_NAME = "Detroit Dream Team: Halloween Hackathon"
BRIDGE_SECRET = os.environ.get("ROCKET_BRIDGE_SECRET", "rocket:e3a48aa96ebeb0731e4c751d")
GCS_TICKETS_URI = "https://storage.googleapis.com/vtxdemos-abnb-images/rocket_support/tickets_v1.json"

# In-memory state (also backed up to /tmp and synced via Cloudtop bridge)
_BRIDGE_STATE: Dict[str, Any] = {
    "cxf_token": "",
    "token_updated_at": 0.0,
    "space_id": DEFAULT_GCHAT_SPACE,
    "space_name": DEFAULT_GCHAT_SPACE_NAME,
    "bot_sender_email": "jesusarguelles@google.com",
}

# Ticket store: ticket_id -> {
#   "ticket_id": str,
#   "user_name": str,
#   "user_email": str,
#   "track": str,
#   "created_at": float,
#   "space_id": str,
#   "thread_name": str,  # e.g. "spaces/AAQA9IvwTUs/threads/..."
#   "seen_gchat_msg_ids": List[str],
#   "pending_outbound": List[Dict[str, Any]],
#   "messages": List[Dict[str, Any]],
# }
_TICKETS: Dict[str, Dict[str, Any]] = {}
_LOCAL_STORE_PATH = "/tmp/rocket_support_tickets.json"


def _load_tickets_from_disk() -> None:
    if _TICKETS:
        return
    try:
        if os.path.exists(_LOCAL_STORE_PATH):
            with open(_LOCAL_STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _TICKETS.update(data)
    except Exception:
        pass


def _save_tickets_to_disk() -> None:
    try:
        with open(_LOCAL_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(_TICKETS, f)
    except Exception:
        pass


def _gchat_api_call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calls Google Chat REST API v1 using the bridged CXF OAuth2 token."""
    token = (_BRIDGE_STATE.get("cxf_token") or "").strip()
    if not token:
        raise RuntimeError("No active Google Chat bridge token yet.")
    url = f"https://chat.googleapis.com/v1/{path.lstrip('/')}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_outbound_to_gchat(ticket: Dict[str, Any], msg_item: Dict[str, Any]) -> bool:
    """Posts a participant's support message directly to the Google Chat Space thread."""
    space = ticket.get("space_id") or DEFAULT_GCHAT_SPACE
    user_name = ticket.get("user_name") or "Portal Visitor"
    user_email = ticket.get("user_email") or "participant@rocket.com"
    track = ticket.get("track") or "General / Portal"
    ticket_id = ticket.get("ticket_id") or "RKT-000"
    text_body = msg_item.get("text") or ""
    ai_context = msg_item.get("ai_context") or ""

    if not ticket.get("thread_name"):
        # First message in this ticket -> create a clear executive banner in Google Chat
        chat_text = (
            f"🚀 *[Rocket Portal Live Support · #{ticket_id}]*\n"
            f"*From:* {user_name} (`{user_email}`) · *Track:* {track}\n"
            f"*Question / Message:* {text_body}"
        )
        if ai_context:
            chat_text += f"\n*Prior AI Context:* _{ai_context[:260]}_"
        chat_text += (
            "\n\n💬 _Reply directly in this thread (starting with your answer) and it will stream live back to the user's Portal chat window!_"
        )
    else:
        chat_text = (
            f"💬 *[{user_name} · #{ticket_id} Follow-up]:*\n"
            f"{text_body}"
        )

    payload: Dict[str, Any] = {"text": chat_text}
    if ticket.get("thread_name"):
        payload["thread"] = {"name": ticket["thread_name"]}
        path = f"{space}/messages?messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
    else:
        path = f"{space}/messages"

    try:
        res = _gchat_api_call("POST", path, payload)
        msg_id = res.get("name", "")
        thread_name = res.get("thread", {}).get("name", "")
        if thread_name and not ticket.get("thread_name"):
            ticket["thread_name"] = thread_name
        if msg_id:
            seen = ticket.setdefault("seen_gchat_msg_ids", [])
            if msg_id not in seen:
                seen.append(msg_id)
        msg_item["delivered_to_gchat"] = True
        msg_item["gchat_message_id"] = msg_id
        return True
    except Exception:
        msg_item["delivered_to_gchat"] = False
        return False


def poll_gchat_thread_replies(ticket: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Checks Google Chat Space for any new replies in this ticket's thread from human Googlers."""
    space = ticket.get("space_id") or DEFAULT_GCHAT_SPACE
    thread_name = ticket.get("thread_name") or ""
    if not thread_name or not _BRIDGE_STATE.get("cxf_token"):
        return []

    new_replies: List[Dict[str, Any]] = []
    try:
        res = _gchat_api_call("GET", f"{space}/messages?pageSize=30&orderBy=createTime%20desc")
        messages = res.get("messages", [])
        seen = ticket.setdefault("seen_gchat_msg_ids", [])

        # Iterate oldest-to-newest among matching thread messages
        for m in reversed(messages):
            m_id = m.get("name", "")
            m_thread = m.get("thread", {}).get("name", "")
            if not m_id or m_thread != thread_name or m_id in seen:
                continue
            txt = (m.get("text") or "").strip()
            # Ignore our own outbound portal bridge banners
            if txt.startswith("🚀 *[Rocket Portal Live Support") or txt.startswith("💬 *["):
                seen.append(m_id)
                continue

            sender_info = m.get("sender", {})
            sender_name = sender_info.get("displayName") or "Google Cloud Team"
            sender_email = sender_info.get("email") or "googler@google.com"
            seen.append(m_id)

            reply_obj = {
                "id": m_id,
                "role": "human_agent",
                "sender_name": f"{sender_name} (Google Cloud)",
                "sender_email": sender_email,
                "text": txt,
                "timestamp": m.get("createTime") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            ticket.setdefault("messages", []).append(reply_obj)
            new_replies.append(reply_obj)

        if new_replies:
            _save_tickets_to_disk()
    except Exception:
        pass
    return new_replies


def answer_support_question_with_ai(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Answers a portal user's question using Vertex AI `gemini-3.8-flash` and flags when human escalation helps."""
    t0 = time.time()
    q_clean = (question or "").strip()
    if not q_clean:
        return {"ok": False, "error": "Empty question"}

    lower_q = q_clean.lower()
    human_keywords = (
        "human", "person", "googler", "talk to someone", "contact", "collaborate",
        "sundar", "angela", "jesus", "joris", "luis", "ricky", "office hours",
        "license", "pam grant", "access issue", "slack", "google chat", "help me build",
    )
    suggest_human = any(k in lower_q for k in human_keywords)

    sys_instruction = (
        "You are the Rocket × Google Cloud Portal Support Concierge (`gemini-3.8-flash`).\n"
        "You help Rocket Companies (Rocket Mortgage, Redfin, Mr. Cooper) engineers, product managers, "
        "and executives navigate the Unified Portal (`https://rocket-hackathon-portal-254356041555.us-central1.run.app`).\n\n"
        "KEY FACTS YOU KNOW:\n"
        "1. **4 Portal Tabs**:\n"
        "   - Tab 1 (`1. Live Studios`): 5 Flagship Production Studios (#1 BigQuery ML TimesFM 2.0 Forecast, #2 Veo 3.1 Reels Studio, #3 Ask Redfin 2.0 Grounded Chat with Google Maps+YouTube+Search, #4 Gemini 3.8 Live 24fps Video Avatar, #5 Redfin × Rocket Hybrid Vector Search & 108 Homes) + Ricky Merrefield's GECX Launchpad (`ces.cloud.google.com`) + Monday Super-Wow Lab.\n"
        "   - Tab 2 (`2. Build & GitHub (<3m)`): Public GitHub repository (`https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/rocket`), 33 standalone microservice repos (`rocket-ai-hackathon-argon-suite`), Antigravity IDE/CLI, and GCP project `dev-233554-hllwn26-hack-f1f8`.\n"
        "   - Tab 3 (`3. AI & Agent Platform Glossary` & `/glossary`): 20 core Agent Platform concepts (`Agent = Model + Harness`, `ADK`, `Vertex AI Agent Engine`, `MCP`, `A2A`, `Tri-Modal Grounding`, `gVisor Sandbox`, `Model Armor`, `LLM-as-a-Judge`) where clicking `See Live in Studio` opens a real-time **Mini-IDE Sandbox** to edit code and run on Vertex AI.\n"
        "   - Tab 4 (`4. Reference Library (33)`): 33 interactive domain blueprints (`Square 1.1` to `M.5`).\n"
        "2. **Talk to a Human (Detroit Dream Team Google Chat)**:\n"
        "   - If the user wants to collaborate with the Google Cloud team (Jesus Chavez, Sundar Chellappa, Angela Kavanaugh, Joris Wynendaele, Luis Lopez, Ricky Merrefield), ask a custom architecture question, or request licenses/access, tell them they can click **'Talk to a Human (Google Chat Live)'** right inside this widget to message our internal `Detroit Dream Team: Halloween Hackathon` Google Chat space in real time!\n\n"
        "Keep answers concise (2–4 sentences or short bullet points), warm, and actionable."
    )

    answer_text = ""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project="vtxdemos", location="global")
        conv_text = ""
        if history:
            for turn in history[-6:]:
                r = turn.get("role", "user")
                t = turn.get("text", "")
                conv_text += f"{r.upper()}: {t}\n"
        prompt = f"{conv_text}USER QUESTION: {q_clean}"
        resp = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.25,
                max_output_tokens=2048,
            ),
        )
        answer_text = (resp.text or "").strip()
    except Exception as exc:
        answer_text = (
            "I can help you explore all 5 Flagship Studios, the 20-card Agent Platform Glossary with the Live Sandbox Mini-IDE, "
            "or the 33 standalone GitHub microservice repos (`dev-233554-hllwn26-hack-f1f8`). "
            f"If you'd like direct help from our Google Cloud engineers, click **Talk to a Human (Google Chat)** below! ({exc})"
        )
        suggest_human = True

    latency_ms = int((time.time() - t0) * 1000)
    return {
        "ok": True,
        "answer": answer_text,
        "model": "gemini-3.8-flash",
        "latency_ms": latency_ms,
        "suggest_human": suggest_human,
        "space_name": _BRIDGE_STATE.get("space_name", DEFAULT_GCHAT_SPACE_NAME),
    }


def create_or_append_human_ticket(
    user_name: str,
    user_email: str,
    track: str,
    message_text: str,
    ticket_id: str = "",
    ai_context: str = "",
) -> Dict[str, Any]:
    """Creates or appends a message to a live human support ticket and dispatches to Google Chat."""
    _load_tickets_from_disk()
    tid = (ticket_id or "").strip()
    if not tid or tid not in _TICKETS:
        short_hex = uuid.uuid4().hex[:5].upper()
        tid = f"RKT-{short_hex}"
        _TICKETS[tid] = {
            "ticket_id": tid,
            "user_name": (user_name or "Rocket Builder").strip(),
            "user_email": (user_email or "builder@rocket.com").strip(),
            "track": (track or "Hackathon Collaboration & Architecture").strip(),
            "created_at": time.time(),
            "space_id": _BRIDGE_STATE.get("space_id") or DEFAULT_GCHAT_SPACE,
            "thread_name": "",
            "seen_gchat_msg_ids": [],
            "messages": [],
        }

    ticket = _TICKETS[tid]
    if user_name:
        ticket["user_name"] = user_name.strip()
    if user_email:
        ticket["user_email"] = user_email.strip()
    if track:
        ticket["track"] = track.strip()

    msg_item: Dict[str, Any] = {
        "id": f"local-{uuid.uuid4().hex[:8]}",
        "role": "user",
        "sender_name": ticket["user_name"],
        "sender_email": ticket["user_email"],
        "text": message_text.strip(),
        "ai_context": (ai_context or "").strip(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "delivered_to_gchat": False,
    }
    ticket["messages"].append(msg_item)

    # Attempt immediate direct delivery to Google Chat Space if token is available
    delivered = post_outbound_to_gchat(ticket, msg_item)
    _save_tickets_to_disk()

    return {
        "ok": True,
        "ticket_id": tid,
        "delivered_immediately": delivered,
        "space_id": ticket["space_id"],
        "space_name": _BRIDGE_STATE.get("space_name", DEFAULT_GCHAT_SPACE_NAME),
        "thread_name": ticket.get("thread_name", ""),
        "messages": ticket["messages"],
    }


def get_ticket_status(ticket_id: str) -> Dict[str, Any]:
    """Returns all messages for `ticket_id`, polling Google Chat for any new Googler replies."""
    _load_tickets_from_disk()
    tid = (ticket_id or "").strip()
    ticket = _TICKETS.get(tid)
    if not ticket:
        return {"ok": False, "error": "Ticket not found", "ticket_id": tid}

    # Flush any undelivered outbound messages if token is now present
    if _BRIDGE_STATE.get("cxf_token"):
        for m in ticket.get("messages", []):
            if m.get("role") == "user" and not m.get("delivered_to_gchat"):
                post_outbound_to_gchat(ticket, m)

    new_replies = poll_gchat_thread_replies(ticket)
    return {
        "ok": True,
        "ticket_id": tid,
        "space_name": _BRIDGE_STATE.get("space_name", DEFAULT_GCHAT_SPACE_NAME),
        "thread_name": ticket.get("thread_name", ""),
        "bridge_online": bool(_BRIDGE_STATE.get("cxf_token")),
        "new_replies_count": len(new_replies),
        "messages": ticket.get("messages", []),
    }


def handle_bridge_sync(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Called by Cloudtop daemon (`scripts/gchat_support_bridge.py`) to sync fresh CXF OAuth token & flush queues."""
    _load_tickets_from_disk()
    secret = (payload.get("secret") or "").strip()
    if secret != BRIDGE_SECRET:
        return {"ok": False, "error": "Invalid bridge secret"}

    token = (payload.get("cxf_token") or "").strip()
    if token:
        _BRIDGE_STATE["cxf_token"] = token
        _BRIDGE_STATE["token_updated_at"] = time.time()
    if payload.get("space_id"):
        _BRIDGE_STATE["space_id"] = payload["space_id"]
    if payload.get("space_name"):
        _BRIDGE_STATE["space_name"] = payload["space_name"]

    flushed_outbound = 0
    synced_replies = 0
    if _BRIDGE_STATE.get("cxf_token"):
        for ticket in _TICKETS.values():
            for m in ticket.get("messages", []):
                if m.get("role") == "user" and not m.get("delivered_to_gchat"):
                    if post_outbound_to_gchat(ticket, m):
                        flushed_outbound += 1
            replies = poll_gchat_thread_replies(ticket)
            synced_replies += len(replies)

    _save_tickets_to_disk()
    return {
        "ok": True,
        "token_active": bool(_BRIDGE_STATE.get("cxf_token")),
        "tickets_count": len(_TICKETS),
        "flushed_outbound": flushed_outbound,
        "synced_replies": synced_replies,
        "space_id": _BRIDGE_STATE["space_id"],
        "space_name": _BRIDGE_STATE["space_name"],
    }
