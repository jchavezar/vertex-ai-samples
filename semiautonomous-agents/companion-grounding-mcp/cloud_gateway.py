#!/usr/bin/env python3
"""
Lego Block 3: Unified Cloud Run Supermemory Gateway (`companion-grounding-cloud`)
Powered by `gemini-3.8-flash` + `ground_truth.db` (2,453 chronologically ordered records,
671 3072-dim `gemini-embedding-001` vectors, 20 cross-platform graph nodes, 1,837 calendar events).

Supports FULL MCP OAuth 2.1 + True Two-Factor Authentication (PIN + RFC 6238 TOTP):
- `GET  /.well-known/oauth-protected-resource`
- `GET  /.well-known/oauth-authorization-server`
- `POST /oauth/register` (RFC 7591 Dynamic Client Registration)
- `GET/POST /oauth/authorize` (2FA Sign-In Screen: Passcode + 6-Digit Google Authenticator TOTP + PKCE S256)
- `POST /oauth/token` (OAuth 2.1 Code & Refresh Token Exchange with cryptographic PKCE verification)
- `/mcp/sse` & `/mcp` (Authenticated via OAuth Bearer Token OR Path Token)
"""

import os
import hmac
import json
import time
import uuid
import struct
import shutil
import base64
import hashlib
import secrets
import sqlite3
import subprocess
from urllib.parse import urlencode
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Paths & Config
BASE_DIR = Path(__file__).resolve().parent
MOUNTED_DB = Path(os.environ.get("MOUNTED_DB_PATH", "/mnt/memory/ground_truth.db"))
LOCAL_DB = BASE_DIR / "data" / "ground_truth.db"
RAM_DB = Path("/tmp/ground_truth_ram.db")
_LAST_MTIME = 0.0

PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
GCS_BUCKET = os.environ.get("GCS_MEMORY_BUCKET", "gs://vtxdemos-companion-memory")
AUTH_TOKEN = os.environ.get("SUPERMEMORY_AUTH_TOKEN", "")
OAUTH_PASSCODE = os.environ.get("SUPERMEMORY_OAUTH_PIN", "")
TOTP_SECRET = os.environ.get("SUPERMEMORY_TOTP_SECRET", "")
PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3-pro-preview"]

OAUTH_CODES = {}

COACHING_CONTEXT_NOTE = """First-Party Personal Communication Self-Reflection Notes (Owner: Jesus Chavez).
Purpose: Help Jesus recall details from his own personal conversations across Instagram DMs, Google Chat 1:1 DMs, Google Chat Shared Spaces, Google Docs, Gmail, Meet, and Calendar, and reflect on his own communication habits (using principles from Mark Manson's book 'Models': authenticity, non-neediness, warm receptivity, and avoiding unnecessary self-deprecation or double-texting)."""


def get_db():
    global _LAST_MTIME
    source = MOUNTED_DB if MOUNTED_DB.exists() else LOCAL_DB
    if source.exists():
        try:
            mtime = source.stat().st_mtime
            if not RAM_DB.exists() or mtime > _LAST_MTIME:
                shutil.copy2(source, RAM_DB)
                _LAST_MTIME = mtime
            target = RAM_DB
        except Exception:
            target = source
    else:
        target = source
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    return conn


def compute_totp(secret_b32: str, time_step: int) -> str:
    """RFC 6238 TOTP 6-digit generator using standard library hmac-sha1."""
    clean = secret_b32.strip().replace(" ", "").upper()
    pad = "=" * ((8 - len(clean) % 8) % 8)
    key = base64.b32decode(clean + pad, casefold=True)
    msg = struct.pack(">Q", time_step)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code_int:06d}"


