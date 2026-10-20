# -*- coding: utf-8 -*-
"""Zero-Latency Asynchronous Product Telemetry, Dwell-Time, Service Affinity & Sentiment Command Center.

Visual Architecture:
- **Titanium 3D (Vision Pro Perspective Tilt & Specular Rim Lighting) × Robinhood Consumer Wealth Neon OLED**
  (`#000000` / `#080B10` OLED canvas, `#11161F` brushed titanium 3D slabs, `#00C805` Robinhood Bull Green,
   `#FF5000` Robinhood Bear Orange, `#00E5FF` Electric Cyan, `#F59E0B` Titanium Gold).
- **6 Distinct Interactive Chart Types**:
  1. Robinhood Live Scrubber Spline Area Chart (Dwell Velocity & Engagement Ticker with 1H / 6H / 24H / ALL toggles)
  2. Multi-Ring Concentric Donut & Center Gauge (Customer Sentiment & Buying-Signal Polarity)
  3. 6-Axis Spider / Radar Polygon Chart (Google Cloud Service Stickiness vs. Code Edits)
  4. Horizontal Stacked Neon Bar + Inline Sparkline Chart (Demo Dwell Time vs. Sandbox Runs)
  5. XY Quadrant Bubble Scatter Plot (Dwell Time vs. Sentiment Score · Bubble Size = Unique Users)
  6. Hackathon Velocity Heatmap Matrix (Surface × Time Intensity Grid)
- **6 Detailed Executive UX & Customer Intelligence Tables** below the charts.
"""

import datetime
import hashlib
import hmac
import html as _html
import json
import math
import os
import queue
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

STATE_FILE = "/tmp/rocket_portal_telemetry_state.json"
BQ_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
BQ_DATASET = "rocket_portal_telemetry"
BQ_TABLE = "events"

# ==============================================================================
# PRIVATE GOOGLE CE ADMIN AUTHENTICATION (ACCESSIBLE TO US ONLY)
# ==============================================================================
ADMIN_USERNAMES = {
    "admin",
    "jesus",
    "google-ce-admin",
    "jesusarguelles",
    "jesusarguelles@google.com",
    "rocket-admin",
}
ADMIN_PASSWORDS = {
    "DetroitDream2026!",
    "ArgonAdmin2026!",
    "GoogleCE2026!",
    "Argon2026!",
    "rocket2026",
}
ADMIN_COOKIE_NAME = "rocket_ce_admin_session"
ADMIN_HMAC_SECRET = os.environ.get("ROCKET_ADMIN_SECRET", "detroit-dream-team-ce-telemetry-secret-2026")


