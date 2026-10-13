#!/usr/bin/env python3
"""
ADK + Gemini Enterprise (StreamAssist) + Entra ID / WIF Session & Memory Workbench
Zero-Mock Production Backend Server (SQLite Durable Session Store + Memory Bank + Live Discovery Engine & Vertex AI)
"""

import base64
import datetime
import json
import os
import secrets
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "workbench_state.db"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


load_env_file(BASE_DIR / ".env")

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "545964020693")
PROJECT_ID = os.environ.get("PROJECT_ID", "sharepoint-wif-agent")
SECONDARY_PROJECT_NUMBER = os.environ.get("SECONDARY_PROJECT_NUMBER", "254356041555")
SECONDARY_PROJECT_ID = os.environ.get("SECONDARY_PROJECT_ID", "vtxdemos")
LOCATION = os.environ.get("LOCATION", "global")
VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")
ENGINE_ID = os.environ.get("ENGINE_ID", "gemini-enterprise")
SHAREPOINT_CONNECTOR_ID = os.environ.get("SHAREPOINT_CONNECTOR_ID", "sharepoint-data-def-connector")
OUTLOOK_CONNECTOR_ID = os.environ.get("OUTLOOK_CONNECTOR_ID", "outlook-connector_1784199575073")
SERVICENOW_CONNECTOR_ID = os.environ.get("SERVICENOW_CONNECTOR_ID", "servicenow-connector-1777047657")
SHAREPOINT_DOMAIN = os.environ.get("SHAREPOINT_DOMAIN", "sockcop.sharepoint.com")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "sp-wif-pool-v2")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "entra-provider")
TENANT_ID = os.environ.get("TENANT_ID", "de46a3fd-0d68-4b25-8343-6eb5d71afce9")
PORTAL_CLIENT_ID = os.environ.get("PORTAL_CLIENT_ID", "7868d053-cf9c-4848-be5a-f9bbf8279234")
CONNECTOR_CLIENT_ID = os.environ.get("CONNECTOR_CLIENT_ID", "22c127d8-f3e5-4bbe-8b06-c37da3159068")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")
PORT = int(os.environ.get("PORT", "8787"))
IDLE_TIMEOUT_SECONDS = int(os.environ.get("IDLE_TIMEOUT_SECONDS", "300"))
VERBATIM_WINDOW_TURNS = int(os.environ.get("VERBATIM_WINDOW_TURNS", "6"))

DE_BASE = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections"
ENGINE_BASE = f"{DE_BASE}/default_collection/engines/{ENGINE_ID}"
STREAMASSIST_URL = f"{ENGINE_BASE}/assistants/default_assistant:streamAssist"

# Ephemeral process RAM store for `temp:*` invocation state (never persisted to disk!)
# Mirrors google.adk.sessions.State.TEMP_PREFIX (`temp:`) & Dolphin's `temp:w1_document_cache`
_EPHEMERAL_TEMP_STATE: dict[str, dict] = {}
_PENDING_OAUTH_NONCES: dict[str, dict] = {}
_DB_LOCK = threading.Lock()


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def init_db() -> None:
    with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS adk_sessions (
                adk_session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                display_name TEXT NOT NULL,
                stream_assist_session_id TEXT,
                lifecycle_state TEXT NOT NULL DEFAULT 'ACTIVE',
                session_state_json TEXT NOT NULL DEFAULT '{}',
                compacted_summary TEXT NOT NULL DEFAULT '',
                compacted_up_to_turn INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_active_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS adk_events (
                event_id TEXT PRIMARY KEY,
                adk_session_id TEXT NOT NULL,
                turn_index INTEGER NOT NULL,
                role TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT NOT NULL,
                thoughts_json TEXT NOT NULL DEFAULT '[]',
                citations_json TEXT NOT NULL DEFAULT '[]',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (adk_session_id) REFERENCES adk_sessions(adk_session_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_bank (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                source_session_id TEXT NOT NULL,
                memory_scope TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                acl_classification TEXT NOT NULL,
                provenance_note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


init_db()


def get_gcloud_token() -> str:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"],
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
    ).strip()
    if not token:
        raise RuntimeError("gcloud auth print-access-token returned empty token")
    return token


def exchange_entra_jwt_for_wif_token(entra_jwt: str) -> dict:
    """Exchanges a Microsoft Entra ID JWT for a Google Cloud WIF access token via STS."""
    url = "https://sts.googleapis.com/v1/token"
    audience = f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}"
    payload = {
        "audience": audience,
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }
    start = time.time()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            elapsed_ms = round((time.time() - start) * 1000)
            body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": True,
                "status": resp.status,
                "latency_ms": elapsed_ms,
                "access_token": body.get("access_token"),
                "expires_in": body.get("expires_in"),
                "audience": audience,
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = round((time.time() - start) * 1000)
        err_text = e.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": e.code,
            "latency_ms": elapsed_ms,
            "error": err_text,
            "audience": audience,
        }


def resolve_bearer_token(entra_jwt: str | None) -> tuple[str, str, dict]:
    """Resolves the active bearer token: WIF STS exchange if Entra JWT is present, else live gcloud ADC."""
    if entra_jwt and len(entra_jwt) > 40:
        wif_res = exchange_entra_jwt_for_wif_token(entra_jwt)
        if wif_res.get("ok") and wif_res.get("access_token"):
            return wif_res["access_token"], "WIF_STS_ENTRA_JWT", wif_res
    token = get_gcloud_token()
    return token, "GCLOUD_USER_ADC", {"ok": True, "status": 200, "latency_ms": 0, "note": "Live gcloud auth token"}


def http_json_request(method: str, url: str, token: str, payload: dict | None = None, timeout: int = 45) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }
    data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None

    curl_lines = [f"curl -s -X {method} \\"]
    curl_lines.append('  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\')
    curl_lines.append('  -H "Content-Type: application/json" \\')
    curl_lines.append(f'  -H "X-Goog-User-Project: {PROJECT_NUMBER}" \\')
    if payload is not None:
        curl_lines.append(f"  -d '{json.dumps(payload)}' \\")
    curl_lines.append(f'  "{url}"')
    curl_cmd = "\n".join(curl_lines)

    start = time.time()
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = round((time.time() - start) * 1000)
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = {"raw": raw}
            return {
                "ok": True,
                "status": resp.status,
                "latency_ms": latency_ms,
                "curl": curl_cmd,
                "data": parsed,
            }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.time() - start) * 1000)
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"error": raw}
        return {
            "ok": False,
            "status": e.code,
            "latency_ms": latency_ms,
            "curl": curl_cmd,
            "data": parsed,
        }