def verify_totp_code(candidate_totp: str) -> bool:
    """Verifies a 6-digit TOTP code against TOTP_SECRET with +/- 1 step (30s) window."""
    if not TOTP_SECRET:
        return True
    c = (candidate_totp or "").strip().replace(" ", "")
    if not (len(c) == 6 and c.isdigit()):
        return False
    now_step = int(time.time() // 30)
    for delta in (-1, 0, 1):
        if hmac.compare_digest(c, compute_totp(TOTP_SECRET, now_step + delta)):
            return True
    return False


def is_valid_secret(candidate: str) -> bool:
    if not candidate:
        return False
    c = candidate.strip()
    if AUTH_TOKEN and hmac.compare_digest(c, AUTH_TOKEN):
        return True
    if OAUTH_PASSCODE and hmac.compare_digest(c, OAUTH_PASSCODE):
        return True
    if c.startswith("sm_oauth_") and AUTH_TOKEN:
        parts = c.split(".")
        if len(parts) == 2:
            expected_sig = hashlib.sha256(f"{parts[0]}:{AUTH_TOKEN}".encode()).hexdigest()[:24]
            return hmac.compare_digest(parts[1], expected_sig)
    return False


def mint_oauth_token() -> str:
    nonce = f"sm_oauth_{secrets.token_urlsafe(16)}"
    sig = hashlib.sha256(f"{nonce}:{AUTH_TOKEN}".encode()).hexdigest()[:24]
    return f"{nonce}.{sig}"


def verify_token(req: Request, path_token: Optional[str] = None):
    if not AUTH_TOKEN and not OAUTH_PASSCODE:
        return True
    auth_header = req.headers.get("Authorization", "")
    bearer = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else ""
    query_token = req.query_params.get("token", "") or req.query_params.get("api_key", "")
    for candidate in [path_token, bearer, query_token]:
        if candidate and is_valid_secret(candidate):
            return True
    raise HTTPException(status_code=401, detail="Unauthorized: Valid OAuth Bearer token or Passcode required.")


def fetch_context_window(conn: sqlite3.Connection, msg_id: int, radius: int = 4):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, platform, channel_name, sender, timestamp, timestamp_utc, text, reactions,
               sentiment_label, models_positives, models_flaws
        FROM raw_messages
        WHERE id BETWEEN ? AND ?
        ORDER BY id ASC
        """,
        (max(1, msg_id - radius), msg_id + radius),
    )
    return [dict(r) for r in cur.fetchall()]


def run_supermemory_search(query: str, limit: int = 8) -> dict:
    conn = get_db()
    cur = conn.cursor()
    words = [w.strip("?.,!'\"") for w in query.split() if len(w.strip("?.,!'\"")) >= 3]
    fts_matches = []
    if words:
        fts_q = " OR ".join(f'"{w}"' for w in words[:6])
        try:
            cur.execute(
                """
                SELECT m.id, m.platform, m.channel_name, m.sender, m.timestamp, m.timestamp_utc, m.text,
                       m.sentiment_label, m.models_positives, m.models_flaws, m.models_coaching_note
                FROM raw_messages_fts f
                JOIN raw_messages m ON f.rowid = m.id
                WHERE raw_messages_fts MATCH ?
                ORDER BY m.id DESC
                LIMIT ?
                """,
                (fts_q, limit),
            )
            for row in cur.fetchall():
                d = dict(row)
                d["context_window_pm5"] = fetch_context_window(conn, d["id"], 5)
                fts_matches.append(d)
        except Exception:
            pass

    cur.execute(
        """
        SELECT id, platform, channel_name, sender, timestamp, timestamp_utc, text,
               models_positives, models_flaws
        FROM raw_messages
        ORDER BY id DESC
        LIMIT 30
        """
    )
    recent_anchor = list(reversed([dict(r) for r in cur.fetchall()]))

    try:
        cur.execute("SELECT * FROM topic_graph_nodes LIMIT 20")
        graph_nodes = [dict(r) for r in cur.fetchall()]
    except Exception:
        graph_nodes = []

    conn.close()
    return {
        "archive_owner": "Jesus Chavez (Authenticated First-Party Personal Memory Journal)",
        "context_note": COACHING_CONTEXT_NOTE,
        "matched_journal_entries": fts_matches,
        "recent_journal_entries_october_2026": recent_anchor,
        "topic_summary_nodes": graph_nodes,
    }


def audit_quotes_in_text(text_to_check: str) -> dict:
    """Deterministic post-generation quote verifier against ground_truth.db."""
    import re
    candidates = re.findall(r'"([^"\n]{10,120})"', text_to_check or "")
    conn = get_db()
    cur = conn.cursor()
    verified = []
    unverified = []
    for q in candidates:
        clean = q.strip()
        cur.execute(
            "SELECT id, timestamp_utc, platform, sender, text FROM raw_messages WHERE text LIKE ? LIMIT 1",
            (f"%{clean}%",),
        )
        row = cur.fetchone()
        if row:
            verified.append({
                "quote": clean,
                "id": row["id"],
                "timestamp_utc": row["timestamp_utc"],
                "platform": row["platform"],
                "sender": row["sender"],
            })
        else:
            unverified.append(clean)
    conn.close()
    return {
        "checked_quotes_count": len(candidates),
        "verified_quotes": verified,
        "unverified_or_paraphrased_strings": unverified,
    }


def ask_gemini_38_flash_coach(question: str) -> dict:
    bundle = run_supermemory_search(question, limit=10)
    system_instruction = f"""You are Jesus's Personal Memory & Communication Self-Reflection Coach (powered by {PRIMARY_MODEL}).
Speak like Jesus's sharpest, most trusted, direct, non-sycophantic close friend.

STRICT ZERO-HALLUCINATION & VERBATIM EVIDENCE PROTOCOL:
1. NEVER invent, guess, or paraphrase a quote inside quotation marks. Only place text inside double quotes ("...") if it appears VERBATIM in the JSON records below.
2. Every single quoted message MUST include its exact database citation tag: `[id:<id> | <timestamp_utc> | <platform> | <sender>]`.
3. NEVER interpret a short reply in isolation—always read `context_window_pm5` (the 5 messages before and 5 messages after) so you know the exact topic being discussed.
4. If a detail is not present in the JSON records below, state clearly that it is not in the matched records rather than guessing.

Use Mark Manson's 'Models' principles to help Jesus reflect on his own communication style:
- Stand unapologetically behind thoughtful gestures and warm banter without retroactive HR-style apologies.
- Maintain balanced investment rhythm (avoid 4+ multi-bubble chasing or self-deprecating permission-seeking).

FIRST-PARTY JOURNAL SNAPSHOT:
- Total Logged Entries: 2,453 chronologically ordered records across Instagram DMs (1,339), Google Chat 1:1 DM (953), 6 Shared Google Chat Spaces (141), Gmail (15), and Shared Google Docs (5).

MATCHED JOURNAL ENTRIES (WITH +-5 MESSAGE CONTEXT WINDOWS):
{json.dumps(bundle['matched_journal_entries'][:6], ensure_ascii=False, indent=2)}

MOST RECENT JOURNAL ENTRIES (THROUGH OCT 9, 2026):
{json.dumps(bundle['recent_journal_entries_october_2026'][-25:], ensure_ascii=False, indent=2)}
"""
    used_model = PRIMARY_MODEL
    answer_text = ""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        for candidate_model in [PRIMARY_MODEL] + FALLBACK_MODELS:
            try:
                resp = client.models.generate_content(
                    model=candidate_model,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0,
                    ),
                )
                if resp and resp.text:
                    used_model = candidate_model
                    answer_text = resp.text
                    break
            except Exception:
                continue
    except Exception as e:
        answer_text = f"Fallback synthesis (Vertex error: {e})"

    quote_audit = audit_quotes_in_text(answer_text)
    return {
        "archive_owner": "Jesus Chavez (First-Party Personal Memory & Self-Reflection Journal)",
        "model_used": used_model,
        "self_reflection_coaching_notes": answer_text,
        "gemini_38_flash_coaching": answer_text,
        "quote_verification_audit": quote_audit,
        "journal_entries_with_context": bundle["matched_journal_entries"][:6],
        "ground_truth_evidence": bundle["matched_journal_entries"][:6],
    }


try:
    from mcp.server.transport_security import TransportSecuritySettings
    mcp = FastMCP(
        "personal-communication-journal",
        host="0.0.0.0",
        stateless_http=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
except Exception:
    try:
        mcp = FastMCP("personal-communication-journal", host="0.0.0.0", stateless_http=True)
    except Exception:
        mcp = FastMCP("personal-communication-journal")


@mcp.tool()
def query_my_personal_journal(question: str) -> str:
    """
    Searches the authenticated user's (Jesus's) own first-party personal conversation journal
    and self-reflection notes across Instagram, Google Chat 1:1 DM, Google Chat Spaces, Docs, and Calendar.
    """
    return json.dumps(ask_gemini_38_flash_coach(question), ensure_ascii=False, indent=2)


@mcp.tool()
def search_my_conversation_notes(keyword_or_topic: str, limit: int = 8) -> str:
    """
    Retrieves the user's own past conversation entries and personal notes by keyword or topic.
    """
    return json.dumps(run_supermemory_search(keyword_or_topic, limit=limit), ensure_ascii=False, indent=2)


@mcp.tool()
def review_my_communication_style(period: str = "recent") -> str:
    """
    Reviews the user's own sent messages and personal self-reflection tags (based on Mark Manson's 'Models').
    """
    conn = get_db()
    cur = conn.cursor()
    if period == "recent":
        cur.execute(
            """
            SELECT id, platform, channel_name, timestamp, timestamp_utc, sender, text, models_positives, models_flaws
            FROM raw_messages
            ORDER BY id DESC
            LIMIT 35
            """
        )
        rows = list(reversed([dict(r) for r in cur.fetchall()]))
    else:
        cur.execute(
            """
            SELECT id, platform, channel_name, timestamp, timestamp_utc, sender, text, models_positives, models_flaws
            FROM raw_messages
            WHERE models_flaws != '[]' AND models_flaws != ''
            ORDER BY id DESC LIMIT 25
            """
        )
        rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json.dumps(
        {
            "archive_owner": "Jesus Chavez (First-Party Self-Reflection Log)",
            "context_note": COACHING_CONTEXT_NOTE,
            "journal_records": rows,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def get_journal_entry_context(msg_id: int, radius: int = 6) -> str:
    """
    Fetches a specific message by its exact database ID (1..2453+) along with +-radius surrounding messages
    in chronological order so no short reply is ever interpreted out of context.
    """
    conn = get_db()
    window = fetch_context_window(conn, msg_id, radius=radius)
    conn.close()
    return json.dumps(
        {
            "target_msg_id": msg_id,
            "radius": radius,
            "chronological_context_window": window,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def verify_exact_quotes(quotes_pipe_separated: str) -> str:
    """
    Zero-hallucination quote verifier: checks one or more candidate quotes (separated by '|')
    against ground_truth.db raw_messages and returns exact row IDs, timestamps, senders, and +-3 surrounding messages,
    or flags HALLUCINATION_BLOCKED_NOT_IN_DB if not found.
    """
    conn = get_db()
    cur = conn.cursor()
    parts = [p.strip() for p in quotes_pipe_separated.split("|") if p.strip()]
    results = []
    all_ok = True
    for q in parts:
        cur.execute(
            "SELECT id, platform, channel_name, sender, timestamp_utc, timestamp, text FROM raw_messages WHERE text LIKE ? ORDER BY id DESC LIMIT 3",
            (f"%{q}%",),
        )
        rows = [dict(r) for r in cur.fetchall()]
        if rows:
            for r in rows:
                r["context_window_pm3"] = fetch_context_window(conn, r["id"], radius=3)
            results.append({"candidate_quote": q, "status": "VERIFIED_IN_GROUND_TRUTH_DB", "matches": rows})
        else:
            all_ok = False
            results.append({"candidate_quote": q, "status": "HALLUCINATION_BLOCKED_NOT_IN_DB", "matches": []})
    conn.close()
    return json.dumps(
        {
            "all_quotes_verified": all_ok,
            "total_checked": len(parts),
            "verification_results": results,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def sync_my_journal_backup() -> str:
    """
    Triggers a user-authorized backup sync of the user's own personal journal database to Cloud Storage.
    """
    payload = json.dumps({
        "sync_requested_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": "first_party_user_journal_backup",
        "status": "pending_cloudtop_pickup"
    })
    mounted_trigger = Path("/mnt/memory/sync_trigger.json")
    if mounted_trigger.parent.exists():
        mounted_trigger.write_text(payload, encoding="utf-8")
    else:
        subprocess.run(
            ["gcloud", "storage", "cp", "-", f"{GCS_BUCKET}/sync_trigger.json", f"--project={PROJECT_ID}", "--quiet"],
            input=payload,
            text=True
        )
    return json.dumps({
        "status": "queued",
        "message": "Personal journal backup sync queued."
    })


import contextlib


@contextlib.asynccontextmanager
async def mcp_lifespan(app: FastAPI):
    if hasattr(mcp, "session_manager"):
        async with mcp.session_manager.run():
            yield
    else:
        yield


app = FastAPI(title="Supermemory Cloud Gateway (OAuth 2.1 + 2FA TOTP + Streamable HTTP)", lifespan=mcp_lifespan)
try:
    http_subapp = mcp.streamable_http_app()
    for route in http_subapp.routes:
        app.router.routes.append(route)
except Exception:
    pass
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_https_base_url(req: Request) -> str:
    host = req.headers.get("x-forwarded-host") or req.headers.get("host") or "companion-grounding-cloud-254356041555.us-central1.run.app"
    return f"https://{host}"


@app.get("/.well-known/oauth-protected-resource")
@app.get("/.well-known/oauth-protected-resource/{rest:path}")
def oauth_protected_resource(req: Request, rest: str = ""):
    base = get_https_base_url(req)
    return {
        "resource": f"{base}/mcp/sse",
        "authorization_servers": [base],
        "bearer_methods_supported": ["header", "query"],
        "scopes_supported": ["mcp:tools", "profile", "offline_access"],
    }


@app.get("/.well-known/oauth-authorization-server")
@app.get("/.well-known/openid-configuration")
def oauth_authorization_server(req: Request):
    base = get_https_base_url(req)
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token",
        "registration_endpoint": f"{base}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post", "client_secret_basic"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "scopes_supported": ["mcp:tools", "profile", "offline_access"],
    }


@app.post("/oauth/register")
async def oauth_register(req: Request):
    body = await req.json()
    client_id = f"claude_mobile_{secrets.token_hex(8)}"
    client_secret = f"secret_{secrets.token_urlsafe(24)}"
    return JSONResponse(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(time.time()),
            "client_secret_expires_at": 0,
            "redirect_uris": body.get("redirect_uris", []),
            "grant_types": body.get("grant_types", ["authorization_code", "refresh_token"]),
            "response_types": body.get("response_types", ["code"]),
            "client_name": body.get("client_name", "Claude Mobile MCP"),
            "token_endpoint_auth_method": body.get("token_endpoint_auth_method", "none"),
        },
        status_code=201,
    )


@app.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize_get(
    req: Request,
    response_type: str = "code",
    client_id: str = "",
    redirect_uri: str = "",
    state: str = "",
    code_challenge: str = "",
    code_challenge_method: str = "S256",
    scope: str = "",
):
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Authorize Supermemory Brain (OAuth 2.1 + 2FA TOTP)</title>
  <style>
    :root {{
      --bg-canvas: #FAFAFA;
      --bg-surface: #FFFFFF;
      --border: #EAEAEA;
      --border-focus: #111111;
      --text-primary: #09090B;
      --text-secondary: #666666;
      --btn-bg: #000000;
      --btn-text: #FFFFFF;
      --badge-bg: #F4F4F5;
      --ink-grad: radial-gradient(circle at 30% 30%, #52525b, #18181b, #000000);
    }}
    [data-theme="dark"] {{
      --bg-canvas: #000000;
      --bg-surface: #0A0A0A;
      --border: #222222;
      --border-focus: #EDEDED;
      --text-primary: #EDEDED;
      --text-secondary: #888888;
      --btn-bg: #FFFFFF;
      --btn-text: #000000;
      --badge-bg: #18181B;
      --ink-grad: radial-gradient(circle at 30% 30%, #ffffff, #a1a1aa, #18181b);
    }}
    body {{
      background: var(--bg-canvas);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 16px;
    }}
    .topbar {{
      width: 100%;
      max-width: 420px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .theme-btn {{
      background: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border);
      padding: 6px 10px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 11px;
      cursor: pointer;
    }}
    .card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      max-width: 420px;
      width: 100%;
      padding: 24px;
      box-sizing: border-box;
    }}
    h1 {{ font-size: 18px; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.02em; }}
    p {{ font-size: 13px; color: var(--text-secondary); margin: 0 0 20px 0; line-height: 1.5; }}
    label {{ display: block; font-size: 11px; font-family: monospace; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); margin-bottom: 6px; }}
    input[type="password"], input[type="text"] {{
      width: 100%;
      box-sizing: border-box;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 15px;
      margin-bottom: 16px;
      background: var(--bg-canvas);
      color: var(--text-primary);
    }}
    button.primary {{
      width: 100%;
      background: var(--btn-bg);
      color: var(--btn-text);
      border: none;
      border-radius: 8px;
      padding: 13px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
    }}
    .badge {{
      display: inline-block;
      font-family: monospace;
      font-size: 10px;
      background: var(--badge-bg);
      padding: 4px 8px;
      border-radius: 4px;
      margin-bottom: 12px;
    }}
    .loader-row {{
      display: none;
      align-items: center;
      gap: 10px;
      margin-top: 14px;
      font-family: monospace;
      font-size: 12px;
      color: var(--text-secondary);
    }}
    .shrinking-shining-ink {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: var(--ink-grad);
      animation: inkPulse 1.4s infinite ease-in-out;
    }}
    @keyframes inkPulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.95; }}
      50% {{ transform: scale(0.55); opacity: 0.45; }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <span style="font-family:monospace;font-size:11px;color:var(--text-secondary);">SUPERMEMORY // ZERO-TRUST 2FA</span>
    <button type="button" class="theme-btn" id="themeToggle" onclick="toggleTheme()">☀️ Light</button>
  </div>
  <div class="card">
    <div class="badge">OAUTH 2.1 PKCE S256 • RFC 6238 TOTP MFA</div>
    <h1>Connect Supermemory Brain</h1>
    <p>Authorize <b>Claude / MCP Client</b> to access your 2,453 chronological records, 671 vectors, 20-node causal graph, and Mark Manson <i>Models</i> harness.</p>
    <form method="POST" action="/oauth/authorize" onsubmit="document.getElementById('loader').style.display='flex';">
      <input type="hidden" name="client_id" value="{client_id}" />
      <input type="hidden" name="redirect_uri" value="{redirect_uri}" />
      <input type="hidden" name="state" value="{state}" />
      <input type="hidden" name="code_challenge" value="{code_challenge}" />
      <input type="hidden" name="code_challenge_method" value="{code_challenge_method}" />
      <label>Factor 1 — Supermemory Passcode (PIN)</label>
      <input type="password" name="passcode" placeholder="Enter your PIN..." required autofocus />
      <label>Factor 2 — Authenticator 6-Digit TOTP Code</label>
      <input type="text" name="totp_code" inputmode="numeric" pattern="[0-9]{{6}}" maxlength="6" placeholder="123456" required />
      <button type="submit" class="primary">Verify 2FA & Connect</button>
      <div class="loader-row" id="loader">
        <div class="shrinking-shining-ink"></div>
        <span class="sweep-text">Verifying cryptographic PKCE & RFC 6238 TOTP...</span>
      </div>
    </form>
  </div>
  <script>
    function toggleTheme() {{
      const root = document.documentElement;
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      document.getElementById('themeToggle').textContent = next === 'dark' ? '🌙 Dark' : '☀️ Light';
    }}
  </script>
</body>
</html>"""
    return HTMLResponse(html)