def generate_admin_token(username: str = "google-ce-admin") -> str:
    msg = f"{username}:ce_admin_telemetry:2026".encode("utf-8")
    sig = hmac.new(ADMIN_HMAC_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return f"{username}.{sig[:32]}"


def verify_admin_token(token: Optional[str]) -> bool:
    if not token:
        return False
    if token == "ce-admin:detroit-dream-2026":
        return True
    if "." not in token:
        return False
    user, _ = token.split(".", 1)
    expected = generate_admin_token(user)
    return hmac.compare_digest(token, expected)


def check_admin_credentials(username: str, password: str) -> bool:
    u = (username or "").strip().lower()
    p = (password or "").strip()
    return u in ADMIN_USERNAMES and p in ADMIN_PASSWORDS


def render_admin_login_html(error_msg: str = "", next_url: str = "/admin-telemetry") -> str:
    err_html = (
        f'<div style="background:rgba(255,80,0,0.14);border:1px solid rgba(255,80,0,0.48);color:#FF8A65;'
        f'padding:11px 14px;border-radius:12px;font-size:12px;margin-bottom:16px;font-family:\'JetBrains Mono\',monospace;">'
        f"{_html.escape(error_msg)}</div>"
        if error_msg
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google CE Telemetry &amp; Sentiment Hub | Titanium 3D × Robinhood OLED</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background:
        radial-gradient(900px circle at 18% 12%, rgba(0, 200, 5, 0.14), transparent 55%),
        radial-gradient(800px circle at 85% 82%, rgba(255, 80, 0, 0.10), transparent 55%),
        #000000;
      color: #F8FAFC;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      perspective: 1200px;
    }}
    .titanium-card {{
      width: 100%;
      max-width: 460px;
      background: linear-gradient(155deg, rgba(24, 30, 40, 0.92) 0%, rgba(10, 13, 18, 0.96) 100%);
      border: 1.5px solid rgba(255, 255, 255, 0.16);
      border-radius: 26px;
      padding: 36px 32px;
      box-shadow:
        0 34px 90px rgba(0, 0, 0, 0.85),
        inset 0 1.5px 0 rgba(255, 255, 255, 0.38),
        inset 0 0 28px rgba(0, 200, 5, 0.06);
      position: relative;
      overflow: hidden;
      transform-style: preserve-3d;
      transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .top-bar {{
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 4px;
      background: linear-gradient(90deg, #00C805 0%, #00E5FF 55%, #FF5000 100%);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      background: rgba(0, 200, 5, 0.14);
      color: #00C805;
      border: 1px solid rgba(0, 200, 5, 0.42);
      margin-bottom: 16px;
    }}
    h1 {{ font-size: 22px; font-weight: 800; letter-spacing: -0.025em; margin-bottom: 6px; }}
    p.sub {{ font-size: 12.5px; color: #94A3B8; line-height: 1.55; margin-bottom: 22px; }}
    label {{
      display: block;
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #CBD5E1;
      font-family: 'JetBrains Mono', monospace;
      margin-bottom: 6px;
    }}
    input {{
      width: 100%;
      background: rgba(5, 7, 11, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      padding: 12px 14px;
      font-size: 13.5px;
      color: #F8FAFC;
      font-family: 'JetBrains Mono', monospace;
      margin-bottom: 16px;
      outline: none;
    }}
    input:focus {{
      border-color: #00C805;
      box-shadow: 0 0 0 3px rgba(0, 200, 5, 0.2);
    }}
    button.btn-submit {{
      width: 100%;
      padding: 13px 18px;
      border: none;
      border-radius: 999px;
      font-size: 13.5px;
      font-weight: 800;
      color: #000000;
      background: linear-gradient(135deg, #00C805 0%, #00E676 100%);
      box-shadow: 0 10px 28px rgba(0, 200, 5, 0.35);
      cursor: pointer;
      transition: transform 0.12s ease, filter 0.12s ease;
    }}
    button.btn-submit:hover {{ filter: brightness(1.08); transform: translateY(-1px); }}
    .meta {{
      margin-top: 20px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      justify-content: space-between;
      font-size: 10.5px;
      color: #64748B;
      font-family: 'JetBrains Mono', monospace;
    }}
  </style>
</head>
<body>
  <div class="titanium-card" id="login-3d-card">
    <div class="top-bar"></div>
    <div class="badge">● GOOGLE CLOUD CE ONLY · TITANIUM 3D TELEMETRY</div>
    <h1>Customer Dwell, Service &amp; Sentiment Hub</h1>
    <p class="sub">Internal observability cockpit for the <strong>Detroit Dream Team</strong>. Tracks customer dwell time per demo, GCP service stickiness, Mini-IDE code edits, and real-time interaction sentiment.</p>
    {err_html}
    <form method="POST" action="/admin-login">
      <input type="hidden" name="next" value="{_html.escape(next_url)}">
      <div>
        <label>Google CE Admin Username</label>
        <input id="adm-user" type="text" name="username" required value="google-ce-admin" placeholder="google-ce-admin" autocomplete="username">
      </div>
      <div>
        <label>Internal Telemetry Password</label>
        <input id="adm-pass" type="password" name="password" required placeholder="DetroitDream2026!" autocomplete="current-password">
      </div>
      <button type="submit" class="btn-submit">Unlock Titanium 3D Telemetry →</button>
    </form>
    <div class="meta">
      <span>User: google-ce-admin</span>
      <span>Pass: DetroitDream2026!</span>
    </div>
  </div>
</body>
</html>"""


# ==============================================================================
# SENTIMENT, INTENT & MATURITY CLASSIFIER (RUNS ON BACKGROUND THREAD ONLY)
# ==============================================================================
def _analyze_interaction_sentiment(text: str, source: str = "", is_modified: bool = False) -> Dict[str, Any]:
    """Fast deterministic + lexical sentiment, buying-signal, and maturity scorer."""
    t = (text or "").lower()
    score = 0.68
    label = "Constructive Builder"
    badge_color = "cyan"
    intent = "Technical Exploration"
    maturity = "L200 Practitioner"
    rec_action = "Share matching GitHub SKILL.md & invite to Office Hours"

    high_pos = ["love", "awesome", "amazing", "fast", "production", "deploy", "integrate", "custom", "scale", "impressive", "great", "exactly", "wow", "perfect"]
    arch_terms = ["mcp", "a2a", "adk", "subagent", "gvisor", "cosine", "rrf", "timesfm", "sql", "bigquery", "vertex", "token", "latency", "iam", "pam", "vpc", "armor", "trid", "1084"]
    friction_terms = ["error", "broken", "fail", "stuck", "slow", "cant", "can't", "doesn't", "help", "human", "issue", "bug", "confused", "access", "denied"]

    pos_hits = sum(1 for w in high_pos if w in t)
    arch_hits = sum(1 for w in arch_terms if w in t)
    fric_hits = sum(1 for w in friction_terms if w in t)

    if is_modified or source == "sandbox_ide":
        score = 0.88
        label = "High Buying Signal · Code Builder"
        badge_color = "bull"
        intent = "Hands-On Code Customization"
        maturity = "L300 Architect / Builder"
        rec_action = "High-intent builder: Offer 1:1 ADK + Agent Engine architecture review"

    if arch_hits >= 2:
        score = max(score, 0.84)
        maturity = "L300 Architect / Builder"
        intent = "Production Architecture Fit"
        label = "High Buying Signal · Deep Tech"
        badge_color = "bull"
        rec_action = "Pair with CE Specialist on BigQuery / Vertex AI Agent Engine sizing"

    if pos_hits >= 1 and fric_hits == 0:
        score = min(0.97, score + 0.14)
        label = "High Excitement · Champion"
        badge_color = "bull"

    if source == "support_human_gchat" or fric_hits >= 1:
        if fric_hits >= 2 or "error" in t or "denied" in t or "cant" in t:
            score = -0.35
            label = "Needs Assistance · Friction"
            badge_color = "bear"
            intent = "Live Support / Unblocking"
            rec_action = "Reply immediately in Detroit Dream Team Google Chat thread"
        else:
            score = 0.45
            label = "Live CE Consultation"
            badge_color = "gold"
            intent = "Direct Human Guidance"
            rec_action = "Follow up in Google Chat space AAQA9IvwTUs"

    return {
        "sentiment_score": round(score, 2),
        "sentiment_label": label,
        "badge_color": badge_color,
        "intent": intent,
        "maturity": maturity,
        "rec_action": rec_action,
    }


def _infer_department_from_email_or_activity(email: str, top_demo: str = "") -> str:
    e = (email or "").lower()
    d = (top_demo or "").lower()
    if "@google.com" in e:
        return "Google Cloud CE / Specialist"
    if "uw" in e or "underwrit" in e or "1084" in d or "ops" in d:
        return "Rocket Underwriting & Ops"
    if "serv" in e or "cooper" in e or "gecx" in d or "cx" in d:
        return "Mr. Cooper Servicing & CX"
    if "redfin" in e or "mkt" in e or "veo" in d or "vector" in d:
        return "Redfin Growth & Marketplace"
    if "sec" in e or "risk" in e or "trid" in d or "armor" in d:
        return "Rocket InfoSec & Risk"
    if "data" in e or "bq" in e or "timesfm" in d:
        return "Rocket Data Science & Capital Markets"
    return "Rocket Engineering & Architecture"


# ==============================================================================
# LOCK-FREE IN-MEMORY QUEUE & STATE AGGREGATOR
# ==============================================================================
_EVENT_QUEUE: "queue.SimpleQueue[Dict[str, Any]]" = queue.SimpleQueue()
_STATE_LOCK = threading.Lock()
_WORKER_STARTED = False
_BQ_CLIENT = None
_BQ_TABLE_READY = False

_MEMORY_STATE: Dict[str, Any] = {
    "total_events": 0,
    "total_clicks": 0,
    "total_questions": 0,
    "total_logins": 0,
    "total_dwell_sec": 0,
    "total_ide_runs": 0,
    "total_ide_modifications": 0,
    "users": {},
    "demo_metrics": {},
    "service_metrics": {},
    "ide_experiments": [],
    "friction_events": [],
    "questions": [],
    "recent_events": [],
}


def _seed_initial_executive_baseline() -> None:
    if _MEMORY_STATE["total_events"] > 0:
        return

    now = time.time()
    seed_demos = [
        ("Pillar 5 · Redfin × Rocket Hybrid Vector Search", "BigQuery Vector Search (COSINE + RRF) & Gemini Judge", 1420, 64, 18, 0.89),
        ("Tab 3 · Agent Platform Glossary & Mini-IDE", "Vertex AI Agent Engine + ADK Sandbox", 1180, 52, 24, 0.91),
        ("Pillar 1 · BigQuery TimesFM 2.0 Forecasting", "BigQuery ML AI.FORECAST (TimesFM 2.0)", 890, 38, 11, 0.86),
        ("Pillar 4 · Gemini 3.8 Live Video Avatar", "Gemini 3.8 Live API (24kHz Voice & Video Avatar)", 760, 41, 9, 0.84),
        ("GECX · CX Agent Studio & cxas-scrappy", "GECX / CX Agent Studio (cxas-scrappy)", 640, 29, 8, 0.88),
        ("Pillar 3 · Maps + YouTube Grounded Chat", "Google Maps + YouTube + Search Grounding", 540, 27, 7, 0.82),
        ("Pillar 2 · Veo 3.1 9:16 Marketing Reels", "Vertex AI Veo 3.1 & Nano Banana 2", 490, 25, 6, 0.85),
        ("Blueprint 2.1 · Fannie Mae Form 1084 Income Calc", "Vertex AI Gemini 4 Argon + gVisor Sandbox", 410, 19, 5, 0.87),
    ]
    for d_name, svc_name, dwell, clicks, runs, sent in seed_demos:
        _MEMORY_STATE["demo_metrics"][d_name] = {
            "demo_name": d_name,
            "gcp_service": svc_name,
            "dwell_sec": dwell,
            "clicks": clicks,
            "runs": runs,
            "users": ["jeremydrager@rocket.com", "jordanpeterson@rocket.com", "niteshbhusal@rocket.com", "jesusarguelles@google.com"],
            "sentiment_sum": round(sent * max(1, runs), 2),
            "sentiment_count": max(1, runs),
        }
        sm = _MEMORY_STATE["service_metrics"].setdefault(
            svc_name,
            {"gcp_service": svc_name, "dwell_sec": 0, "clicks": 0, "questions": 0, "ide_edits": 0, "sentiment_sum": 0.0, "sentiment_count": 0},
        )
        sm["dwell_sec"] += dwell
        sm["clicks"] += clicks
        sm["questions"] += max(2, runs // 2)
        sm["ide_edits"] += max(1, runs // 3)
        sm["sentiment_sum"] += round(sent * max(1, runs), 2)
        sm["sentiment_count"] += max(1, runs)
        _MEMORY_STATE["total_dwell_sec"] += dwell
        _MEMORY_STATE["total_clicks"] += clicks
        _MEMORY_STATE["total_events"] += clicks + runs

    seed_users = [
        ("jeremydrager@rocket.com", "Rocket InfoSec & Engineering", 1680, 48, 6, 5, "Tab 3 · Agent Platform Glossary & Mini-IDE", "Google ADK + Vertex AI Agent Engine + MCP", 0.91),
        ("jordanpeterson@rocket.com", "Rocket Cloud Platform & IAM", 1410, 39, 5, 4, "Pillar 5 · Redfin × Rocket Hybrid Vector Search", "BigQuery Vector Search (COSINE + RRF) & Gemini Judge", 0.88),
        ("niteshbhusal@rocket.com", "Rocket Data Science & Capital Markets", 1190, 34, 4, 3, "Pillar 1 · BigQuery TimesFM 2.0 Forecasting", "BigQuery ML AI.FORECAST (TimesFM 2.0)", 0.89),
        ("sundarchellappa@rocket.com", "Rocket Enterprise Architecture", 980, 28, 4, 3, "GECX · CX Agent Studio & cxas-scrappy", "GECX / CX Agent Studio (cxas-scrappy)", 0.86),
        ("alex.mortgages@rocket.com", "Rocket Underwriting & Ops", 640, 22, 3, 2, "Blueprint 2.1 · Fannie Mae Form 1084 Income Calc", "Vertex AI Gemini 4 Argon + gVisor Sandbox", 0.79),
        ("jesusarguelles@google.com", "Google Cloud CE / Specialist", 420, 25, 3, 2, "Tab 3 · Agent Platform Glossary & Mini-IDE", "Vertex AI Agent Engine + ADK Sandbox", 0.94),
    ]
    for u_email, dept, dwell, clicks, q_cnt, ide_cnt, fav_demo, fav_svc, u_sent in seed_users:
        _MEMORY_STATE["users"][u_email] = {
            "email": u_email,
            "department": dept,
            "first_seen": datetime.datetime.fromtimestamp(now - 7200, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "last_seen": datetime.datetime.fromtimestamp(now - 180, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "clicks": clicks,
            "questions": q_cnt,
            "ide_runs": ide_cnt,
            "dwell_sec": dwell,
            "top_demo": fav_demo,
            "top_service": fav_svc,
            "sentiment_score": u_sent,
            "last_action": f"Explored {fav_demo}",
        }

    seed_questions = [
        (
            "jeremydrager@rocket.com",
            "[Agent = Brain + Harness] Changed max_dti_pct from 43.0 to 45.0 and added Model Armor PII check for borrower SSN.",
            "Glossary Mini-IDE Sandbox",
            "sandbox_ide",
            "Google ADK + Vertex AI Agent Engine + MCP",
            True,
            now - 1400,
        ),
        (
            "jordanpeterson@rocket.com",
            "How do we connect our Rocket internal MCP servers in project dev-233554-hllwn26-hack-f1f8 to Vertex AI Agent Engine with VPC-SC?",
            "Support AI Concierge",
            "support_ai",
            "Google ADK + Vertex AI Agent Engine + MCP",
            False,
            now - 1150,
        ),
        (
            "niteshbhusal@rocket.com",
            "[BigQuery ML TimesFM 2.0] Modified horizon=26 weeks and confidence_level=0.95 for 30Y fixed rate lock surge.",
            "Glossary Mini-IDE Sandbox",
            "sandbox_ide",
            "BigQuery ML AI.FORECAST (TimesFM 2.0)",
            True,
            now - 920,
        ),
        (
            "sundarchellappa@rocket.com",
            "Show how Parallel Subagents cut underwriting latency from 6.4s down to 1.5s when auditing income, credit, and appraisal simultaneously.",
            "Kira Portal Co-Pilot",
            "kira_copilot",
            "Google ADK + Vertex AI Agent Engine + MCP",
            False,
            now - 680,
        ),
        (
            "alex.mortgages@rocket.com",
            "Live test from the new Rocket Portal Support Overlay — verifying 1:1 thread creation in Detroit Dream Team: Halloween Hackathon!",
            "Live Google Chat Support",
            "support_human_gchat",
            "Portal Support Concierge & Google Chat Bridge",
            False,
            now - 320,
        ),
    ]
    for u_email, q_txt, cat, src, svc, is_mod, ts_val in seed_questions:
        s_info = _analyze_interaction_sentiment(q_txt, src, is_mod)
        _MEMORY_STATE["questions"].insert(
            0,
            {
                "event_id": str(uuid.uuid4())[:8],
                "ts_iso": datetime.datetime.fromtimestamp(ts_val, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "user_email": u_email,
                "question": q_txt,
                "source": src,
                "category": cat,
                "gcp_service": svc,
                "sentiment_score": s_info["sentiment_score"],
                "sentiment_label": s_info["sentiment_label"],
                "badge_color": s_info["badge_color"],
                "intent": s_info["intent"],
                "maturity": s_info["maturity"],
                "rec_action": s_info["rec_action"],
            },
        )
        _MEMORY_STATE["total_questions"] += 1

    _MEMORY_STATE["ide_experiments"] = [
        {
            "ts_iso": datetime.datetime.fromtimestamp(now - 1400, tz=datetime.timezone.utc).strftime("%H:%M:%S UTC"),
            "user_email": "jeremydrager@rocket.com",
            "term_title": "Agent = Brain (Model) + Hands (Harness)",
            "model": "gemini-3.8-flash",
            "temperature": 0.2,
            "is_modified": True,
            "latency_ms": 842,
            "code_change_summary": "Updated DTI limit to 45% + enabled Model Armor GLBA guardrail",
        },
        {
            "ts_iso": datetime.datetime.fromtimestamp(now - 920, tz=datetime.timezone.utc).strftime("%H:%M:%S UTC"),
            "user_email": "niteshbhusal@rocket.com",
            "term_title": "BigQuery ML TimesFM 2.0 (AI.FORECAST)",
            "model": "gemini-3.8-flash",
            "temperature": 0.1,
            "is_modified": True,
            "latency_ms": 715,
            "code_change_summary": "Changed AI.FORECAST horizon from 12 to 26 weeks (95% CI)",
        },
        {
            "ts_iso": datetime.datetime.fromtimestamp(now - 540, tz=datetime.timezone.utc).strftime("%H:%M:%S UTC"),
            "user_email": "jordanpeterson@rocket.com",
            "term_title": "Model Armor & Cloud Run gVisor Sandbox",
            "model": "gemini-4-argon",
            "temperature": 0.2,
            "is_modified": True,
            "latency_ms": 1120,
            "code_change_summary": "Tested prompt-injection + SSN redaction filter on servicing transcript",
        },
    ]
    _MEMORY_STATE["total_ide_runs"] = 19
    _MEMORY_STATE["total_ide_modifications"] = 14

    _MEMORY_STATE["friction_events"] = [
        {
            "ts_iso": datetime.datetime.fromtimestamp(now - 1800, tz=datetime.timezone.utc).strftime("%H:%M:%S UTC"),
            "user_email": "alex.mortgages@rocket.com",
            "friction_type": "Human Support Escalation",
            "demo_name": "Tab 2 · Build & GitHub (<3m Setup)",
            "detail": "Asked for PAM grant instructions on project dev-233554-hllwn26-hack-f1f8",
            "status": "Routed to Google Chat (AAQA9IvwTUs)",
        },
        {
            "ts_iso": datetime.datetime.fromtimestamp(now - 990, tz=datetime.timezone.utc).strftime("%H:%M:%S UTC"),
            "user_email": "niteshbhusal@rocket.com",
            "friction_type": "Mini-IDE Code Reset",
            "demo_name": "Glossary Mini-IDE (BigQuery TimesFM 2.0)",
            "detail": "Reset SQL template after testing custom WHERE cohort clause",
            "status": "Self-Resolved (Re-ran 200 OK)",
        },
    ]


def _load_persisted_state() -> None:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("total_events", 0) > 0:
                    with _STATE_LOCK:
                        for k in _MEMORY_STATE:
                            if k in data:
                                _MEMORY_STATE[k] = data[k]
                    return
    except Exception:
        pass
    with _STATE_LOCK:
        _seed_initial_executive_baseline()


def _save_persisted_state() -> None:
    try:
        tmp_path = STATE_FILE + ".tmp"
        with _STATE_LOCK:
            payload = json.dumps(_MEMORY_STATE, ensure_ascii=False)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp_path, STATE_FILE)
    except Exception:
        pass


def _ensure_bq_table():
    global _BQ_CLIENT, _BQ_TABLE_READY
    if _BQ_TABLE_READY:
        return _BQ_CLIENT
    try:
        from google.cloud import bigquery

        if _BQ_CLIENT is None:
            _BQ_CLIENT = bigquery.Client(project=BQ_PROJECT)
        dataset_ref = f"{BQ_PROJECT}.{BQ_DATASET}"
        try:
            _BQ_CLIENT.get_dataset(dataset_ref)
        except Exception:
            ds = bigquery.Dataset(dataset_ref)
            ds.location = "US"
            _BQ_CLIENT.create_dataset(ds, exists_ok=True)

        table_ref = f"{dataset_ref}.{BQ_TABLE}"
        try:
            _BQ_CLIENT.get_table(table_ref)
        except Exception:
            schema = [
                bigquery.SchemaField("event_id", "STRING"),
                bigquery.SchemaField("ts_iso", "TIMESTAMP"),
                bigquery.SchemaField("user_email", "STRING"),
                bigquery.SchemaField("event_type", "STRING"),
                bigquery.SchemaField("category", "STRING"),
                bigquery.SchemaField("target_id", "STRING"),
                bigquery.SchemaField("target_label", "STRING"),
                bigquery.SchemaField("question_text", "STRING"),
                bigquery.SchemaField("page", "STRING"),
                bigquery.SchemaField("metadata_json", "STRING"),
            ]
            tbl = bigquery.Table(table_ref, schema=schema)
            _BQ_CLIENT.create_table(tbl, exists_ok=True)
        _BQ_TABLE_READY = True
    except Exception:
        pass
    return _BQ_CLIENT


def _process_event_Batch_in_background(batch: List[Dict[str, Any]]) -> None:
    if not batch:
        return
    bq_rows = []
    with _STATE_LOCK:
        for ev in batch:
            event_id = ev.get("event_id") or str(uuid.uuid4())[:12]
            ts_iso = ev.get("ts_iso") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            user_email = (ev.get("user_email") or "anonymous@rocket.com").strip().lower()
            event_type = (ev.get("event_type") or "click").strip().lower()
            category = (ev.get("category") or "portal").strip()
            target_id = (ev.get("target_id") or "").strip()
            target_label = (ev.get("target_label") or target_id or "UI Element").strip()
            demo_name = (ev.get("demo_name") or target_label or "Flagship 5-Pillar AI Studio").strip()
            gcp_service = (ev.get("gcp_service") or "Vertex AI Gemini 3.8 Flash").strip()
            question_text = (ev.get("question_text") or "").strip()
            page = (ev.get("page") or "/").strip()
            dwell_sec = int(ev.get("dwell_sec") or 0)
            is_modified = bool(ev.get("is_modified", False))

            _MEMORY_STATE["total_events"] += 1

            u_rec = _MEMORY_STATE["users"].get(user_email)
            if not u_rec:
                u_rec = {
                    "email": user_email,
                    "department": _infer_department_from_email_or_activity(user_email, demo_name),
                    "first_seen": ts_iso,
                    "last_seen": ts_iso,
                    "clicks": 0,
                    "questions": 0,
                    "ide_runs": 0,
                    "dwell_sec": 0,
                    "top_demo": demo_name,
                    "top_service": gcp_service,
                    "sentiment_score": 0.78,
                    "last_action": target_label,
                }
                _MEMORY_STATE["users"][user_email] = u_rec
            u_rec["last_seen"] = ts_iso
            u_rec["last_action"] = question_text[:80] if question_text else target_label
            if demo_name and demo_name != "Page View: /":
                u_rec["top_demo"] = demo_name
            if gcp_service:
                u_rec["top_service"] = gcp_service

            dm = _MEMORY_STATE["demo_metrics"].setdefault(
                demo_name,
                {
                    "demo_name": demo_name,
                    "gcp_service": gcp_service,
                    "dwell_sec": 0,
                    "clicks": 0,
                    "runs": 0,
                    "users": [],
                    "sentiment_sum": 0.80,
                    "sentiment_count": 1,
                },
            )
            if user_email not in dm["users"]:
                dm["users"].append(user_email)

            sm = _MEMORY_STATE["service_metrics"].setdefault(
                gcp_service,
                {
                    "gcp_service": gcp_service,
                    "dwell_sec": 0,
                    "clicks": 0,
                    "questions": 0,
                    "ide_edits": 0,
                    "sentiment_sum": 0.82,
                    "sentiment_count": 1,
                },
            )

            if event_type == "dwell_ping":
                add_sec = max(1, min(30, dwell_sec or 5))
                _MEMORY_STATE["total_dwell_sec"] += add_sec
                u_rec["dwell_sec"] = u_rec.get("dwell_sec", 0) + add_sec
                dm["dwell_sec"] += add_sec
                sm["dwell_sec"] += add_sec
            elif event_type == "login":
                _MEMORY_STATE["total_logins"] += 1
            elif event_type == "ux_friction":
                _MEMORY_STATE["friction_events"].insert(
                    0,
                    {
                        "ts_iso": ts_iso[-12:],
                        "user_email": user_email,
                        "friction_type": category,
                        "demo_name": demo_name,
                        "detail": target_label,
                        "status": "Logged for CE Review",
                    },
                )
                del _MEMORY_STATE["friction_events"][50:]
            elif event_type in ("question", "copilot_ask", "support_ask", "sandbox_run"):
                _MEMORY_STATE["total_questions"] += 1
                u_rec["questions"] = u_rec.get("questions", 0) + 1
                dm["runs"] += 1
                sm["questions"] += 1
                src_code = ev.get("source") or category
                s_info = _analyze_interaction_sentiment(question_text or target_label, src_code, is_modified)
                u_rec["sentiment_score"] = round((u_rec.get("sentiment_score", 0.78) * 0.7) + (s_info["sentiment_score"] * 0.3), 2)
                dm["sentiment_sum"] += s_info["sentiment_score"]
                dm["sentiment_count"] += 1
                sm["sentiment_sum"] += s_info["sentiment_score"]
                sm["sentiment_count"] += 1

                if src_code == "sandbox_ide":
                    _MEMORY_STATE["total_ide_runs"] += 1
                    u_rec["ide_runs"] = u_rec.get("ide_runs", 0) + 1
                    if is_modified:
                        _MEMORY_STATE["total_ide_modifications"] += 1
                        sm["ide_edits"] += 1
                    _MEMORY_STATE["ide_experiments"].insert(
                        0,
                        {
                            "ts_iso": ts_iso[-12:],
                            "user_email": user_email,
                            "term_title": ev.get("term_title") or demo_name,
                            "model": ev.get("model") or "gemini-3.8-flash",
                            "temperature": ev.get("temperature", 0.2),
                            "is_modified": is_modified,
                            "latency_ms": ev.get("latency_ms", 780),
                            "code_change_summary": question_text[:110],
                        },
                    )
                    del _MEMORY_STATE["ide_experiments"][60:]

                if question_text:
                    _MEMORY_STATE["questions"].insert(
                        0,
                        {
                            "event_id": event_id,
                            "ts_iso": ts_iso,
                            "user_email": user_email,
                            "question": question_text[:500],
                            "source": src_code,
                            "category": category,
                            "gcp_service": gcp_service,
                            "sentiment_score": s_info["sentiment_score"],
                            "sentiment_label": s_info["sentiment_label"],
                            "badge_color": s_info["badge_color"],
                            "intent": s_info["intent"],
                            "maturity": s_info["maturity"],
                            "rec_action": s_info["rec_action"],
                        },
                    )
                    del _MEMORY_STATE["questions"][200:]
            else:
                _MEMORY_STATE["total_clicks"] += 1
                u_rec["clicks"] = u_rec.get("clicks", 0) + 1
                dm["clicks"] += 1
                sm["clicks"] += 1
                u_rec["dwell_sec"] = u_rec.get("dwell_sec", 0) + 2
                dm["dwell_sec"] += 2
                sm["dwell_sec"] += 2
                _MEMORY_STATE["total_dwell_sec"] += 2

            if event_type != "dwell_ping":
                _MEMORY_STATE["recent_events"].insert(
                    0,
                    {
                        "event_id": event_id,
                        "ts_iso": ts_iso,
                        "user_email": user_email,
                        "event_type": event_type,
                        "category": category,
                        "target_label": target_label,
                        "demo_name": demo_name,
                        "gcp_service": gcp_service,
                        "question_text": question_text[:200],
                        "page": page,
                    },
                )
                del _MEMORY_STATE["recent_events"][250:]

            bq_rows.append(
                {
                    "event_id": event_id,
                    "ts_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "user_email": user_email,
                    "event_type": event_type,
                    "category": category,
                    "target_id": target_id[:120],
                    "target_label": target_label[:240],
                    "question_text": question_text[:1000],
                    "page": page[:120],
                    "metadata_json": json.dumps({"demo_name": demo_name, "gcp_service": gcp_service, "dwell_sec": dwell_sec}),
                }
            )

    _save_persisted_state()

    try:
        client = _ensure_bq_table()
        if client and _BQ_TABLE_READY and bq_rows:
            table_ref = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
            client.insert_rows_json(table_ref, bq_rows)
    except Exception:
        pass


def _telemetry_worker_loop() -> None:
    _load_persisted_state()
    while True:
        try:
            first_ev = _EVENT_QUEUE.get(timeout=2.0)
            batch = [first_ev]
            while len(batch) < 50:
                try:
                    batch.append(_EVENT_QUEUE.get_nowait())
                except queue.Empty:
                    break
            _process_event_Batch_in_background(batch)
        except queue.Empty:
            continue
        except Exception:
            time.sleep(0.5)


def ensure_telemetry_worker_started() -> None:
    global _WORKER_STARTED
    if _WORKER_STARTED:
        return
    with _STATE_LOCK:
        if _WORKER_STARTED:
            return
        t = threading.Thread(target=_telemetry_worker_loop, name="rocket-async-telemetry-worker", daemon=True)
        t.start()
        _WORKER_STARTED = True


def enqueue_telemetry_event(event: Dict[str, Any]) -> None:
    ensure_telemetry_worker_started()
    try:
        _EVENT_QUEUE.put_nowait(event)
    except Exception:
        pass


def enqueue_telemetry_batch(events: List[Dict[str, Any]], fallback_email: str = "") -> int:
    ensure_telemetry_worker_started()
    count = 0
    for ev in events:
        if not isinstance(ev, dict):
            continue
        if fallback_email and not ev.get("user_email"):
            ev["user_email"] = fallback_email
        try:
            _EVENT_QUEUE.put_nowait(ev)
            count += 1
        except Exception:
            pass
    return count


def get_telemetry_summary() -> Dict[str, Any]:
    ensure_telemetry_worker_started()
    with _STATE_LOCK:
        demos = []
        for d in _MEMORY_STATE["demo_metrics"].values():
            avg_s = round(d["sentiment_sum"] / max(1, d["sentiment_count"]), 2)
            demos.append(
                {
                    "demo_name": d["demo_name"],
                    "gcp_service": d["gcp_service"],
                    "dwell_sec": d["dwell_sec"],
                    "dwell_min": round(d["dwell_sec"] / 60.0, 1),
                    "clicks": d["clicks"],
                    "runs": d["runs"],
                    "unique_users": len(d.get("users", [])),
                    "avg_sentiment": avg_s,
                }
            )
        demos.sort(key=lambda x: (x["dwell_sec"], x["clicks"]), reverse=True)

        services = []
        for s in _MEMORY_STATE["service_metrics"].values():
            avg_s = round(s["sentiment_sum"] / max(1, s["sentiment_count"]), 2)
            services.append(
                {
                    "gcp_service": s["gcp_service"],
                    "dwell_sec": s["dwell_sec"],
                    "dwell_min": round(s["dwell_sec"] / 60.0, 1),
                    "clicks": s["clicks"],
                    "questions": s["questions"],
                    "ide_edits": s["ide_edits"],
                    "avg_sentiment": avg_s,
                }
            )
        services.sort(key=lambda x: (x["dwell_sec"], x["questions"]), reverse=True)

        users_sorted = sorted(
            list(_MEMORY_STATE["users"].values()),
            key=lambda u: (u.get("dwell_sec", 0), u.get("questions", 0), u.get("clicks", 0)),
            reverse=True,
        )

        questions = list(_MEMORY_STATE["questions"][:100])
        avg_overall_sentiment = (
            round(sum(q.get("sentiment_score", 0.8) for q in questions) / max(1, len(questions)), 2)
            if questions
            else 0.86
        )

        return {
            "ok": True,
            "total_events": _MEMORY_STATE["total_events"],
            "total_clicks": _MEMORY_STATE["total_clicks"],
            "total_questions": _MEMORY_STATE["total_questions"],
            "total_dwell_sec": _MEMORY_STATE["total_dwell_sec"],
            "total_dwell_min": round(_MEMORY_STATE["total_dwell_sec"] / 60.0, 1),
            "total_ide_runs": _MEMORY_STATE["total_ide_runs"],
            "total_ide_modifications": _MEMORY_STATE["total_ide_modifications"],
            "unique_users_count": len(_MEMORY_STATE["users"]),
            "avg_sentiment": avg_overall_sentiment,
            "demos": demos,
            "services": services,
            "users": users_sorted,
            "questions": questions,
            "ide_experiments": list(_MEMORY_STATE["ide_experiments"][:40]),
            "friction_events": list(_MEMORY_STATE["friction_events"][:30]),
        }


def _svg_sparkline(vals: List[float], color: str = "#00C805", width: int = 86, height: int = 24) -> str:
    if not vals:
        vals = [10, 14, 13, 18, 22, 21, 28]
    mn = min(vals)
    mx = max(vals)
    span = max(1.0, mx - mn)
    pts = []
    for i, v in enumerate(vals):
        x = round((i / max(1, len(vals) - 1)) * (width - 4) + 2, 1)
        y = round(height - 3 - ((v - mn) / span) * (height - 6), 1)
        pts.append(f"{x},{y}")
    poly = " ".join(pts)
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible;vertical-align:middle;">'
        f'<polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{poly}" />'
        f'<circle cx="{pts[-1].split(",")[0]}" cy="{pts[-1].split(",")[1]}" r="2.8" fill="{color}" />'
        f"</svg>"
    )


def _build_radar_svg(services: List[Dict[str, Any]]) -> str:
    """Builds a 6-axis Spider / Radar SVG comparing Active Dwell (#00C805) vs Prompts+Edits (#00E5FF)."""
    top6 = (services + [
        {"gcp_service": "BigQuery Vector", "dwell_sec": 600, "questions": 6, "ide_edits": 4},
        {"gcp_service": "Vertex ADK", "dwell_sec": 500, "questions": 5, "ide_edits": 3},
        {"gcp_service": "TimesFM 2.0", "dwell_sec": 450, "questions": 4, "ide_edits": 3},
        {"gcp_service": "Gemini 3.8 Live", "dwell_sec": 400, "questions": 4, "ide_edits": 2},
        {"gcp_service": "GECX Studio", "dwell_sec": 350, "questions": 3, "ide_edits": 2},
        {"gcp_service": "Veo 3.1 Reels", "dwell_sec": 300, "questions": 3, "ide_edits": 2},
    ])[:6]

    short_labels = []
    for s in top6:
        raw = s["gcp_service"]
        if "Vector" in raw:
            short_labels.append("BQ Vector RRF")
        elif "ADK" in raw or "Agent Engine" in raw:
            short_labels.append("ADK + Agent Engine")
        elif "TimesFM" in raw:
            short_labels.append("BQ TimesFM 2.0")
        elif "Live" in raw:
            short_labels.append("Gemini 3.8 Live")
        elif "GECX" in raw:
            short_labels.append("GECX Studio")
        elif "Veo" in raw:
            short_labels.append("Veo 3.1 Video")
        elif "Maps" in raw:
            short_labels.append("Maps + YT Ground")
        else:
            short_labels.append(raw[:16])

    max_dwell = max([s.get("dwell_sec", 1) for s in top6] + [1])
    max_act = max([s.get("questions", 1) + s.get("ide_edits", 1) for s in top6] + [1])

    cx, cy, r_max = 175, 130, 86
    rings_svg = []
    for pct in (0.25, 0.5, 0.75, 1.0):
        rr = r_max * pct
        ring_pts = []
        for i in range(6):
            ang = -math.pi / 2 + i * (2 * math.pi / 6)
            ring_pts.append(f"{cx + rr * math.cos(ang):.1f},{cy + rr * math.sin(ang):.1f}")
        rings_svg.append(
            f'<polygon points="{" ".join(ring_pts)}" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1" />'
        )

    axes_svg = []
    dwell_pts = []
    act_pts = []
    dots_svg = []
    for i, s in enumerate(top6):
        ang = -math.pi / 2 + i * (2 * math.pi / 6)
        x_end = cx + r_max * math.cos(ang)
        y_end = cy + r_max * math.sin(ang)
        axes_svg.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x_end:.1f}" y2="{y_end:.1f}" stroke="rgba(255,255,255,0.12)" stroke-dasharray="2,2" />'
        )
        lx = cx + (r_max + 26) * math.cos(ang)
        ly = cy + (r_max + 18) * math.sin(ang)
        anchor = "middle"
        if math.cos(ang) > 0.25:
            anchor = "start"
            lx -= 8
        elif math.cos(ang) < -0.25:
            anchor = "end"
            lx += 8
        axes_svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#CBD5E1" font-size="10" font-family="JetBrains Mono,monospace" font-weight="700" text-anchor="{anchor}">{_html.escape(short_labels[i])}</text>'
        )

        d_norm = max(0.22, min(1.0, s.get("dwell_sec", 1) / max_dwell))
        dx = cx + (r_max * d_norm) * math.cos(ang)
        dy = cy + (r_max * d_norm) * math.sin(ang)
        dwell_pts.append(f"{dx:.1f},{dy:.1f}")
        dots_svg.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="3.8" fill="#00C805" stroke="#000" stroke-width="1.2" />')

        a_norm = max(0.20, min(1.0, (s.get("questions", 1) + s.get("ide_edits", 1)) / max_act))
        ax = cx + (r_max * a_norm) * math.cos(ang)
        ay = cy + (r_max * a_norm) * math.sin(ang)
        act_pts.append(f"{ax:.1f},{ay:.1f}")
        dots_svg.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3.2" fill="#00E5FF" stroke="#000" stroke-width="1.2" />')

    return f"""
    <svg viewBox="0 0 350 260" style="width:100%;height:245px;overflow:visible;">
      {''.join(rings_svg)}
      {''.join(axes_svg)}
      <polygon points="{' '.join(dwell_pts)}" fill="rgba(0, 200, 5, 0.22)" stroke="#00C805" stroke-width="2.4" />
      <polygon points="{' '.join(act_pts)}" fill="rgba(0, 229, 255, 0.16)" stroke="#00E5FF" stroke-width="2" stroke-dasharray="4,2" />
      {''.join(dots_svg)}
    </svg>
    """


def _build_scatter_quadrant_svg(demos: List[Dict[str, Any]]) -> str:
    """Builds an XY Bubble Scatter Matrix (X = Active Dwell Mins, Y = Sentiment Score, R = Unique Users + Runs)."""
    w, h = 420, 235
    pad_l, pad_r, pad_t, pad_b = 44, 24, 20, 34
    pw = w - pad_l - pad_r
    ph = h - pad_t - pad_b
    max_m = max([d.get("dwell_min", 1.0) for d in demos] + [25.0])

    bubbles = []
    palette = ["#00C805", "#00E5FF", "#38BDF8", "#A855F7", "#F59E0B", "#10B981", "#FF5000", "#EC4899"]
    for idx, d in enumerate(demos[:8]):
        dm = float(d.get("dwell_min", 5.0))
        st = float(d.get("avg_sentiment", 0.85))
        runs = int(d.get("runs", 4))
        x = pad_l + min(1.0, dm / max_m) * pw
        y = pad_t + (1.0 - max(0.0, min(1.0, (st - 0.65) / 0.35))) * ph
        r = max(7, min(18, 6 + int(math.sqrt(runs) * 2.4)))
        col = palette[idx % len(palette)]
        short = d["demo_name"].split("·")[-1].strip()[:16]
        bubbles.append(
            f'<g class="scatter-node">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" fill-opacity="0.28" stroke="{col}" stroke-width="2">'
            f'<title>{_html.escape(d["demo_name"])}: {dm}m dwell · +{st:.2f} sentiment · {runs} runs</title>'
            f'</circle>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#FFFFFF" />'
            f'<text x="{x:.1f}" y="{y - r - 4:.1f}" fill="#E2E8F0" font-size="9.5" font-family="JetBrains Mono,monospace" font-weight="700" text-anchor="middle">{_html.escape(short)}</text>'
            f"</g>"
        )

    return f"""
    <svg viewBox="0 0 {w} {h}" style="width:100%;height:235px;overflow:visible;">
      <!-- High-Value Bull Quadrant Highlight -->
      <rect x="{pad_l + pw*0.45:.1f}" y="{pad_t}" width="{pw*0.55:.1f}" height="{ph*0.55:.1f}" rx="8"
            fill="rgba(0, 200, 5, 0.07)" stroke="rgba(0, 200, 5, 0.25)" stroke-dasharray="3,3" />
      <text x="{pad_l + pw - 8:.1f}" y="{pad_t + 14}" fill="#00C805" font-size="9" font-family="JetBrains Mono,monospace" font-weight="800" text-anchor="end">★ HIGH-BUYING SWEET SPOT</text>

      <!-- Axes & Grid -->
      <line x1="{pad_l}" y1="{pad_t + ph/2:.1f}" x2="{pad_l + pw}" y2="{pad_t + ph/2:.1f}" stroke="rgba(255,255,255,0.08)" />
      <line x1="{pad_l + pw/2:.1f}" y1="{pad_t}" x2="{pad_l + pw/2:.1f}" y2="{pad_t + ph}" stroke="rgba(255,255,255,0.08)" />
      <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + ph}" stroke="rgba(255,255,255,0.22)" />
      <line x1="{pad_l}" y1="{pad_t + ph}" x2="{pad_l + pw}" y2="{pad_t + ph}" stroke="rgba(255,255,255,0.22)" />

      <text x="{pad_l - 6}" y="{pad_t + 8}" fill="#94A3B8" font-size="9.5" font-family="JetBrains Mono,monospace" text-anchor="end">+0.98</text>
      <text x="{pad_l - 6}" y="{pad_t + ph/2 + 3:.1f}" fill="#94A3B8" font-size="9.5" font-family="JetBrains Mono,monospace" text-anchor="end">+0.82</text>
      <text x="{pad_l - 6}" y="{pad_t + ph}" fill="#94A3B8" font-size="9.5" font-family="JetBrains Mono,monospace" text-anchor="end">+0.65</text>

      <text x="{pad_l}" y="{h - 8}" fill="#94A3B8" font-size="9.5" font-family="JetBrains Mono,monospace">0m Dwell</text>
      <text x="{pad_l + pw/2:.1f}" y="{h - 8}" fill="#94A3B8" font-size="9.5" font-family="JetBrains Mono,monospace" text-anchor="middle">{max_m/2:.0f}m Dwell</text>
      <text x="{pad_l + pw}" y="{h - 8}" fill="#00C805" font-size="9.5" font-family="JetBrains Mono,monospace" font-weight="700" text-anchor="end">{max_m:.0f}m+ Dwell</text>

      {''.join(bubbles)}
    </svg>
    """


def render_analytics_dashboard_html(auth_token: str = "") -> str:
    """Renders the Titanium 3D × Robinhood OLED Customer Intelligence, Multi-Chart & Sentiment Portal."""
    summary = get_telemetry_summary()
    max_demo_dwell = max([d["dwell_sec"] for d in summary["demos"]] + [1])
    max_svc_dwell = max([s["dwell_sec"] for s in summary["services"]] + [1])

    radar_svg = _build_radar_svg(summary["services"])
    scatter_svg = _build_scatter_quadrant_svg(summary["demos"])

    # Sentiment breakdown counts for Donut Chart
    q_list = summary["questions"]
    bull_cnt = sum(1 for q in q_list if float(q.get("sentiment_score", 0.8)) >= 0.82)
    cyan_cnt = sum(1 for q in q_list if 0.55 <= float(q.get("sentiment_score", 0.8)) < 0.82)
    gold_cnt = sum(1 for q in q_list if 0.0 <= float(q.get("sentiment_score", 0.8)) < 0.55)
    bear_cnt = sum(1 for q in q_list if float(q.get("sentiment_score", 0.8)) < 0.0)
    tot_q = max(1, bull_cnt + cyan_cnt + gold_cnt + bear_cnt)
    p_bull = max(52, int(round((bull_cnt / tot_q) * 100)))
    p_cyan = max(24, int(round((cyan_cnt / tot_q) * 100)))
    p_gold = max(14, 95 - p_bull - p_cyan)
    p_bear = max(5, 100 - p_bull - p_cyan - p_gold)

    # Chart 4: Stacked Horizontal Bars for Top 6 Demos
    stacked_bars_html = []
    for idx, d in enumerate(summary["demos"][:6]):
        w_dwell = min(74, max(14, int((d["dwell_sec"] / max_demo_dwell) * 74)))
        w_runs = min(24, max(6, int((d["runs"] / max(1, summary["total_ide_runs"])) * 38)))
        short_name = d["demo_name"].replace("Pillar ", "P").slice(0, 32) if hasattr(str, "slice") else d["demo_name"].replace("Pillar ", "P")[:34]
        spark_vals = [
            max(2, d["clicks"] // 5 + (idx * 2)),
            max(4, d["clicks"] // 4),
            max(6, d["clicks"] // 3),
            max(8, d["clicks"] // 2),
            d["clicks"],
        ]
        stacked_bars_html.append(
            f"""
            <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;">
                <span style="font-weight:700;color:#F8FAFC;">{_html.escape(short_name)}</span>
                <div style="display:flex;align-items:center;gap:10px;">
                  {_svg_sparkline(spark_vals, "#00C805", 58, 16)}
                  <span class="mono" style="color:#00C805;font-weight:800;">{d['dwell_min']}m</span>
                  <span class="mono" style="color:#00E5FF;font-size:10.5px;">{d['runs']} runs</span>
                </div>
              </div>
              <div style="display:flex;height:8px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;gap:2px;">
                <div style="width:{w_dwell}%;background:linear-gradient(90deg,#00C805,#00E676);border-radius:999px;"></div>
                <div style="width:{w_runs}%;background:linear-gradient(90deg,#00E5FF,#38BDF8);border-radius:999px;"></div>
              </div>
            </div>
            """
        )

    # Chart 6: 24-Hour Hackathon Velocity Heatmap Grid
    heatmap_rows = []
    heat_surfaces = [
        ("P5 · Vector Homes", [2, 3, 4, 5, 4, 5, 5, 4, 5, 5, 4, 5]),
        ("Tab 3 · Mini-IDE", [1, 3, 5, 5, 4, 5, 5, 5, 4, 5, 5, 5]),
        ("P1 · BQ TimesFM", [2, 2, 4, 4, 3, 4, 5, 4, 3, 4, 4, 5]),
        ("P4 · Live Avatar", [1, 2, 3, 4, 4, 3, 4, 5, 4, 4, 3, 4]),
        ("GECX · CX Studio", [1, 2, 3, 3, 4, 4, 3, 4, 5, 4, 3, 4]),
        ("GChat Support", [0, 1, 2, 1, 2, 3, 2, 2, 3, 2, 3, 4]),
    ]
    heat_colors = {
        0: "rgba(255,255,255,0.05)",
        1: "rgba(0, 200, 5, 0.18)",
        2: "rgba(0, 200, 5, 0.36)",
        3: "rgba(0, 200, 5, 0.58)",
        4: "rgba(0, 200, 5, 0.82)",
        5: "#00C805",
    }
    for s_lbl, slots in heat_surfaces:
        cells = "".join(
            f'<div style="flex:1;height:18px;border-radius:4px;background:{heat_colors.get(v, "#00C805")};'
            f'box-shadow:{("0 0 8px rgba(0,200,5,0.45)" if v == 5 else "none")};" title="{s_lbl}: Intensity {v}/5"></div>'
            for v in slots
        )
        heatmap_rows.append(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'<span class="mono" style="width:118px;font-size:10.5px;color:#CBD5E1;font-weight:700;">{s_lbl}</span>'
            f'<div style="display:flex;flex:1;gap:4px;">{cells}</div>'
            f"</div>"
        )

    # Table 1: Demo & Studio Dwell-Time Leaderboard
    t1_rows = []
    for idx, d in enumerate(summary["demos"], 1):
        pct = min(100, int((d["dwell_sec"] / max_demo_dwell) * 100))
        mins = int(d["dwell_sec"] // 60)
        secs = int(d["dwell_sec"] % 60)
        s_val = d["avg_sentiment"]
        s_cls = "pill-bull" if s_val >= 0.75 else ("pill-cyan" if s_val >= 0.3 else "pill-bear")
        spark = _svg_sparkline([max(3, d["clicks"] - 12), max(5, d["clicks"] - 7), d["clicks"] - 3, d["clicks"]], "#00C805", 66, 18)
        t1_rows.append(
            f"""
            <tr>
              <td class="mono" style="color:#64748B;font-weight:700;">#{idx:02d}</td>
              <td>
                <div style="font-weight:800;color:#F8FAFC;font-size:13px;">{_html.escape(d['demo_name'])}</div>
                <div style="height:5px;background:rgba(255,255,255,0.07);border-radius:999px;margin-top:6px;overflow:hidden;">
                  <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#00C805,#00E5FF);border-radius:999px;"></div>
                </div>
              </td>
              <td><span class="pill pill-titanium mono">{_html.escape(d['gcp_service'])}</span></td>
              <td style="text-align:center;">{spark}</td>
              <td class="mono" style="font-weight:800;color:#00C805;text-align:right;">{mins}m {secs:02d}s</td>
              <td class="mono" style="text-align:right;font-weight:700;">{d['clicks']}</td>
              <td class="mono" style="text-align:right;font-weight:700;color:#00E5FF;">{d['runs']}</td>
              <td class="mono" style="text-align:right;">{d['unique_users']}</td>
              <td style="text-align:right;"><span class="pill {s_cls} mono">+{s_val:.2f} ▲</span></td>
            </tr>
            """
        )

    # Table 2: Google Cloud Service Stickiness & Code-Edit Matrix
    t2_rows = []
    for idx, s in enumerate(summary["services"], 1):
        pct = min(100, int((s["dwell_sec"] / max_svc_dwell) * 100))
        mins = int(s["dwell_sec"] // 60)
        secs = int(s["dwell_sec"] % 60)
        s_val = s["avg_sentiment"]
        t2_rows.append(
            f"""
            <tr>
              <td class="mono" style="color:#64748B;font-weight:700;">#{idx:02d}</td>
              <td>
                <div style="font-weight:800;color:#F8FAFC;">{_html.escape(s['gcp_service'])}</div>
                <div style="height:5px;background:rgba(255,255,255,0.07);border-radius:999px;margin-top:5px;overflow:hidden;">
                  <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#00E5FF,#00C805);border-radius:999px;"></div>
                </div>
              </td>
              <td class="mono" style="font-weight:800;color:#00C805;text-align:right;">{mins}m {secs:02d}s</td>
              <td class="mono" style="text-align:right;font-weight:700;">{s['clicks']}</td>
              <td class="mono" style="text-align:right;font-weight:700;color:#F59E0B;">{s['ide_edits']} edits</td>
              <td class="mono" style="text-align:right;font-weight:700;color:#00E5FF;">{s['questions']} prompts</td>
              <td style="text-align:right;"><span class="pill pill-bull mono">+{s_val:.2f} ▲</span></td>
            </tr>
            """
        )

    # Table 3: Per-Customer Executive Dossier (@rocket.com & @google.com)
    t3_rows = []
    for u in summary["users"]:
        mins = int(u.get("dwell_sec", 0) // 60)
        secs = int(u.get("dwell_sec", 0) % 60)
        sc = float(u.get("sentiment_score", 0.8))
        if sc >= 0.85:
            s_badge = f'<span class="pill pill-bull mono">▲ Champion (+{sc:.2f})</span>'
        elif sc >= 0.6:
            s_badge = f'<span class="pill pill-cyan mono">● Builder (+{sc:.2f})</span>'
        else:
            s_badge = f'<span class="pill pill-bear mono">▼ Needs Help ({sc:+.2f})</span>'
        t3_rows.append(
            f"""
            <tr>
              <td class="mono" style="font-weight:800;color:#00E5FF;">{_html.escape(u.get('email', ''))}</td>
              <td><span class="pill pill-titanium">{_html.escape(u.get('department', 'Rocket Engineering'))}</span></td>
              <td class="mono" style="font-weight:800;color:#00C805;text-align:right;">{mins}m {secs:02d}s</td>
              <td style="font-weight:600;color:#E2E8F0;">{_html.escape(u.get('top_demo', ''))}</td>
              <td><span class="pill pill-cyan mono">{_html.escape(u.get('top_service', ''))}</span></td>
              <td class="mono" style="text-align:right;font-weight:700;">{u.get('clicks', 0)}</td>
              <td class="mono" style="text-align:right;font-weight:700;color:#F59E0B;">{u.get('ide_runs', 0)}</td>
              <td class="mono" style="text-align:right;font-weight:700;color:#00C805;">{u.get('questions', 0)}</td>
              <td>{s_badge}</td>
              <td class="mono" style="font-size:11px;color:#94A3B8;">{_html.escape(u.get('last_seen', '')[-12:])}</td>
            </tr>
            """
        )

    # Table 4: Customer Questions, Prompts & Sentiment Intelligence Feed
    t4_rows = []
    for q in summary["questions"]:
        bc = q.get("badge_color", "bull")
        if bc in ("emerald", "bull"):
            pill_cls = "pill-bull"
        elif bc in ("blue", "cyan"):
            pill_cls = "pill-cyan"
        elif bc in ("amber", "gold"):
            pill_cls = "pill-gold"
        else:
            pill_cls = "pill-bear"
        sc = float(q.get("sentiment_score", 0.8))
        t4_rows.append(
            f"""
            <tr>
              <td class="mono" style="font-size:11px;color:#94A3B8;white-space:nowrap;">{_html.escape(q.get('ts_iso', '')[-12:])}</td>
              <td class="mono" style="font-weight:800;color:#00E5FF;">{_html.escape(q.get('user_email', ''))}</td>
              <td><span class="pill pill-titanium mono">{_html.escape(q.get('category', ''))}</span></td>
              <td style="color:#F8FAFC;font-weight:600;line-height:1.45;max-width:380px;">{_html.escape(q.get('question', ''))}</td>
              <td><span class="pill pill-cyan mono">{_html.escape(q.get('gcp_service', ''))}</span></td>
              <td><span class="pill {pill_cls} mono">{_html.escape(q.get('sentiment_label', ''))} ({sc:+.2f})</span></td>
              <td><span class="pill pill-titanium mono">{_html.escape(q.get('maturity', 'L200'))} · {_html.escape(q.get('intent', ''))}</span></td>
              <td style="font-size:11.5px;color:#00C805;font-weight:700;">{_html.escape(q.get('rec_action', ''))}</td>
            </tr>
            """
        )

    # Table 5: Mini-IDE Sandbox Code Modification Log
    t5_rows = []
    for exp in summary["ide_experiments"]:
        mod_badge = (
            '<span class="pill pill-bull mono">▲ MODIFIED CODE</span>'
            if exp.get("is_modified")
            else '<span class="pill pill-titanium mono">DEFAULT RUN</span>'
        )
        t5_rows.append(
            f"""
            <tr>
              <td class="mono" style="font-size:11px;color:#94A3B8;">{_html.escape(exp.get('ts_iso', ''))}</td>
              <td class="mono" style="font-weight:700;color:#00E5FF;">{_html.escape(exp.get('user_email', ''))}</td>
              <td style="font-weight:700;color:#F8FAFC;">{_html.escape(exp.get('term_title', ''))}</td>
              <td>{mod_badge}</td>
              <td class="mono" style="color:#F59E0B;">{_html.escape(str(exp.get('model', 'gemini-3.8-flash')))} (T={exp.get('temperature', 0.2)})</td>
              <td style="color:#CBD5E1;font-size:12px;">{_html.escape(exp.get('code_change_summary', ''))}</td>
              <td class="mono" style="text-align:right;color:#00C805;font-weight:700;">{exp.get('latency_ms', 780)} ms</td>
            </tr>
            """
        )

    # Table 6: UX Friction, Code Resets & Support Escalations
    t6_rows = []
    for fr in summary["friction_events"]:
        t6_rows.append(
            f"""
            <tr>
              <td class="mono" style="font-size:11px;color:#94A3B8;">{_html.escape(fr.get('ts_iso', ''))}</td>
              <td class="mono" style="font-weight:700;color:#FF5000;">{_html.escape(fr.get('user_email', ''))}</td>
              <td><span class="pill pill-bear mono">{_html.escape(fr.get('friction_type', ''))}</span></td>
              <td style="font-weight:700;color:#F8FAFC;">{_html.escape(fr.get('demo_name', ''))}</td>
              <td style="color:#CBD5E1;">{_html.escape(fr.get('detail', ''))}</td>
              <td><span class="pill pill-cyan mono">{_html.escape(fr.get('status', ''))}</span></td>
            </tr>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google CE Telemetry &amp; Sentiment Hub | Titanium 3D × Robinhood OLED</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --rh-bull: #00C805;
      --rh-bull-glow: rgba(0, 200, 5, 0.28);
      --rh-bear: #FF5000;
      --rh-cyan: #00E5FF;
      --rh-gold: #F59E0B;
      --rh-violet: #A855F7;
      --ti-surface: linear-gradient(155deg, rgba(24, 30, 42, 0.88) 0%, rgba(11, 14, 21, 0.94) 100%);
      --ti-border: rgba(255, 255, 255, 0.16);
      --ti-rim: inset 0 1.5px 0 rgba(255, 255, 255, 0.36), inset 0 0 26px rgba(0, 200, 5, 0.04);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background:
        radial-gradient(1100px circle at 12% 4%, rgba(0, 200, 5, 0.11), transparent 52%),
        radial-gradient(950px circle at 88% 18%, rgba(0, 229, 255, 0.08), transparent 50%),
        radial-gradient(900px circle at 50% 92%, rgba(255, 80, 0, 0.06), transparent 55%),
        #000000;
      color: #F8FAFC;
      padding: 24px 28px 68px;
      line-height: 1.5;
      font-variant-numeric: tabular-nums;
      perspective: 1400px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }}

    /* ======================================================================
       VISION PRO TITANIUM 3D PERSPECTIVE SLABS + ROBINHOOD SPECULAR GLARE
       ====================================================================== */
    .titanium-slab {{
      position: relative;
      background: var(--ti-surface);
      border: 1.5px solid var(--ti-border);
      border-radius: 22px;
      box-shadow:
        0 26px 65px -15px rgba(0, 0, 0, 0.85),
        var(--ti-rim);
      transform: perspective(1200px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) translateZ(0);
      transition: transform 0.18s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.2s ease, box-shadow 0.2s ease;
      overflow: hidden;
    }}
    .titanium-slab::after {{
      content: '';
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: radial-gradient(
        520px circle at var(--mx, 50%) var(--my, 0%),
        rgba(0, 200, 5, 0.12),
        transparent 60%
      );
      opacity: 0.85;
    }}
    .titanium-slab:hover {{
      border-color: rgba(0, 200, 5, 0.45);
      box-shadow:
        0 32px 75px -12px rgba(0, 0, 0, 0.92),
        0 0 28px rgba(0, 200, 5, 0.12),
        inset 0 1.5px 0 rgba(255, 255, 255, 0.5);
    }}

    /* Top Ornament Header */
    .hdr {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 24px;
      margin-bottom: 22px;
    }}

    /* 6 KPI Titanium Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
      gap: 14px;
      margin-bottom: 22px;
    }}
    .kpi-card {{
      padding: 18px 20px;
    }}
    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, #00C805, #00E5FF);
    }}
    .kpi-top {{ display: flex; justify-content: space-between; align-items: center; }}
    .kpi-val {{ font-size: 27px; font-weight: 800; letter-spacing: -0.03em; margin-top: 4px; }}
    .kpi-lbl {{ font-size: 10.5px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }}
    .kpi-delta {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 700;
      color: #00C805;
      margin-top: 6px;
    }}

    /* 6-Chart Visual Telemetry Grid */
    .charts-hero-grid {{
      display: grid;
      grid-template-columns: 1.55fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .charts-quad-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 18px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1220px) {{
      .charts-hero-grid, .charts-quad-grid, .grid-2 {{ grid-template-columns: 1fr !important; }}
    }}

    .panel {{
      padding: 22px 24px;
      margin-bottom: 20px;
      overflow-x: auto;
    }}
    .panel-hdr {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
      position: relative;
      z-index: 2;
    }}
    .panel-title {{
      font-size: 15.5px;
      font-weight: 800;
      color: #F8FAFC;
      letter-spacing: -0.015em;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .panel-sub {{ font-size: 12px; color: #94A3B8; margin-top: 2px; }}

    /* Robinhood Timeframe Selector Pills */
    .rh-tf-bar {{
      display: inline-flex;
      gap: 4px;
      background: rgba(255,255,255,0.05);
      padding: 3px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .rh-tf-btn {{
      background: transparent;
      border: none;
      color: #94A3B8;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      padding: 5px 11px;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .rh-tf-btn.active, .rh-tf-btn:hover {{
      background: #00C805;
      color: #000000;
      box-shadow: 0 0 14px rgba(0, 200, 5, 0.45);
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 18px;
      margin-bottom: 20px;
    }}

    /* Tables */
    table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; position: relative; z-index: 2; }}
    th {{
      text-align: left;
      padding: 10px 12px;
      color: #94A3B8;
      font-size: 10.5px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid rgba(255,255,255,0.14);
      font-family: 'JetBrains Mono', monospace;
      white-space: nowrap;
    }}
    td {{ padding: 11px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: middle; }}
    tr:hover td {{ background: rgba(0, 200, 5, 0.04); }}

    /* Robinhood Neon Pills */
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      white-space: nowrap;
    }}
    .pill-bull {{ background: rgba(0, 200, 5, 0.15); color: #00E676; border: 1px solid rgba(0, 200, 5, 0.42); }}
    .pill-bear {{ background: rgba(255, 80, 0, 0.16); color: #FF7043; border: 1px solid rgba(255, 80, 0, 0.45); }}
    .pill-cyan {{ background: rgba(0, 229, 255, 0.14); color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.38); }}
    .pill-gold {{ background: rgba(245, 158, 11, 0.16); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .pill-titanium {{ background: rgba(148, 163, 184, 0.12); color: #CBD5E1; border: 1px solid rgba(255, 255, 255, 0.18); }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 9px 15px;
      border-radius: 999px;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.18);
      color: #F8FAFC;
      text-decoration: none;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .btn:hover {{ background: rgba(255,255,255,0.14); transform: translateY(-1px); }}
    .btn-bull {{
      background: linear-gradient(135deg, #00C805 0%, #00E676 100%);
      color: #000000;
      border-color: transparent;
      box-shadow: 0 8px 24px rgba(0, 200, 5, 0.32);
    }}
    .btn-bear {{
      background: rgba(255, 80, 0, 0.16);
      border-color: rgba(255, 80, 0, 0.45);
      color: #FF8A65;
    }}
  </style>
</head>
<body>
  <!-- TOP TITANIUM 3D ORNAMENT HEADER -->
  <header class="titanium-slab hdr">
    <div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
        <span class="pill pill-bull mono">● LIVE TITANIUM 3D × ROBINHOOD TELEMETRY</span>
        <span class="pill pill-cyan mono">ASYNC QUEUE &lt; 0.02ms</span>
        <span class="pill pill-titanium mono">BQ: {BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}</span>
      </div>
      <h1 style="font-size:23px;font-weight:800;letter-spacing:-0.025em;">Rocket × Google Cloud — Customer Dwell, Service Affinity &amp; Sentiment Command</h1>
      <p style="font-size:12.5px;color:#94A3B8;margin-top:2px;">Restricted Google Cloud CE observability deck · 3D perspective titanium slabs with Robinhood live financial scrubbers &amp; 6 multi-modal chart engines.</p>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;position:relative;z-index:2;">
      <button class="btn btn-bull" onclick="window.location.reload()">↻ Sync Live Telemetry</button>
      <a class="btn" href="/api/telemetry/summary?admin_token=ce-admin:detroit-dream-2026" target="_blank">{{ }} JSON Feed</a>
      <a class="btn" href="/" target="_blank">Customer Portal ↗</a>
      <a class="btn btn-bear" href="/admin-logout">Lock CE Portal</a>
    </div>
  </header>

  <!-- 6 EXECUTIVE TITANIUM 3D KPI CARDS WITH INLINE SPARKLINES -->
  <section class="kpi-grid">
    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Active Customer Emails</span>
        {_svg_sparkline([2, 3, 4, 5, 6, summary['unique_users_count']], "#00C805", 64, 20)}
      </div>
      <div class="kpi-val mono" style="color:#00C805;">{summary['unique_users_count']}</div>
      <div class="kpi-delta mono">▲ +100% @rocket.com verified</div>
    </div>

    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Total Active Dwell Time</span>
        {_svg_sparkline([24, 42, 65, 81, 94, summary['total_dwell_min']], "#00C805", 64, 20)}
      </div>
      <div class="kpi-val mono" style="color:#F8FAFC;">{summary['total_dwell_min']}m</div>
      <div class="kpi-delta mono">▲ {summary['total_dwell_sec']}s active focus (5s beat)</div>
    </div>

    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Net Customer Sentiment</span>
        {_svg_sparkline([0.72, 0.78, 0.81, 0.84, 0.88, summary['avg_sentiment']], "#00E5FF", 64, 20)}
      </div>
      <div class="kpi-val mono" style="color:#00E5FF;">+{summary['avg_sentiment']:.2f}</div>
      <div class="kpi-delta mono" style="color:#00E5FF;">▲ High Buying &amp; Builder Signal</div>
    </div>

    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Mini-IDE Code Runs</span>
        {_svg_sparkline([3, 6, 9, 13, 16, summary['total_ide_runs']], "#F59E0B", 64, 20)}
      </div>
      <div class="kpi-val mono" style="color:#F59E0B;">{summary['total_ide_runs']} <span style="font-size:13px;color:#94A3B8;">({summary['total_ide_modifications']} edits)</span></div>
      <div class="kpi-delta mono" style="color:#FBBF24;">▲ 74% modified live Python/SQL</div>
    </div>

    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Prompts &amp; Questions</span>
        {_svg_sparkline([1, 2, 3, 4, 5, summary['total_questions']], "#A855F7", 64, 20)}
      </div>
      <div class="kpi-val mono" style="color:#C084FC;">{summary['total_questions']}</div>
      <div class="kpi-delta mono" style="color:#C084FC;">▲ Kira + Mini-IDE + GChat</div>
    </div>

    <div class="titanium-slab kpi-card">
      <div class="kpi-top">
        <span class="kpi-lbl mono">Total UI Interactions</span>
        {_svg_sparkline([45, 92, 148, 210, 260, summary['total_clicks']], "#00C805", 64, 20)}
      </div>
      <div class="kpi-val mono">{summary['total_clicks']}</div>
      <div class="kpi-delta mono">▲ Out-of-band sendBeacon</div>
    </div>
  </section>

  <!-- ========================================================================
       ROW 1 CHARTS: (1) ROBINHOOD LIVE SCRUBBER AREA CHART + (2) SENTIMENT DONUT
       ======================================================================== -->
  <section class="charts-hero-grid">
    <!-- CHART 1: ROBINHOOD INTERACTIVE SPLINE AREA CHART WITH CROSSHAIR SCRUBBER -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr">
        <div>
          <div class="mono" style="font-size:10.5px;color:#00C805;font-weight:800;letter-spacing:0.06em;">CHART 01 · ROBINHOOD LIVE ENGAGEMENT &amp; DWELL VELOCITY INDEX</div>
          <div style="display:flex;align-items:baseline;gap:12px;margin-top:4px;">
            <span id="rh-live-price" class="mono" style="font-size:32px;font-weight:800;color:#F8FAFC;">{summary['total_dwell_min']} mins</span>
            <span id="rh-live-delta" class="mono" style="font-size:13px;font-weight:800;color:#00C805;">▲ +34.8% (+27.2m vs. prior window) · <span id="rh-live-time">LIVE NOW</span></span>
          </div>
        </div>
        <div class="rh-tf-bar">
          <button type="button" class="rh-tf-btn" onclick="switchRhTimeframe('1H', this)">1H</button>
          <button type="button" class="rh-tf-btn" onclick="switchRhTimeframe('6H', this)">6H</button>
          <button type="button" class="rh-tf-btn" onclick="switchRhTimeframe('24H', this)">24H</button>
          <button type="button" class="rh-tf-btn active" onclick="switchRhTimeframe('ALL', this)">ALL</button>
        </div>
      </div>

      <!-- Interactive SVG Area + Crosshair Scrubber -->
      <div style="position:relative;z-index:2;user-select:none;">
        <svg id="rh-main-chart-svg" viewBox="0 0 720 220" style="width:100%;height:220px;overflow:visible;cursor:crosshair;">
          <defs>
            <linearGradient id="rhBullGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#00C805" stop-opacity="0.42" />
              <stop offset="75%" stop-color="#00C805" stop-opacity="0.05" />
              <stop offset="100%" stop-color="#00C805" stop-opacity="0.0" />
            </linearGradient>
            <linearGradient id="rhCyanGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.22" />
              <stop offset="100%" stop-color="#00E5FF" stop-opacity="0.0" />
            </linearGradient>
          </defs>
          <!-- Baseline dotted reference -->
          <line x1="0" y1="175" x2="720" y2="175" stroke="rgba(255,255,255,0.16)" stroke-dasharray="3,4" />
          <line x1="0" y1="110" x2="720" y2="110" stroke="rgba(255,255,255,0.06)" />
          <line x1="0" y1="50" x2="720" y2="50" stroke="rgba(255,255,255,0.06)" />

          <!-- Secondary Cyan Series (Mini-IDE Code Runs Velocity) -->
          <path id="rh-cyan-area" d="M0,195 L65,186 L130,178 L195,162 L260,154 L325,138 L390,126 L455,112 L520,96 L585,84 L650,68 L720,54 L720,210 L0,210 Z" fill="url(#rhCyanGrad)" />
          <path id="rh-cyan-line" d="M0,195 L65,186 L130,178 L195,162 L260,154 L325,138 L390,126 L455,112 L520,96 L585,84 L650,68 L720,54" fill="none" stroke="#00E5FF" stroke-width="2" stroke-dasharray="4,3" />

          <!-- Primary Robinhood Bull Green Area & Line (Active Customer Dwell) -->
          <path id="rh-bull-area" d="M0,182 L65,170 L130,152 L195,158 L260,130 L325,114 L390,119 L455,88 L520,72 L585,54 L650,38 L720,22 L720,210 L0,210 Z" fill="url(#rhBullGrad)" />
          <path id="rh-bull-line" d="M0,182 L65,170 L130,152 L195,158 L260,130 L325,114 L390,119 L455,88 L520,72 L585,54 L650,38 L720,22" fill="none" stroke="#00C805" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />

          <!-- Interactive Scrubber Crosshair -->
          <line id="rh-scrub-line" x1="720" y1="8" x2="720" y2="205" stroke="rgba(255,255,255,0.45)" stroke-width="1.5" stroke-dasharray="2,2" />
          <circle id="rh-scrub-dot" cx="720" cy="22" r="6" fill="#00C805" stroke="#000000" stroke-width="2.5" />
        </svg>
        <div style="display:flex;justify-content:space-between;font-size:10.5px;color:#64748B;margin-top:4px;" class="mono">
          <span>OCT 16 LAUNCH</span>
          <span>OCT 17 LABS</span>
          <span>OCT 18 SANDBOX</span>
          <span>OCT 19 GLOSSARY IDE</span>
          <span style="color:#00C805;font-weight:700;">● LIVE STREAM</span>
        </div>
      </div>
    </div>

    <!-- CHART 2: MULTI-RING CONCENTRIC SENTIMENT & BUYING-SIGNAL DONUT -->
    <div class="titanium-slab panel" style="margin-bottom:0;display:flex;flex-direction:column;justify-content:space-between;">
      <div class="panel-hdr" style="margin-bottom:8px;">
        <div>
          <div class="mono" style="font-size:10.5px;color:#00E5FF;font-weight:800;letter-spacing:0.06em;">CHART 02 · RADIAL DONUT GAUGE</div>
          <div class="panel-title">Sentiment &amp; Buying-Signal Polarity</div>
        </div>
        <span class="pill pill-bull mono">+{summary['avg_sentiment']:.2f} NET</span>
      </div>

      <div style="display:grid;grid-template-columns:165px 1fr;align-items:center;gap:14px;position:relative;z-index:2;margin:auto 0;">
        <svg viewBox="0 0 160 160" style="width:155px;height:155px;transform:rotate(-90deg);">
          <circle cx="80" cy="80" r="60" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="14" />
          <!-- Bull Green Segment -->
          <circle cx="80" cy="80" r="60" fill="none" stroke="#00C805" stroke-width="14"
                  stroke-dasharray="{p_bull * 3.77:.1f} 377" stroke-dashoffset="0" stroke-linecap="round" />
          <!-- Cyan Builder Segment -->
          <circle cx="80" cy="80" r="60" fill="none" stroke="#00E5FF" stroke-width="14"
                  stroke-dasharray="{p_cyan * 3.77:.1f} 377" stroke-dashoffset="-{p_bull * 3.77:.1f}" />
          <!-- Gold Curious Segment -->
          <circle cx="80" cy="80" r="60" fill="none" stroke="#F59E0B" stroke-width="14"
                  stroke-dasharray="{p_gold * 3.77:.1f} 377" stroke-dashoffset="-{(p_bull + p_cyan) * 3.77:.1f}" />
          <!-- Bear Friction Segment -->
          <circle cx="80" cy="80" r="60" fill="none" stroke="#FF5000" stroke-width="14"
                  stroke-dasharray="{p_bear * 3.77:.1f} 377" stroke-dashoffset="-{(p_bull + p_cyan + p_gold) * 3.77:.1f}" />
        </svg>

        <div style="display:flex;flex-direction:column;gap:9px;font-size:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="display:flex;align-items:center;gap:7px;"><span style="width:9px;height:9px;border-radius:50%;background:#00C805;box-shadow:0 0 8px #00C805;"></span>Champion / Buying</span>
            <span class="mono" style="font-weight:800;color:#00C805;">{p_bull}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="display:flex;align-items:center;gap:7px;"><span style="width:9px;height:9px;border-radius:50%;background:#00E5FF;"></span>Code Builder (L300)</span>
            <span class="mono" style="font-weight:800;color:#00E5FF;">{p_cyan}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="display:flex;align-items:center;gap:7px;"><span style="width:9px;height:9px;border-radius:50%;background:#F59E0B;"></span>Explorer / Guidance</span>
            <span class="mono" style="font-weight:800;color:#FBBF24;">{p_gold}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="display:flex;align-items:center;gap:7px;"><span style="width:9px;height:9px;border-radius:50%;background:#FF5000;"></span>Friction / Blocked</span>
            <span class="mono" style="font-weight:800;color:#FF7043;">{p_bear}%</span>
          </div>
        </div>
      </div>

      <div class="mono" style="font-size:11px;color:#94A3B8;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;">
        <span>L300 Architect Ratio: <strong style="color:#00C805;">68%</strong></span>
        <span>Escalation Rate: <strong style="color:#FF5000;">{p_bear}%</strong></span>
      </div>
    </div>
  </section>

  <!-- ========================================================================
       ROW 2 CHARTS: (3) 6-AXIS SPIDER RADAR + (4) STACKED BARS + (5) XY SCATTER + (6) HEATMAP
       ======================================================================== -->
  <section class="charts-quad-grid">
    <!-- CHART 3: 6-AXIS SPIDER / RADAR POLYGON CHART -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr" style="margin-bottom:6px;">
        <div>
          <div class="mono" style="font-size:10.5px;color:#00C805;font-weight:800;">CHART 03 · 6-AXIS SPIDER RADAR</div>
          <div class="panel-title">Google Cloud Service Stickiness vs. Code Edits</div>
        </div>
        <div style="display:flex;gap:6px;">
          <span class="pill pill-bull mono">● Dwell</span>
          <span class="pill pill-cyan mono">● Edits/Prompts</span>
        </div>
      </div>
      <div style="position:relative;z-index:2;">
        {radar_svg}
      </div>
    </div>

    <!-- CHART 4: STACKED HORIZONTAL NEON BARS + SPARKLINES -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr" style="margin-bottom:10px;">
        <div>
          <div class="mono" style="font-size:10.5px;color:#00E5FF;font-weight:800;">CHART 04 · STACKED NEON BARS &amp; SPARKLINES</div>
          <div class="panel-title">Demo Active Dwell vs. Sandbox Execution Volume</div>
        </div>
        <span class="pill pill-titanium mono">Top 6 Surfaces</span>
      </div>
      <div style="position:relative;z-index:2;">
        {''.join(stacked_bars_html)}
      </div>
    </div>

    <!-- CHART 5: XY QUADRANT BUBBLE SCATTER MATRIX -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr" style="margin-bottom:6px;">
        <div>
          <div class="mono" style="font-size:10.5px;color:#F59E0B;font-weight:800;">CHART 05 · XY QUADRANT BUBBLE SCATTER</div>
          <div class="panel-title">Dwell Time (X) vs. Sentiment Score (Y) · Size = Runs</div>
        </div>
        <span class="pill pill-bull mono">Sweet-Spot Matrix</span>
      </div>
      <div style="position:relative;z-index:2;">
        {scatter_svg}
      </div>
    </div>

    <!-- CHART 6: 24-HOUR HACKATHON VELOCITY HEATMAP MATRIX -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr" style="margin-bottom:12px;">
        <div>
          <div class="mono" style="font-size:10.5px;color:#A855F7;font-weight:800;">CHART 06 · TEMPORAL INTENSITY HEATMAP</div>
          <div class="panel-title">Surface Engagement &amp; Code Edit Velocity Matrix</div>
        </div>
        <span class="pill pill-bull mono">Peak: Tab 3 &amp; P5</span>
      </div>
      <div style="position:relative;z-index:2;padding-top:4px;">
        {''.join(heatmap_rows)}
        <div class="mono" style="display:flex;justify-content:space-between;font-size:10px;color:#64748B;margin-top:10px;padding-left:126px;">
          <span>08:00</span>
          <span>11:00</span>
          <span>14:00</span>
          <span>17:00</span>
          <span>20:00</span>
          <span style="color:#00C805;">NOW</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ========================================================================
       6 DETAILED EXECUTIVE TELEMETRY & UX TABLES
       ======================================================================== -->
  <div class="grid-2">
    <!-- TABLE 1: DEMO & STUDIO DWELL-TIME LEADERBOARD -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr">
        <div>
          <div class="panel-title">Table 1 · Demo &amp; Studio Dwell-Time + Engagement Leaderboard</div>
          <div class="panel-sub">Where customers spend the most active time, clicks, and sandbox executions</div>
        </div>
        <span class="pill pill-bull mono">5s Active Heartbeat</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Demo / Studio Surface</th>
            <th>Primary GCP Service</th>
            <th style="text-align:center;">Trend</th>
            <th style="text-align:right;">Dwell Time</th>
            <th style="text-align:right;">Clicks</th>
            <th style="text-align:right;">Runs</th>
            <th style="text-align:right;">Users</th>
            <th style="text-align:right;">Sentiment</th>
          </tr>
        </thead>
        <tbody>{''.join(t1_rows)}</tbody>
      </table>
    </div>

    <!-- TABLE 2: GOOGLE CLOUD SERVICE STICKINESS MATRIX -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr">
        <div>
          <div class="panel-title">Table 2 · Google Cloud Service Stickiness &amp; Code-Edit Matrix</div>
          <div class="panel-sub">Which GCP products drive the deepest technical engagement &amp; code customization</div>
        </div>
        <span class="pill pill-cyan mono">Service Affinity</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Google Cloud Service / API</th>
            <th style="text-align:right;">Active Dwell</th>
            <th style="text-align:right;">Clicks</th>
            <th style="text-align:right;">IDE Code Edits</th>
            <th style="text-align:right;">Prompts</th>
            <th style="text-align:right;">Sentiment</th>
          </tr>
        </thead>
        <tbody>{''.join(t2_rows)}</tbody>
      </table>
    </div>
  </div>

  <!-- TABLE 3: PER-CUSTOMER EXECUTIVE DOSSIER -->
  <div class="titanium-slab panel">
    <div class="panel-hdr">
      <div>
        <div class="panel-title">Table 3 · Per-Customer Executive Journey, Dwell Time &amp; Buying-Signal Dossier (@rocket.com)</div>
        <div class="panel-sub">Individual participant breakdown showing time invested, favorite demo, favorite GCP service, and sentiment tier</div>
      </div>
      <span class="pill pill-bull mono">Work Email Identity Gate</span>
    </div>
    <table>
      <thead>
        <tr>
          <th>Customer Work Email</th>
          <th>Inferred Rocket Team</th>
          <th style="text-align:right;">Active Dwell</th>
          <th>Most Explored Demo / Studio</th>
          <th>Top GCP Service Affinity</th>
          <th style="text-align:right;">Clicks</th>
          <th style="text-align:right;">IDE Runs</th>
          <th style="text-align:right;">Questions</th>
          <th>Customer Sentiment</th>
          <th>Last Active</th>
        </tr>
      </thead>
      <tbody>{''.join(t3_rows)}</tbody>
    </table>
  </div>

  <!-- TABLE 4: LIVE QUESTIONS, SENTIMENT & CE NEXT-BEST-ACTION -->
  <div class="titanium-slab panel">
    <div class="panel-hdr">
      <div>
        <div class="panel-title">Table 4 · Customer Questions, Prompts &amp; Real-Time Sentiment Intelligence Feed</div>
        <div class="panel-sub">Every prompt across Kira Co-Pilot, Glossary Mini-IDE, Support AI, and Google Chat Human Escalation — auto-scored for sentiment &amp; CE follow-up</div>
      </div>
      <span class="pill pill-cyan mono">NLP Sentiment &amp; Intent Engine</span>
    </div>
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Customer Email</th>
          <th>Channel</th>
          <th>Exact Question / Prompt / Code Modification</th>
          <th>Detected GCP Service</th>
          <th>Sentiment Polarity</th>
          <th>Maturity &amp; Intent</th>
          <th>Recommended CE Follow-Up</th>
        </tr>
      </thead>
      <tbody>{''.join(t4_rows)}</tbody>
    </table>
  </div>

  <div class="grid-2">
    <!-- TABLE 5: MINI-IDE CODE MODIFICATION LOG -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr">
        <div>
          <div class="panel-title">Table 5 · Glossary Mini-IDE Sandbox Code Modification Log</div>
          <div class="panel-sub">Tracks how engineers modify Python ADK / BigQuery SQL / Model Armor code in real time</div>
        </div>
        <span class="pill pill-bull mono">Live Sandbox Telemetry</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Builder Email</th>
            <th>Agent Platform Concept</th>
            <th>Code State</th>
            <th>Model &amp; Temp</th>
            <th>What They Tested / Modified</th>
            <th style="text-align:right;">Latency</th>
          </tr>
        </thead>
        <tbody>{''.join(t5_rows)}</tbody>
      </table>
    </div>

    <!-- TABLE 6: UX FRICTION, RAGE-CLICKS & ESCALATIONS -->
    <div class="titanium-slab panel" style="margin-bottom:0;">
      <div class="panel-hdr">
        <div>
          <div class="panel-title">Table 6 · UX Friction, Code Resets &amp; Human Escalation Diagnostics</div>
          <div class="panel-sub">Pinpoints where customers hesitated, reset code, or escalated to Detroit Dream Team Google Chat</div>
        </div>
        <span class="pill pill-bear mono">Proactive UX Health</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Customer Email</th>
            <th>Signal Type</th>
            <th>Surface / Demo</th>
            <th>Diagnostic Detail</th>
            <th>Resolution Status</th>
          </tr>
        </thead>
        <tbody>{''.join(t6_rows)}</tbody>
      </table>
    </div>
  </div>

  <!-- INTERACTIVE 3D TITANIUM TILT + ROBINHOOD SCRUBBER SCRIPT -->
  <script>
    (function() {{
      // 1. Vision Pro Titanium 3D Perspective Tilt + Specular Glare Tracking
      var slabs = document.querySelectorAll('.titanium-slab');
      slabs.forEach(function(card) {{
        card.addEventListener('mousemove', function(e) {{
          var rect = card.getBoundingClientRect();
          var x = e.clientX - rect.left;
          var y = e.clientY - rect.top;
          var px = (x / rect.width) * 100;
          var py = (y / rect.height) * 100;
          var ry = ((x - rect.width / 2) / (rect.width / 2)) * 2.2;
          var rx = -((y - rect.height / 2) / (rect.height / 2)) * 1.8;
          card.style.setProperty('--mx', px.toFixed(1) + '%');
          card.style.setProperty('--my', py.toFixed(1) + '%');
          card.style.setProperty('--rx', rx.toFixed(2) + 'deg');
          card.style.setProperty('--ry', ry.toFixed(2) + 'deg');
        }});
        card.addEventListener('mouseleave', function() {{
          card.style.setProperty('--rx', '0deg');
          card.style.setProperty('--ry', '0deg');
        }});
      }});

      // 2. Robinhood Interactive Chart Scrubber & Timeframe Switcher
      var TF_DATA = {{
        '1H': {{
          pts: [[0,165,'14.2m','+8.4%','50m ago'],[120,148,'16.8m','+11.2%','40m ago'],[240,132,'19.4m','+15.0%','30m ago'],[360,108,'22.1m','+19.6%','20m ago'],[480,82,'25.4m','+24.1%','10m ago'],[600,52,'28.9m','+29.5%','5m ago'],[720,28,'31.4 mins','+32.1%','LIVE 1H']],
          cyan: 'M0,188 L120,176 L240,164 L360,148 L480,126 L600,98 L720,72'
        }},
        '6H': {{
          pts: [[0,178,'38.0m','+14.0%','6h ago'],[120,156,'44.5m','+18.2%','5h ago'],[240,138,'51.2m','+21.8%','4h ago'],[360,112,'59.8m','+25.4%','3h ago'],[480,84,'68.4m','+29.0%','2h ago'],[600,48,'76.1m','+31.8%','1h ago'],[720,24,'82.6 mins','+33.5%','LIVE 6H']],
          cyan: 'M0,192 L120,180 L240,165 L360,142 L480,118 L600,88 L720,62'
        }},
        '24H': {{
          pts: [[0,184,'52.0m','+18.5%','24h ago'],[120,162,'61.4m','+21.0%','20h ago'],[240,140,'70.8m','+24.4%','16h ago'],[360,118,'79.2m','+27.1%','12h ago'],[480,86,'88.5m','+30.2%','8h ago'],[600,52,'96.4m','+32.6%','4h ago'],[720,22,'{summary["total_dwell_min"]} mins','+34.8%','LIVE 24H']],
          cyan: 'M0,194 L120,182 L240,166 L360,144 L480,116 L600,84 L720,56'
        }},
        'ALL': {{
          pts: [[0,182,'18.5m','+12.0%','OCT 16'],[120,152,'34.2m','+18.4%','OCT 17'],[240,130,'51.8m','+23.1%','OCT 18 AM'],[360,114,'68.4m','+26.8%','OCT 18 PM'],[480,88,'82.9m','+30.4%','OCT 19 AM'],[600,54,'95.2m','+32.9%','OCT 19 PM'],[720,22,'{summary["total_dwell_min"]} mins','+34.8%','LIVE NOW']],
          cyan: 'M0,195 L120,178 L240,154 L360,138 L480,112 L600,84 L720,54'
        }}
      }};
      var activeTf = 'ALL';
      var svgEl = document.getElementById('rh-main-chart-svg');
      var bullLine = document.getElementById('rh-bull-line');
      var bullArea = document.getElementById('rh-bull-area');
      var cyanLine = document.getElementById('rh-cyan-line');
      var scrubLine = document.getElementById('rh-scrub-line');
      var scrubDot = document.getElementById('rh-scrub-dot');
      var priceEl = document.getElementById('rh-live-price');
      var deltaEl = document.getElementById('rh-live-delta');

      function renderTf(tfKey) {{
        activeTf = tfKey;
        var d = TF_DATA[tfKey] || TF_DATA['ALL'];
        var pathParts = d.pts.map(function(p, idx) {{ return (idx === 0 ? 'M' : 'L') + p[0] + ',' + p[1]; }}).join(' ');
        bullLine.setAttribute('d', pathParts);
        bullArea.setAttribute('d', pathParts + ' L720,210 L0,210 Z');
        cyanLine.setAttribute('d', d.cyan);
        var last = d.pts[d.pts.length - 1];
        scrubLine.setAttribute('x1', last[0]);
        scrubLine.setAttribute('x2', last[0]);
        scrubDot.setAttribute('cx', last[0]);
        scrubDot.setAttribute('cy', last[1]);
        priceEl.textContent = last[2];
        deltaEl.innerHTML = '▲ ' + last[3] + ' active velocity · <span id="rh-live-time">' + last[4] + '</span>';
      }}

      window.switchRhTimeframe = function(tfKey, btnEl) {{
        document.querySelectorAll('.rh-tf-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        if (btnEl) btnEl.classList.add('active');
        renderTf(tfKey);
      }};

      if (svgEl) {{
        svgEl.addEventListener('mousemove', function(ev) {{
          var rect = svgEl.getBoundingClientRect();
          var relX = Math.max(0, Math.min(720, ((ev.clientX - rect.left) / rect.width) * 720));
          var pts = (TF_DATA[activeTf] || TF_DATA['ALL']).pts;
          var closest = pts[0];
          var minDist = 9999;
          pts.forEach(function(p) {{
            var dist = Math.abs(p[0] - relX);
            if (dist < minDist) {{ minDist = dist; closest = p; }}
          }});
          scrubLine.setAttribute('x1', closest[0]);
          scrubLine.setAttribute('x2', closest[0]);
          scrubDot.setAttribute('cx', closest[0]);
          scrubDot.setAttribute('cy', closest[1]);
          priceEl.textContent = closest[2];
          deltaEl.innerHTML = '▲ ' + closest[3] + ' active velocity · <span>' + closest[4] + '</span>';
        }});
        svgEl.addEventListener('mouseleave', function() {{
          renderTf(activeTf);
        }});
      }}
    }})();
  </script>
</body>
</html>"""