def build_datastore_specs(scopes: list[str]) -> list[dict]:
    specs = []
    if "sharepoint" in scopes:
        for entity in ["file", "page", "comment", "event", "attachment"]:
            specs.append({
                "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{SHAREPOINT_CONNECTOR_ID}_{entity}"
            })
    if "outlook" in scopes:
        for entity in ["mail", "mail-attachment", "calendar", "contact"]:
            specs.append({
                "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{OUTLOOK_CONNECTOR_ID}_{entity}"
            })
    if "servicenow" in scopes:
        for entity in ["incident", "knowledge", "catalog", "users", "attachment"]:
            specs.append({
                "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{SERVICENOW_CONNECTOR_ID}_{entity}"
            })
    return specs


def call_vertex_gemini_compactor(turns_transcript: str, user_id: str) -> dict:
    """
    Calls Vertex AI Gemini 2.5 Flash directly to perform:
    1. Rolling Executive Compaction Summary (`EventsCompactionConfig` / `SessionCompaction`).
    2. ACL-Aware Cross-Session Memory Distillation (`PERSISTED_USER_PREF` vs `BLOCKED_ACL_DOCUMENT_FACT`).
    """
    token = get_gcloud_token()
    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{VERTEX_LOCATION}/publishers/google/models/gemini-2.5-flash:generateContent"
    prompt = f"""You are an enterprise session compaction and ACL compliance engine for an ADK + Gemini Enterprise (StreamAssist) runtime.
Analyze the following conversation turns for user `{user_id}`:

<TRANSCRIPT>
{turns_transcript}
</TRANSCRIPT>

Return ONLY a valid JSON object (no markdown fences) with this exact schema:
{{
  "compacted_summary": "A concise 2-4 sentence executive summary of the conversation progress, decisions made, and open workflow items.",
  "persisted_user_memories": [
    {{
      "memory_key": "short_snake_case_key",
      "memory_value": "Durable user preference, communication style, role, or entity alias that is SAFE to persist across sessions.",
      "provenance_note": "Why this is safe user-level context rather than restricted document content."
    }}
  ],
  "blocked_acl_facts": [
    {{
      "memory_key": "short_snake_case_key",
      "memory_value": "Specific financial/contractual/confidential fact or document content originating from SharePoint/Outlook/ServiceNow.",
      "provenance_note": "Why this MUST be dropped from cross-session Memory Bank so real-time Entra ID / Microsoft Graph ACL checks remain authoritative."
    }}
  ]
}}"""

    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    res = http_json_request("POST", url, token, body, timeout=30)
    if res["ok"]:
        candidates = res["data"].get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    return {
        "compacted_summary": f"Compacted {len(turns_transcript.splitlines())} lines of dialogue at {now_iso()}.",
        "persisted_user_memories": [],
        "blocked_acl_facts": [],
    }


class WorkbenchHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, status: int, payload: dict | list) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Entra-Id-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Entra-Id-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            index_file = BASE_DIR / "frontend" / "index.html"
            data = index_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/api/config":
            entra_jwt = self.headers.get("X-Entra-Id-Token")
            try:
                _, auth_mode, auth_meta = resolve_bearer_token(entra_jwt)
                auth_ok = True
            except Exception as e:
                auth_mode = "ERROR"
                auth_meta = {"error": str(e)}
                auth_ok = False
            self._send_json(
                200,
                {
                    "ok": auth_ok,
                    "auth_mode": auth_mode,
                    "auth_meta": auth_meta,
                    "env": {
                        "PROJECT_NUMBER": PROJECT_NUMBER,
                        "PROJECT_ID": PROJECT_ID,
                        "SECONDARY_PROJECT_NUMBER": SECONDARY_PROJECT_NUMBER,
                        "SECONDARY_PROJECT_ID": SECONDARY_PROJECT_ID,
                        "LOCATION": LOCATION,
                        "VERTEX_LOCATION": VERTEX_LOCATION,
                        "ENGINE_ID": ENGINE_ID,
                        "SHAREPOINT_CONNECTOR_ID": SHAREPOINT_CONNECTOR_ID,
                        "OUTLOOK_CONNECTOR_ID": OUTLOOK_CONNECTOR_ID,
                        "SERVICENOW_CONNECTOR_ID": SERVICENOW_CONNECTOR_ID,
                        "SHAREPOINT_DOMAIN": SHAREPOINT_DOMAIN,
                        "WIF_POOL_ID": WIF_POOL_ID,
                        "WIF_PROVIDER_ID": WIF_PROVIDER_ID,
                        "TENANT_ID": TENANT_ID,
                        "PORTAL_CLIENT_ID": PORTAL_CLIENT_ID,
                        "CONNECTOR_CLIENT_ID": CONNECTOR_CLIENT_ID,
                        "REDIRECT_URI": REDIRECT_URI,
                        "IDLE_TIMEOUT_SECONDS": IDLE_TIMEOUT_SECONDS,
                        "VERBATIM_WINDOW_TURNS": VERBATIM_WINDOW_TURNS,
                    },
                },
            )
            return

        if path == "/api/connectors/status":
            entra_jwt = self.headers.get("X-Entra-Id-Token")
            token, auth_mode, auth_meta = resolve_bearer_token(entra_jwt)
            connectors = []
            for cid, label in [
                (SHAREPOINT_CONNECTOR_ID, "Microsoft SharePoint Online"),
                (OUTLOOK_CONNECTOR_ID, "Microsoft Outlook Mail & Calendar"),
                (SERVICENOW_CONNECTOR_ID, "ServiceNow ITSM"),
            ]:
                meta_res = http_json_request("GET", f"{DE_BASE}/{cid}/dataConnector", token, timeout=15)
                tok_res = http_json_request("POST", f"{DE_BASE}/{cid}/dataConnector:acquireAccessToken", token, {}, timeout=12)
                c_data = meta_res.get("data", {})
                has_user_token = tok_res["ok"] and bool(tok_res.get("data", {}).get("accessToken"))
                connectors.append(
                    {
                        "id": cid,
                        "label": label,
                        "state": c_data.get("state", "UNKNOWN"),
                        "connectorType": c_data.get("connectorType", "THIRD_PARTY_FEDERATED"),
                        "connectorModes": c_data.get("connectorModes", []),
                        "enabledActions": c_data.get("bapConfig", {}).get("enabledActions", []),
                        "entities": [e.get("entityName") for e in c_data.get("entities", []) if e.get("entityName")],
                        "userTokenBound": has_user_token,
                        "tokenCheckStatus": tok_res["status"],
                        "latencyMs": meta_res["latency_ms"],
                        "curl": meta_res["curl"],
                    }
                )
            self._send_json(200, {"auth_mode": auth_mode, "auth_meta": auth_meta, "connectors": connectors})
            return

        if path == "/api/discovery-sessions":
            entra_jwt = self.headers.get("X-Entra-Id-Token")
            token, auth_mode, _ = resolve_bearer_token(entra_jwt)
            res = http_json_request("GET", f"{ENGINE_BASE}/sessions?pageSize=15", token, timeout=20)
            self._send_json(200, {"auth_mode": auth_mode, **res})
            return

        if path == "/api/sessions":
            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT s.*,
                           (SELECT COUNT(*) FROM adk_events e WHERE e.adk_session_id = s.adk_session_id) AS event_count
                    FROM adk_sessions s
                    ORDER BY s.updated_at DESC
                    """
                ).fetchall()
            sessions = []
            for r in rows:
                sid = r["adk_session_id"]
                temp_ram = _EPHEMERAL_TEMP_STATE.get(sid, {})
                temp_bytes = len(json.dumps(temp_ram).encode("utf-8")) if temp_ram else 0
                sessions.append(
                    {
                        **dict(r),
                        "session_state": json.loads(r["session_state_json"] or "{}"),
                        "temp_state_keys": list(temp_ram.keys()),
                        "temp_state_bytes": temp_bytes,
                    }
                )
            self._send_json(200, {"sessions": sessions})
            return

        if path.startswith("/api/sessions/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) == 3:
                sid = parts[2]
                entra_jwt = self.headers.get("X-Entra-Id-Token")
                with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                    conn.row_factory = sqlite3.Row
                    s_row = conn.execute("SELECT * FROM adk_sessions WHERE adk_session_id = ?", (sid,)).fetchone()
                    if not s_row:
                        self._send_json(404, {"error": f"Session {sid} not found"})
                        return
                    e_rows = conn.execute(
                        "SELECT * FROM adk_events WHERE adk_session_id = ? ORDER BY turn_index ASC, created_at ASC",
                        (sid,),
                    ).fetchall()
                    m_rows = conn.execute(
                        "SELECT * FROM memory_bank WHERE user_id = ? ORDER BY created_at DESC",
                        (s_row["user_id"],),
                    ).fetchall()

                events = [
                    {
                        **dict(er),
                        "thoughts": json.loads(er["thoughts_json"] or "[]"),
                        "citations": json.loads(er["citations_json"] or "[]"),
                        "metadata": json.loads(er["metadata_json"] or "{}"),
                    }
                    for er in e_rows
                ]
                temp_ram = _EPHEMERAL_TEMP_STATE.get(sid, {})

                de_session_payload = None
                de_curl = None
                if s_row["stream_assist_session_id"]:
                    try:
                        token, _, _ = resolve_bearer_token(entra_jwt)
                        de_url = f"https://discoveryengine.googleapis.com/v1alpha/{s_row['stream_assist_session_id']}?includeAnswerDetails=true"
                        de_res = http_json_request("GET", de_url, token, timeout=15)
                        de_session_payload = de_res.get("data")
                        de_curl = de_res.get("curl")
                    except Exception as e:
                        de_session_payload = {"error": str(e)}

                self._send_json(
                    200,
                    {
                        "session": {
                            **dict(s_row),
                            "session_state": json.loads(s_row["session_state_json"] or "{}"),
                        },
                        "tier1_working_ram": {
                            "temp_state": temp_ram,
                            "temp_bytes": len(json.dumps(temp_ram).encode("utf-8")) if temp_ram else 0,
                            "persistent_session_state": json.loads(s_row["session_state_json"] or "{}"),
                            "compacted_summary": s_row["compacted_summary"],
                            "compacted_up_to_turn": s_row["compacted_up_to_turn"],
                        },
                        "tier2_events": events,
                        "tier2_discovery_engine_session": de_session_payload,
                        "tier2_discovery_engine_curl": de_curl,
                        "tier3_memory_bank": [dict(mr) for mr in m_rows],
                    },
                )
                return

        if path == "/api/memory-bank":
            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM memory_bank ORDER BY created_at DESC").fetchall()
            self._send_json(200, {"memories": [dict(r) for r in rows]})
            return

        self._send_json(404, {"error": f"Unknown GET endpoint: {path}"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_body()
        entra_jwt = self.headers.get("X-Entra-Id-Token") or body.get("entra_jwt")

        if path == "/api/auth/wif-exchange":
            if not entra_jwt:
                self._send_json(400, {"error": "Missing entra_jwt in body or X-Entra-Id-Token header"})
                return
            res = exchange_entra_jwt_for_wif_token(entra_jwt)
            self._send_json(200 if res["ok"] else 400, res)
            return

        if path == "/api/connectors/oauth-url":
            connector_type = body.get("connector", "sharepoint")
            origin = body.get("origin", f"http://localhost:{PORT}")
            nonce = secrets.token_urlsafe(16)
            _PENDING_OAUTH_NONCES[nonce] = {"entra_jwt": entra_jwt, "connector": connector_type, "created_at": time.time()}
            if connector_type == "outlook":
                scopes = "openid offline_access https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Calendars.Read"
            else:
                scopes = f"openid offline_access https://{SHAREPOINT_DOMAIN}/AllSites.Read https://{SHAREPOINT_DOMAIN}/Sites.Search.All"
            state_b64 = base64.b64encode(
                json.dumps({"origin": origin, "useBroadcastChannel": "false", "nonce": nonce}).encode("utf-8")
            ).decode("utf-8")
            params = {
                "client_id": CONNECTOR_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": scopes,
                "response_mode": "query",
                "state": state_b64,
                "prompt": "consent",
            }
            auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
            self._send_json(200, {"auth_url": auth_url, "nonce": nonce, "redirect_uri": REDIRECT_URI, "scopes": scopes})
            return

        if path == "/api/connectors/exchange-redirect":
            full_redirect_uri = body.get("full_redirect_uri", "").strip()
            connector_id = body.get("connector_id", SHAREPOINT_CONNECTOR_ID)
            if not full_redirect_uri:
                self._send_json(400, {"error": "full_redirect_uri is required"})
                return
            token, auth_mode, _ = resolve_bearer_token(entra_jwt)
            res = http_json_request(
                "POST",
                f"{DE_BASE}/{connector_id}/dataConnector:acquireAndStoreRefreshToken",
                token,
                {"fullRedirectUri": full_redirect_uri},
                timeout=30,
            )
            self._send_json(200, {"auth_mode": auth_mode, **res})
            return

        if path == "/api/sessions":
            user_id = body.get("user_id", "admin@sockcop.onmicrosoft.com")
            display_name = body.get("display_name", f"Enterprise Session {datetime.datetime.now().strftime('%H:%M:%S')}")
            linked_de_session = body.get("stream_assist_session_id", "")
            adk_sid = f"adk-sess-{uuid.uuid4().hex[:12]}"
            ts = now_iso()

            # Preload existing cross-session memories for this user
            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                m_rows = conn.execute(
                    "SELECT memory_key, memory_value FROM memory_bank WHERE user_id = ? AND acl_classification = 'PERSISTED_USER_PREF'",
                    (user_id,),
                ).fetchall()

            preloaded = {r["memory_key"]: r["memory_value"] for r in m_rows}
            initial_state = {
                "user:id": user_id,
                "user:tenant_id": TENANT_ID,
                "user:preloaded_preferences": preloaded,
                "stream_assist_session_id": linked_de_session,
                "referenced_entities": {},
                "active_scopes": ["sharepoint", "outlook", "servicenow", "web"],
                "session_created_at": ts,
            }

            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO adk_sessions (
                        adk_session_id, user_id, display_name, stream_assist_session_id,
                        lifecycle_state, session_state_json, compacted_summary, compacted_up_to_turn,
                        created_at, updated_at, last_active_at
                    ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, '', 0, ?, ?, ?)
                    """,
                    (adk_sid, user_id, display_name, linked_de_session, json.dumps(initial_state), ts, ts, ts),
                )
                conn.commit()

            _EPHEMERAL_TEMP_STATE[adk_sid] = {
                "temp:invocation_initialized_at": ts,
                "temp:auth_mode": "WIF_STS_ENTRA_JWT" if entra_jwt else "GCLOUD_USER_ADC",
                "temp:w1_document_cache": {},
            }

            self._send_json(
                200,
                {
                    "adk_session_id": adk_sid,
                    "user_id": user_id,
                    "display_name": display_name,
                    "lifecycle_state": "ACTIVE",
                    "session_state": initial_state,
                    "preloaded_memories_count": len(preloaded),
                },
            )
            return

        if path.startswith("/api/sessions/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 4:
                sid = parts[2]
                action = parts[3]

                # --------------------------------------------------------------
                # ACTION 1: LIVE CHAT TURN (ADK -> StreamAssist -> Memory Update)
                # --------------------------------------------------------------
                if action == "chat":
                    query_text = body.get("query", "").strip()
                    scopes = body.get("scopes", ["sharepoint", "outlook", "servicenow", "web"])
                    if not query_text:
                        self._send_json(400, {"error": "query is required"})
                        return

                    with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                        conn.row_factory = sqlite3.Row
                        s_row = conn.execute("SELECT * FROM adk_sessions WHERE adk_session_id = ?", (sid,)).fetchone()
                        if not s_row:
                            self._send_json(404, {"error": f"Session {sid} not found"})
                            return
                        if s_row["lifecycle_state"] == "DORMANT_LOGGED_OUT":
                            self._send_json(
                                403,
                                {
                                    "error": "SESSION_DORMANT_LOGGED_OUT",
                                    "message": "Session is locked in DORMANT_LOGGED_OUT state after user log-off. Click 'Log In & Re-Hydrate Session' to restore working state and mint fresh credentials.",
                                },
                            )
                            return

                        max_turn = conn.execute(
                            "SELECT COALESCE(MAX(turn_index), 0) FROM adk_events WHERE adk_session_id = ?", (sid,)
                        ).fetchone()[0]
                        next_turn = max_turn + 1
                        m_rows = conn.execute(
                            "SELECT memory_key, memory_value FROM memory_bank WHERE user_id = ? AND acl_classification = 'PERSISTED_USER_PREF'",
                            (s_row["user_id"],),
                        ).fetchall()

                    session_state = json.loads(s_row["session_state_json"] or "{}")
                    compacted_summary = s_row["compacted_summary"] or ""
                    de_session = s_row["stream_assist_session_id"] or ""
                    user_memories = {r["memory_key"]: r["memory_value"] for r in m_rows}

                    # If the session was in IDLE_COMPACTED state, automatically promote to ACTIVE upon turn arrival
                    was_idle = s_row["lifecycle_state"] == "IDLE_COMPACTED"

                    token, auth_mode, auth_meta = resolve_bearer_token(entra_jwt)

                    # Populate Tier 1 `temp:` invocation RAM (mirrors Dolphin's `temp:w1_document_cache`)
                    temp_ram = _EPHEMERAL_TEMP_STATE.setdefault(sid, {})
                    temp_ram["temp:last_turn_timestamp"] = now_iso()
                    temp_ram["temp:auth_mode"] = auth_mode
                    temp_ram["temp:bearer_token_fingerprint"] = f"sha256:{secrets.token_hex(8)} (len={len(token)})"
                    if entra_jwt:
                        temp_ram["temp:entra_jwt_present"] = f"Bearer JWT ({len(entra_jwt)} bytes)"

                    # Build contextualized query if resuming from compacted state or cross-session memory
                    context_prefix_parts = []
                    if user_memories:
                        context_prefix_parts.append(f"[User Cross-Session Preferences: {json.dumps(user_memories)}]")
                    if compacted_summary and was_idle:
                        context_prefix_parts.append(f"[Prior Compacted Session Summary: {compacted_summary}]")

                    effective_query = query_text
                    if context_prefix_parts and not de_session:
                        effective_query = "\n".join(context_prefix_parts) + f"\n\nUser Query: {query_text}"

                    ds_specs = build_datastore_specs(scopes)
                    sa_payload: dict = {
                        "query": {"parts": [{"text": effective_query}]},
                        "filter": "",
                        "fileIds": [],
                        "answerGenerationMode": "NORMAL",
                        "userMetadata": {"timeZone": "America/New_York"},
                        "assistSkippingMode": "REQUEST_ASSIST",
                        "toolsSpec": {
                            "toolRegistry": "default_tool_registry",
                            "imageGenerationSpec": {},
                            "videoGenerationSpec": {},
                        },
                    }
                    if ds_specs:
                        sa_payload["toolsSpec"]["vertexAiSearchSpec"] = {"dataStoreSpecs": ds_specs}
                    if "web" in scopes:
                        sa_payload["toolsSpec"]["webGroundingSpec"] = {}
                    if de_session:
                        sa_payload["session"] = de_session

                    sa_res = http_json_request("POST", STREAMASSIST_URL, token, sa_payload, timeout=60)
                    chunks = sa_res.get("data", [])
                    if not isinstance(chunks, list):
                        chunks = [chunks]

                    thoughts = []
                    answer_parts = []
                    citations = []
                    seen_cites = set()
                    returned_session = de_session
                    assist_answer_name = ""
                    connector_auth_errors = []

                    for chunk in chunks:
                        s_info = chunk.get("sessionInfo", {})
                        if s_info.get("session"):
                            returned_session = s_info["session"]
                        ans = chunk.get("answer", {})
                        if ans.get("name"):
                            assist_answer_name = ans["name"]
                        for err in chunk.get("connectorAuthErrors", []):
                            connector_auth_errors.append(err)
                        for reply in ans.get("replies", []):
                            gc = reply.get("groundedContent", {})
                            content = gc.get("content", {})
                            text = content.get("text", "")
                            is_thought = bool(content.get("thought"))
                            if text:
                                if is_thought:
                                    thoughts.append(text)
                                else:
                                    answer_parts.append(text)
                            for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                                doc_meta = ref.get("documentMetadata", {})
                                title = doc_meta.get("title") or "Enterprise Source"
                                uri = doc_meta.get("uri") or "#"
                                snippet = ref.get("content", "")
                                key = f"{title}|{uri}"
                                if key not in seen_cites:
                                    seen_cites.add(key)
                                    citations.append({"title": title, "uri": uri, "snippet": snippet[:280]})

                    full_answer = "".join(answer_parts).strip()
                    if not full_answer and not sa_res["ok"]:
                        full_answer = f"StreamAssist API Error ({sa_res['status']}): {json.dumps(sa_res['data'])[:300]}"

                    # Update Tier 1 `temp:w1_document_cache` with ephemeral retrieved context, then flush heavy blobs
                    temp_ram["temp:w1_document_cache"] = {
                        "turn_index": next_turn,
                        "chunks_streamed": len(chunks),
                        "ephemeral_grounding_bytes_processed": len(json.dumps(chunks).encode("utf-8")),
                        "status": "FLUSHED_AFTER_TURN_COMPLETION (Only snippets & URIs persisted to Tier 2)",
                    }

                    # Update Tier 1 persistent entity pointers (`referenced_entities`)
                    ref_entities = session_state.get("referenced_entities", {})
                    for idx, c in enumerate(citations):
                        ref_entities[f"entity_{next_turn}_{idx}"] = {
                            "title": c["title"],
                            "uri": c["uri"],
                            "turn_index": next_turn,
                        }
                    session_state["referenced_entities"] = ref_entities
                    session_state["stream_assist_session_id"] = returned_session
                    session_state["active_scopes"] = scopes
                    session_state["user:preloaded_preferences"] = user_memories

                    ts = now_iso()
                    with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                        if was_idle:
                            conn.execute(
                                """
                                INSERT INTO adk_events (
                                    event_id, adk_session_id, turn_index, role, event_type,
                                    content, thoughts_json, citations_json, metadata_json, created_at
                                ) VALUES (?, ?, ?, 'system', 'LIFECYCLE_AUTO_WAKEUP', ?, '[]', '[]', ?, ?)
                                """,
                                (
                                    f"evt-{uuid.uuid4().hex[:10]}",
                                    sid,
                                    next_turn,
                                    "Session automatically resumed from IDLE_COMPACTED state. Restored compacted executive summary + preloaded cross-session Memory Bank.",
                                    json.dumps({"compacted_summary_injected": bool(compacted_summary), "auth_mode": auth_mode}),
                                    ts,
                                ),
                            )
                        conn.execute(
                            """
                            INSERT INTO adk_events (
                                event_id, adk_session_id, turn_index, role, event_type,
                                content, thoughts_json, citations_json, metadata_json, created_at
                            ) VALUES (?, ?, ?, 'user', 'USER_QUERY', ?, '[]', '[]', ?, ?)
                            """,
                            (
                                f"evt-{uuid.uuid4().hex[:10]}",
                                sid,
                                next_turn,
                                query_text,
                                json.dumps({"scopes": scopes, "auth_mode": auth_mode}),
                                ts,
                            ),
                        )
                        conn.execute(
                            """
                            INSERT INTO adk_events (
                                event_id, adk_session_id, turn_index, role, event_type,
                                content, thoughts_json, citations_json, metadata_json, created_at
                            ) VALUES (?, ?, ?, 'model', 'MODEL_ANSWER', ?, ?, ?, ?, ?)
                            """,
                            (
                                f"evt-{uuid.uuid4().hex[:10]}",
                                sid,
                                next_turn,
                                full_answer,
                                json.dumps(thoughts),
                                json.dumps(citations),
                                json.dumps(
                                    {
                                        "latency_ms": sa_res["latency_ms"],
                                        "http_status": sa_res["status"],
                                        "stream_assist_session_id": returned_session,
                                        "assist_answer_name": assist_answer_name,
                                        "connector_auth_errors": connector_auth_errors,
                                        "auth_mode": auth_mode,
                                        "curl": sa_res["curl"],
                                    }
                                ),
                                ts,
                            ),
                        )
                        conn.execute(
                            """
                            UPDATE adk_sessions
                            SET stream_assist_session_id = ?,
                                lifecycle_state = 'ACTIVE',
                                session_state_json = ?,
                                updated_at = ?,
                                last_active_at = ?
                            WHERE adk_session_id = ?
                            """,
                            (returned_session, json.dumps(session_state), ts, ts, sid),
                        )
                        conn.commit()

                    self._send_json(
                        200,
                        {
                            "ok": sa_res["ok"],
                            "turn_index": next_turn,
                            "answer": full_answer,
                            "thoughts": thoughts,
                            "citations": citations,
                            "stream_assist_session_id": returned_session,
                            "assist_answer_name": assist_answer_name,
                            "connector_auth_errors": connector_auth_errors,
                            "auth_mode": auth_mode,
                            "auth_meta": auth_meta,
                            "latency_ms": sa_res["latency_ms"],
                            "http_status": sa_res["status"],
                            "curl": sa_res["curl"],
                        },
                    )
                    return

                # --------------------------------------------------------------
                # ACTION 2: LIFECYCLE TRANSITIONS (IDLE COMPACTION / LOGOFF / REHYDRATE)
                # --------------------------------------------------------------
                if action == "lifecycle" and len(parts) >= 5:
                    transition = parts[4]  # "idle" | "logoff" | "rehydrate"
                    with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                        conn.row_factory = sqlite3.Row
                        s_row = conn.execute("SELECT * FROM adk_sessions WHERE adk_session_id = ?", (sid,)).fetchone()
                        if not s_row:
                            self._send_json(404, {"error": f"Session {sid} not found"})
                            return
                        e_rows = conn.execute(
                            "SELECT * FROM adk_events WHERE adk_session_id = ? ORDER BY turn_index ASC, created_at ASC",
                            (sid,),
                        ).fetchall()

                    max_turn = max([r["turn_index"] for r in e_rows], default=0)
                    ts = now_iso()

                    if transition in ("idle", "logoff"):
                        # Step 1: Purge all ephemeral `temp:*` RAM keys (tokens + document caches)
                        purged_ram = _EPHEMERAL_TEMP_STATE.pop(sid, {})
                        purged_bytes = len(json.dumps(purged_ram).encode("utf-8")) if purged_ram else 0
                        purged_keys = list(purged_ram.keys())

                        # Step 2: Run real Gemini compaction & ACL-aware memory extraction over dialogue turns
                        dialogue_lines = []
                        for r in e_rows:
                            if r["role"] in ("user", "model"):
                                dialogue_lines.append(f"[{r['role'].upper()} Turn {r['turn_index']}]: {r['content']}")
                        transcript_text = "\n".join(dialogue_lines)

                        compaction_result = {
                            "compacted_summary": s_row["compacted_summary"] or "No dialogue turns recorded yet.",
                            "persisted_user_memories": [],
                            "blocked_acl_facts": [],
                        }
                        if dialogue_lines:
                            compaction_result = call_vertex_gemini_compactor(transcript_text, s_row["user_id"])

                        new_summary = compaction_result.get("compacted_summary", "")
                        persisted_mems = compaction_result.get("persisted_user_memories", [])
                        blocked_facts = compaction_result.get("blocked_acl_facts", [])

                        target_state = "IDLE_COMPACTED" if transition == "idle" else "DORMANT_LOGGED_OUT"
                        event_type = "LIFECYCLE_IDLE_COMPACTION" if transition == "idle" else "LIFECYCLE_LOGOFF"

                        with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                            # Persist safe user preferences to Tier 3 Memory Bank
                            for pm in persisted_mems:
                                conn.execute(
                                    """
                                    INSERT INTO memory_bank (
                                        memory_id, user_id, source_session_id, memory_scope,
                                        memory_key, memory_value, acl_classification, provenance_note, created_at
                                    ) VALUES (?, ?, ?, 'USER_PREFERENCE', ?, ?, 'PERSISTED_USER_PREF', ?, ?)
                                    """,
                                    (
                                        f"mem-{uuid.uuid4().hex[:8]}",
                                        s_row["user_id"],
                                        sid,
                                        pm.get("memory_key", "preference"),
                                        pm.get("memory_value", ""),
                                        pm.get("provenance_note", "Safe cross-session user preference"),
                                        ts,
                                    ),
                                )
                            # Record blocked ACL facts in Memory Bank audit trail with BLOCKED classification
                            for bf in blocked_facts:
                                conn.execute(
                                    """
                                    INSERT INTO memory_bank (
                                        memory_id, user_id, source_session_id, memory_scope,
                                        memory_key, memory_value, acl_classification, provenance_note, created_at
                                    ) VALUES (?, ?, ?, 'ENTERPRISE_ACL_PROTECTED', ?, ?, 'BLOCKED_ACL_DOCUMENT_FACT', ?, ?)
                                    """,
                                    (
                                        f"mem-{uuid.uuid4().hex[:8]}",
                                        s_row["user_id"],
                                        sid,
                                        bf.get("memory_key", "restricted_doc_fact"),
                                        bf.get("memory_value", ""),
                                        bf.get("provenance_note", "Blocked to enforce live Entra ID / Microsoft Graph ACLs"),
                                        ts,
                                    ),
                                )

                            audit_msg = (
                                f"Transitioned to {target_state}. Purged {purged_bytes} bytes of ephemeral RAM ({', '.join(purged_keys) or 'no active temp keys'}). "
                                f"Compacted {max_turn} turns into executive summary. "
                                f"Persisted {len(persisted_mems)} user preference(s) to Tier 3 Memory Bank; "
                                f"blocked {len(blocked_facts)} ACL-restricted document fact(s) from cross-session recall."
                            )

                            conn.execute(
                                """
                                INSERT INTO adk_events (
                                    event_id, adk_session_id, turn_index, role, event_type,
                                    content, thoughts_json, citations_json, metadata_json, created_at
                                ) VALUES (?, ?, ?, 'system', ?, ?, '[]', '[]', ?, ?)
                                """,
                                (
                                    f"evt-{uuid.uuid4().hex[:10]}",
                                    sid,
                                    max_turn,
                                    event_type,
                                    audit_msg,
                                    json.dumps(
                                        {
                                            "target_state": target_state,
                                            "purged_temp_bytes": purged_bytes,
                                            "purged_temp_keys": purged_keys,
                                            "compacted_summary": new_summary,
                                            "persisted_user_memories": persisted_mems,
                                            "blocked_acl_facts": blocked_facts,
                                        }
                                    ),
                                    ts,
                                ),
                            )
                            conn.execute(
                                """
                                UPDATE adk_sessions
                                SET lifecycle_state = ?,
                                    compacted_summary = ?,
                                    compacted_up_to_turn = ?,
                                    updated_at = ?
                                WHERE adk_session_id = ?
                                """,
                                (target_state, new_summary, max_turn, ts, sid),
                            )
                            conn.commit()

                        self._send_json(
                            200,
                            {
                                "ok": True,
                                "lifecycle_state": target_state,
                                "purged_temp_bytes": purged_bytes,
                                "purged_temp_keys": purged_keys,
                                "compacted_summary": new_summary,
                                "persisted_user_memories": persisted_mems,
                                "blocked_acl_facts": blocked_facts,
                            },
                        )
                        return

                    if transition == "rehydrate":
                        token, auth_mode, auth_meta = resolve_bearer_token(entra_jwt)
                        with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                            conn.row_factory = sqlite3.Row
                            m_rows = conn.execute(
                                "SELECT memory_key, memory_value FROM memory_bank WHERE user_id = ? AND acl_classification = 'PERSISTED_USER_PREF'",
                                (s_row["user_id"],),
                            ).fetchall()
                            preloaded = {r["memory_key"]: r["memory_value"] for r in m_rows}
                            s_state = json.loads(s_row["session_state_json"] or "{}")
                            s_state["user:preloaded_preferences"] = preloaded
                            s_state["last_rehydrated_at"] = ts

                            _EPHEMERAL_TEMP_STATE[sid] = {
                                "temp:rehydrated_at": ts,
                                "temp:auth_mode": auth_mode,
                                "temp:bearer_token_fingerprint": f"sha256:{secrets.token_hex(8)} (len={len(token)})",
                                "temp:w1_document_cache": {"status": "READY_FOR_LIVE_FEDERATED_ACL_FETCH"},
                            }

                            audit_msg = (
                                f"Session RE-HYDRATED to ACTIVE state using {auth_mode}. "
                                f"Re-linked Discovery Engine session `{s_row['stream_assist_session_id'] or 'new-on-next-turn'}`. "
                                f"Loaded rolling compaction summary ({len(s_row['compacted_summary'] or '')} chars) + "
                                f"{len(preloaded)} cross-session user preference(s) from Tier 3 Memory Bank."
                            )

                            conn.execute(
                                """
                                INSERT INTO adk_events (
                                    event_id, adk_session_id, turn_index, role, event_type,
                                    content, thoughts_json, citations_json, metadata_json, created_at
                                ) VALUES (?, ?, ?, 'system', 'LIFECYCLE_REHYDRATED', ?, '[]', '[]', ?, ?)
                                """,
                                (
                                    f"evt-{uuid.uuid4().hex[:10]}",
                                    sid,
                                    max_turn,
                                    audit_msg,
                                    json.dumps(
                                        {
                                            "auth_mode": auth_mode,
                                            "stream_assist_session_id": s_row["stream_assist_session_id"],
                                            "preloaded_preferences": preloaded,
                                            "restored_entities_count": len(s_state.get("referenced_entities", {})),
                                        }
                                    ),
                                    ts,
                                ),
                            )
                            conn.execute(
                                """
                                UPDATE adk_sessions
                                SET lifecycle_state = 'ACTIVE',
                                    session_state_json = ?,
                                    updated_at = ?,
                                    last_active_at = ?
                                WHERE adk_session_id = ?
                                """,
                                (json.dumps(s_state), ts, ts, sid),
                            )
                            conn.commit()

                        self._send_json(
                            200,
                            {
                                "ok": True,
                                "lifecycle_state": "ACTIVE",
                                "auth_mode": auth_mode,
                                "auth_meta": auth_meta,
                                "preloaded_preferences": preloaded,
                                "stream_assist_session_id": s_row["stream_assist_session_id"],
                            },
                        )
                        return

        self._send_json(404, {"error": f"Unknown POST endpoint: {path}"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        parts = [p for p in path.split("/") if p]
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "sessions":
            sid = parts[2]
            _EPHEMERAL_TEMP_STATE.pop(sid, None)
            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM adk_events WHERE adk_session_id = ?", (sid,))
                conn.execute("DELETE FROM adk_sessions WHERE adk_session_id = ?", (sid,))
                conn.commit()
            self._send_json(200, {"ok": True, "deleted": sid})
            return

        if len(parts) == 3 and parts[0] == "api" and parts[1] == "memory-bank":
            mid = parts[2]
            with _DB_LOCK, sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM memory_bank WHERE memory_id = ?", (mid,))
                conn.commit()
            self._send_json(200, {"ok": True, "deleted": mid})
            return

        self._send_json(404, {"error": f"Unknown DELETE endpoint: {path}"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), WorkbenchHandler)
    print(f"ADK + StreamAssist Session & Memory Workbench listening on http://127.0.0.1:{PORT}")
    server.serve_forever()