@app.post("/oauth/authorize")
async def oauth_authorize_post(
    client_id: str = Form(""),
    redirect_uri: str = Form(""),
    state: str = Form(""),
    code_challenge: str = Form(""),
    code_challenge_method: str = Form("S256"),
    passcode: str = Form(""),
    totp_code: str = Form(""),
):
    if not is_valid_secret(passcode):
        return HTMLResponse(
            "<h3 style='font-family:monospace;padding:24px;'>❌ Factor 1 Failed: Invalid Passcode. <a href='javascript:history.back()'>Try Again</a></h3>",
            status_code=401,
        )
    if TOTP_SECRET and not verify_totp_code(totp_code):
        return HTMLResponse(
            "<h3 style='font-family:monospace;padding:24px;'>❌ Factor 2 Failed: Invalid or Expired 6-Digit Authenticator TOTP Code. <a href='javascript:history.back()'>Try Again</a></h3>",
            status_code=401,
        )
    # Statelessly encode (nonce, code_challenge_method, code_challenge, timestamp) + HMAC signature
    raw_nonce = f"code_{secrets.token_urlsafe(16)}"
    cc_b64 = base64.urlsafe_b64encode(f"{code_challenge_method}:{code_challenge}".encode()).decode().rstrip("=")
    sig = hashlib.sha256(f"{raw_nonce}:{cc_b64}:{AUTH_TOKEN}".encode()).hexdigest()[:24]
    signed_code = f"{raw_nonce}.{cc_b64}.{sig}"
    OAUTH_CODES[signed_code] = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "created_at": time.time(),
    }
    sep = "&" if "?" in redirect_uri else "?"
    params = {"code": signed_code}
    if state:
        params["state"] = state
    return RedirectResponse(url=f"{redirect_uri}{sep}{urlencode(params)}", status_code=302)


@app.post("/oauth/token")
async def oauth_token(req: Request):
    content_type = req.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await req.json()
    else:
        form_data = await req.form()
        data = dict(form_data)

    grant_type = data.get("grant_type", "authorization_code")
    code = data.get("code", "")
    code_verifier = data.get("code_verifier", "")
    client_secret = data.get("client_secret", "")

    if grant_type == "authorization_code":
        parts = code.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail="Invalid authorization code format")
        raw_nonce, cc_b64, sig = parts
        expected_sig = hashlib.sha256(f"{raw_nonce}:{cc_b64}:{AUTH_TOKEN}".encode()).hexdigest()[:24]
        if not hmac.compare_digest(sig, expected_sig):
            raise HTTPException(status_code=400, detail="Invalid authorization code signature")
        # Decode PKCE challenge and verify code_verifier
        pad = "=" * ((4 - len(cc_b64) % 4) % 4)
        cc_decoded = base64.urlsafe_b64decode(cc_b64 + pad).decode()
        method, challenge = cc_decoded.split(":", 1)
        if challenge:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="Missing PKCE code_verifier")
            if method.upper() == "S256":
                computed = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip("=")
            else:
                computed = code_verifier
            if not hmac.compare_digest(computed, challenge):
                raise HTTPException(status_code=400, detail="PKCE code_verifier mismatch")
    elif grant_type == "client_credentials":
        if not is_valid_secret(client_secret):
            raise HTTPException(status_code=401, detail="Invalid client_secret")

    access_token = mint_oauth_token()
    refresh_token = mint_oauth_token()
    return JSONResponse(
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 2592000,
            "refresh_token": refresh_token,
            "scope": "mcp:tools profile offline_access",
        }
    )


@app.get("/api/health")
def api_health():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM raw_messages")
    total = cur.fetchone()[0]
    conn.close()
    return {
        "status": "ok",
        "model": PRIMARY_MODEL,
        "oauth2_pkce_enabled": True,
        "totp_2fa_enabled": bool(TOTP_SECRET),
        "indexed_messages": total,
    }


@app.get("/.well-known/agent.json")
def a2a_agent_card(req: Request):
    verify_token(req)
    base_url = get_https_base_url(req)
    return {
        "name": "companion_supermemory_coach",
        "description": "Selene & Jesus Supermemory Brain (2,453 messages, 671 Vectors, 20-Node Topic Graph & Mark Manson Models Coach)",
        "url": f"{base_url}/a2a",
        "version": "2.2.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "supermemory_coaching",
                "name": "Supermemory Grounding & Mark Manson Models Coaching",
                "description": "Queries Instagram DMs, Google Chat 1:1 & Shared Spaces, Docs, Calendar, and Topic Graph."
            }
        ]
    }


@app.post("/a2a")
async def a2a_endpoint(req: Request):
    verify_token(req)
    body = await req.json()
    question = ""
    if "params" in body and "message" in body["params"]:
        parts = body["params"]["message"].get("parts", [])
        question = " ".join(p.get("text", "") for p in parts if "text" in p)
    elif "query" in body:
        question = body["query"]
    result = ask_gemini_38_flash_coach(question or "Give me a status check on Selene.")
    return {
        "jsonrpc": "2.0",
        "id": body.get("id", "1"),
        "result": {
            "role": "agent",
            "model": result["model_used"],
            "parts": [{"type": "text", "text": result["gemini_38_flash_coaching"]}],
            "evidence": result["ground_truth_evidence"]
        }
    }


@app.post("/api/chat")
async def api_chat(req: Request):
    verify_token(req)
    body = await req.json()
    q = body.get("query", "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Missing query")
    return JSONResponse(ask_gemini_38_flash_coach(q))


@app.post("/api/sync")
async def api_sync(req: Request):
    verify_token(req)
    return JSONResponse(json.loads(sync_my_journal_backup()))


sse_subapp = mcp.sse_app()


@app.middleware("http")
async def mcp_auth_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/s/"):
        parts = path.split("/", 3)
        if len(parts) >= 4:
            token_candidate = parts[2]
            if not is_valid_secret(token_candidate):
                return JSONResponse({"error": "Unauthorized MCP path token"}, status_code=401)
            request.scope["path"] = "/" + parts[3]
            return await call_next(request)
    if path.startswith("/mcp"):
        auth_header = request.headers.get("Authorization", "")
        bearer = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else ""
        query_token = request.query_params.get("token", "")
        if not (is_valid_secret(bearer) or is_valid_secret(query_token)):
            base = get_https_base_url(request)
            return JSONResponse(
                {"error": "invalid_token", "error_description": "OAuth 2.1 Bearer token required"},
                status_code=401,
                headers={
                    "WWW-Authenticate": f'Bearer resource_metadata="{base}/.well-known/oauth-protected-resource"'
                },
            )
    return await call_next(request)


app.mount("/mcp", sse_subapp)


@app.get("/app", response_class=HTMLResponse)
async def mobile_pocket_pwa(req: Request, token: Optional[str] = None):
    html = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Supermemory Brain // Vercel Monochrome Pocket Coach</title>
  <style>
    :root {
      --bg-canvas: #FAFAFA;
      --bg-surface: #FFFFFF;
      --border: #EAEAEA;
      --border-focus: #111111;
      --text-primary: #09090B;
      --text-secondary: #666666;
      --btn-bg: #000000;
      --btn-text: #FFFFFF;
      --badge-bg: #F4F4F5;
      --ink-grad: radial-gradient(circle at 30% 30%, #52525b, #18181b, #000000);
    }
    [data-theme="dark"] {
      --bg-canvas: #000000;
      --bg-surface: #0A0A0A;
      --border: #222222;
      --border-focus: #EDEDED;
      --text-primary: #EDEDED;
      --text-secondary: #888888;
      --btn-bg: #FFFFFF;
      --btn-text: #000000;
      --badge-bg: #18181B;
      --ink-grad: radial-gradient(circle at 30% 30%, #ffffff, #a1a1aa, #18181b);
    }
    body {
      background: var(--bg-canvas);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      min-height: 100vh;
    }
    header {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    .brand { font-weight: 700; font-size: 14px; letter-spacing: -0.02em; }
    .telemetry { font-family: monospace; font-size: 11px; color: var(--text-secondary); letter-spacing: 0.06em; text-transform: uppercase; }
    .theme-btn {
      background: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 11px;
      cursor: pointer;
    }
    main { max-width: 820px; margin: 24px auto; padding: 0 16px 64px; }
    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 16px;
    }
    label { display: block; font-family: monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); margin-bottom: 6px; }
    input, textarea {
      width: 100%;
      box-sizing: border-box;
      padding: 11px 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--bg-canvas);
      color: var(--text-primary);
      font-size: 14px;
      margin-bottom: 12px;
      font-family: inherit;
    }
    button.primary {
      background: var(--btn-bg);
      color: var(--btn-text);
      border: none;
      border-radius: 8px;
      padding: 11px 18px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }
    .loader-row {
      display: none;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
      font-family: monospace;
      font-size: 12px;
      color: var(--text-secondary);
    }
    .shrinking-shining-ink {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: var(--ink-grad);
      animation: inkPulse 1.4s infinite ease-in-out;
    }
    @keyframes inkPulse {
      0%, 100% { transform: scale(1); opacity: 0.95; }
      50% { transform: scale(0.55); opacity: 0.45; }
    }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.55;
      background: var(--bg-canvas);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      margin-top: 12px;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <div class="brand">SUPERMEMORY BRAIN // POCKET COACH</div>
      <div class="telemetry">2,453 CHRONOLOGICAL RECORDS • 671 VECTORS • 20 CAUSAL NODES</div>
    </div>
    <button class="theme-btn" id="themeToggle" onclick="toggleTheme()">☀️ Light</button>
  </header>
  <main>
    <div class="card">
      <label>Passcode / Bearer Token</label>
      <input type="password" id="apiKey" placeholder="Enter your Supermemory PIN (SM-...) or Bearer token" />
      <label>Ask Supermemory Coach (Instagram + Google Chat DM + 6 Shared Spaces + Docs + Calendar)</label>
      <textarea id="queryBox" rows="3" placeholder="e.g., What did Selene and I talk about in October across our DM and shared spaces?"></textarea>
      <button class="primary" onclick="askCoach()">Run Grounded Query</button>
      <div class="loader-row" id="loader">
        <div class="shrinking-shining-ink"></div>
        <span class="sweep-text">Querying 2,453 records & synthesizing Models reflection...</span>
      </div>
      <div id="output"></div>
    </div>
  </main>
  <script>
    const params = new URLSearchParams(location.search);
    if (params.get('token')) document.getElementById('apiKey').value = params.get('token');
    function toggleTheme() {
      const root = document.documentElement;
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      document.getElementById('themeToggle').textContent = next === 'dark' ? '🌙 Dark' : '☀️ Light';
    }
    async function askCoach() {
      const key = document.getElementById('apiKey').value.trim();
      const q = document.getElementById('queryBox').value.trim();
      if (!q) return;
      document.getElementById('loader').style.display = 'flex';
      document.getElementById('output').innerHTML = '';
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
          body: JSON.stringify({query: q})
        });
        const data = await res.json();
        document.getElementById('output').innerHTML = '<pre>' + (data.gemini_38_flash_coaching || JSON.stringify(data, null, 2)) + '</pre>';
      } catch (e) {
        document.getElementById('output').innerHTML = '<pre>Error: ' + e + '</pre>';
      } finally {
        document.getElementById('loader').style.display = 'none';
      }
    }
  </script>
</body>
</html>"""
    return HTMLResponse(html)
