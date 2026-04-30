"""
StreamAssist Chat API with multi-turn conversation support.
Uses Discovery Engine sessions for conversation continuity.
"""
import os
import time
import base64
import json as _json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
ENGINE_ID = os.environ.get("ENGINE_ID")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID")
DATA_STORE_ID = os.environ.get("DATA_STORE_ID")
# Project for /api/quick (Gemini + Google Search). ADC may live in a different
# project than PROJECT_NUMBER (which is the SharePoint/Discovery Engine project).
# Fall back to GOOGLE_CLOUD_PROJECT (ADC's own project) when not set.
QUICK_PROJECT = os.environ.get("QUICK_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT") or PROJECT_NUMBER

# Validate required environment variables
_required = {"PROJECT_NUMBER": PROJECT_NUMBER, "ENGINE_ID": ENGINE_ID, "WIF_POOL_ID": WIF_POOL_ID,
             "WIF_PROVIDER_ID": WIF_PROVIDER_ID, "DATA_STORE_ID": DATA_STORE_ID}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise ValueError(f"Missing required environment variables: {', '.join(_missing)}. See .env.example")

BASE_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}"


class ChatRequest(BaseModel):
    query: str
    sharepoint_only: bool = True
    session_id: Optional[str] = None  # Full session path or None to create new


class CreateSessionRequest(BaseModel):
    display_name: str = "New Chat"


def exchange_token(jwt: str) -> str:
    """Exchange Entra JWT for GCP token via STS."""
    resp = requests.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
    }, timeout=10)
    return resp.json().get("access_token") if resp.ok else None


def extract_sources(data) -> tuple[List[dict], List[dict]]:
    """Extract grounding sources + segment-mapped supports from streamAssist response.

    Returns (sources, supports) where:
      - sources: deduped list of {title, url, snippet}
      - supports: list of {startIndex, endIndex, sourceIndices: [int]} mapping
        text spans in the answer to source indices (for inline citations).
    """
    sources = []
    supports = []
    seen = {}  # key -> source index

    def find_sources(obj, path=""):
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                find_sources(item, f"{path}[{i}]")
        elif isinstance(obj, dict):
            # Pattern 1: textGroundingMetadata (first query)
            if "textGroundingMetadata" in obj:
                tgm = obj["textGroundingMetadata"]
                # Local index map for this block (refs are 0-indexed in supports)
                local_idx_map = []
                for ref in tgm.get("references", []):
                    doc = ref.get("documentMetadata", {})
                    title = doc.get("title", "Document")
                    url = doc.get("uri", "#")
                    snippet = ref.get("content", "")[:300]
                    page_raw = doc.get("pageIdentifier", "")
                    page = None
                    try:
                        if page_raw not in (None, ""):
                            page = int(str(page_raw).strip())
                    except (TypeError, ValueError):
                        page = None
                    key = f"{title}-{url}"
                    if key in seen:
                        # Promote a known page if a later ref carries one
                        existing = sources[seen[key]]
                        if page is not None and not existing.get("page"):
                            existing["page"] = page
                        local_idx_map.append(seen[key])
                    elif title and title != "Document":
                        idx = len(sources)
                        seen[key] = idx
                        src = {"title": title, "url": url, "snippet": snippet}
                        if page is not None:
                            src["page"] = page
                        sources.append(src)
                        local_idx_map.append(idx)
                    else:
                        local_idx_map.append(None)
                # Segment supports
                for sup in tgm.get("groundingSupport", tgm.get("supports", [])):
                    seg = sup.get("segment", {})
                    start = seg.get("startIndex", sup.get("startIndex"))
                    end = seg.get("endIndex", sup.get("endIndex"))
                    refs = sup.get("referenceIndices", sup.get("groundingChunkIndices", []))
                    src_indices = []
                    for r in refs:
                        if isinstance(r, int) and r < len(local_idx_map):
                            mapped = local_idx_map[r]
                            if mapped is not None:
                                src_indices.append(mapped)
                    if start is not None and end is not None and src_indices:
                        supports.append({
                            "startIndex": start,
                            "endIndex": end,
                            "sourceIndices": src_indices,
                        })

            # Pattern 2: groundingMetadata
            if "groundingMetadata" in obj:
                gm = obj["groundingMetadata"]
                local_idx_map = []
                for chunk in gm.get("groundingChunks", []):
                    ctx = chunk.get("retrievedContext", {})
                    title = ctx.get("title", "")
                    url = ctx.get("uri", "#")
                    snippet = ctx.get("text", "")[:300]
                    page_raw = ctx.get("pageIdentifier", "")
                    page = None
                    try:
                        if page_raw not in (None, ""):
                            page = int(str(page_raw).strip())
                    except (TypeError, ValueError):
                        page = None
                    key = f"{title}-{url}"
                    if key in seen:
                        existing = sources[seen[key]]
                        if page is not None and not existing.get("page"):
                            existing["page"] = page
                        local_idx_map.append(seen[key])
                    elif title:
                        idx = len(sources)
                        seen[key] = idx
                        src = {"title": title, "url": url, "snippet": snippet}
                        if page is not None:
                            src["page"] = page
                        sources.append(src)
                        local_idx_map.append(idx)
                    else:
                        local_idx_map.append(None)
                # supportingChunks
                for chunk in gm.get("supportingChunks", []):
                    ctx = chunk.get("retrievedContext", chunk)
                    title = ctx.get("title", "")
                    url = ctx.get("uri", "#")
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen[key] = len(sources)
                        sources.append({"title": title, "url": url, "snippet": ""})
                # Segment supports
                for sup in gm.get("groundingSupports", gm.get("supports", [])):
                    seg = sup.get("segment", {})
                    start = seg.get("startIndex", sup.get("startIndex"))
                    end = seg.get("endIndex", sup.get("endIndex"))
                    refs = sup.get("groundingChunkIndices", sup.get("referenceIndices", []))
                    src_indices = []
                    for r in refs:
                        if isinstance(r, int) and r < len(local_idx_map):
                            mapped = local_idx_map[r]
                            if mapped is not None:
                                src_indices.append(mapped)
                    if start is not None and end is not None and src_indices:
                        supports.append({
                            "startIndex": start,
                            "endIndex": end,
                            "sourceIndices": src_indices,
                        })

            # Pattern 3: searchResults (alternative structure)
            if "searchResults" in obj:
                for result in obj["searchResults"]:
                    doc = result.get("document", result)
                    title = doc.get("title", doc.get("name", ""))
                    url = doc.get("uri", doc.get("link", "#"))
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen[key] = len(sources)
                        sources.append({"title": title, "url": url, "snippet": ""})

            # Pattern 4: citations
            if "citations" in obj:
                for cite in obj["citations"]:
                    title = cite.get("title", cite.get("source", ""))
                    url = cite.get("uri", cite.get("url", "#"))
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen[key] = len(sources)
                        sources.append({"title": title, "url": url, "snippet": ""})

            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    find_sources(v, f"{path}.{k}")

    find_sources(data)
    print(f"[DEBUG] Extracted {len(sources)} sources, {len(supports)} supports")
    return sources[:8], supports


@app.post("/api/sessions")
async def create_session(request: Request, body: CreateSessionRequest):
    """Create a new conversation session."""
    token = request.headers.get("X-Entra-Id-Token")
    gcp_token = exchange_token(token) if token else None

    if not gcp_token:
        return {"error": "Authentication required", "session_id": None}

    resp = requests.post(
        f"{BASE_URL}/sessions",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json={"displayName": body.display_name},
        timeout=10
    )

    if not resp.ok:
        return {"error": f"Failed to create session: {resp.text[:100]}", "session_id": None}

    session = resp.json()
    return {
        "session_id": session.get("name"),
        "display_name": session.get("displayName")
    }


@app.get("/api/sessions")
async def list_sessions(request: Request):
    """List user's conversation sessions."""
    token = request.headers.get("X-Entra-Id-Token")
    gcp_token = exchange_token(token) if token else None

    if not gcp_token:
        return {"sessions": [], "error": "Authentication required"}

    resp = requests.get(
        f"{BASE_URL}/sessions",
        headers={"Authorization": f"Bearer {gcp_token}"},
        timeout=10
    )

    if not resp.ok:
        return {"sessions": [], "error": f"Failed to list sessions: {resp.status_code}"}

    data = resp.json()
    sessions = []
    for s in data.get("sessions", [])[:20]:  # Limit to 20 most recent
        sessions.append({
            "session_id": s.get("name"),
            "display_name": s.get("displayName", "Untitled"),
            "turns": len(s.get("turns", [])),
            "state": s.get("state")
        })

    return {"sessions": sessions}


@app.get("/api/sessions/{session_id:path}")
async def get_session(session_id: str, request: Request):
    """Get session details including conversation history."""
    token = request.headers.get("X-Entra-Id-Token")
    gcp_token = exchange_token(token) if token else None

    if not gcp_token:
        return {"error": "Authentication required"}

    resp = requests.get(
        f"https://discoveryengine.googleapis.com/v1alpha/{session_id}",
        headers={"Authorization": f"Bearer {gcp_token}"},
        timeout=10
    )

    if not resp.ok:
        return {"error": f"Session not found: {resp.status_code}"}

    session = resp.json()
    turns = []
    for turn in session.get("turns", []):
        turns.append({
            "query": turn.get("query", {}).get("text", ""),
            "answer": turn.get("answer", {}).get("text", "")
        })

    return {
        "session_id": session.get("name"),
        "display_name": session.get("displayName"),
        "turns": turns
    }


def _do_chat_sync(gcp_token: str, query: str, session_id: str | None, sharepoint_only: bool, sts_ms: float = 0.0):
    """Synchronous chat logic - runs in thread pool to not block event loop."""
    # Create session if not provided
    if not session_id:
        create_resp = requests.post(
            f"{BASE_URL}/sessions",
            headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
            json={"displayName": query[:30]},
            timeout=10
        )
        if create_resp.ok:
            session_id = create_resp.json().get("name")

    # Build payload — MUST use the "widget" request shape captured from GE
    # console DevTools. The simpler {query:{text:...}} form silently returns
    # zero grounding refs for federated SharePoint per-user queries.
    # Required: query.parts[].text, assistSkippingMode, toolRegistry,
    # userMetadata, and the empty fields the widget endpoint sends.
    payload = {
        "query": {"parts": [{"text": query}]},
        "filter": "",
        "fileIds": [],
        "answerGenerationMode": "NORMAL",
        "userMetadata": {"timeZone": "America/New_York"},
        "assistSkippingMode": "REQUEST_ASSIST",
    }

    # Add session for conversation continuity
    if session_id:
        payload["session"] = session_id

    # Restrict to SharePoint when enabled. Fan out to all 5 federated-connector
    # entity-type datastores (file/page/comment/event/attachment).
    if sharepoint_only:
        sp_entities = ["file", "page", "comment", "event", "attachment"]
        sp_prefix = "sharepoint-data-def-connector"
        payload["toolsSpec"] = {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [
                    {"dataStore": (
                        f"projects/{PROJECT_NUMBER}/locations/global/"
                        f"collections/default_collection/dataStores/{sp_prefix}_{entity}"
                    )}
                    for entity in sp_entities
                ]
            },
            "toolRegistry": "default_tool_registry",
            "imageGenerationSpec": {},
            "videoGenerationSpec": {},
        }

    # Time the StreamAssist call (covers retrieval + generation server-side).
    # We split using the first non-thought chunk timestamp as a proxy for
    # "retrieval done, generation started" since DE doesn't expose phase markers.
    t_call_start = time.perf_counter()
    resp = requests.post(
        f"{BASE_URL}/assistants/default_assistant:streamAssist",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=90
    )
    t_call_end = time.perf_counter()

    if not resp.ok:
        return {
            "answer": f"API Error: {resp.status_code} - {resp.text[:200]}",
            "sources": [],
            "supports": [],
            "thoughts": [],
            "timings": {"sts_ms": int(sts_ms), "retrieval_ms": 0, "generation_ms": int((t_call_end - t_call_start) * 1000)},
            "session_id": session_id,
        }

    # Parse response
    data = resp.json()

    # Debug: Save full response to see structure
    with open("/tmp/last_response.json", "w") as f:
        _json.dump(data, f, indent=2)
    print(f"[DEBUG] Response chunks: {len(data)}")

    answer_parts = []
    thoughts = []
    first_answer_ts = None
    first_chunk_ts = None

    for chunk in data:
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            is_thought = content.get("thought", False)
            ts = reply.get("createTime")
            if first_chunk_ts is None and ts:
                first_chunk_ts = ts
            if text and is_thought:
                thoughts.append({"text": text.strip(), "createTime": ts})
            if text and not is_thought:
                answer_parts.append(text)
                if first_answer_ts is None and ts:
                    first_answer_ts = ts

    answer = "".join(answer_parts) or "I couldn't find relevant information. Try rephrasing your question."
    sources, supports = extract_sources(data)

    # Phase timing heuristic: time-to-first-answer-chunk ~= STS-result + retrieval
    # We approximate retrieval_ms as (first_answer_ts - first_chunk_ts) where
    # first_chunk is typically the first thought (after retrieval). When no
    # thought stream is present we fall back to half/half split.
    total_call_ms = int((t_call_end - t_call_start) * 1000)
    retrieval_ms = 0
    generation_ms = total_call_ms

    def _parse_ts(ts: str) -> float | None:
        if not ts:
            return None
        try:
            from datetime import datetime
            # Strip nanoseconds beyond microseconds and parse
            clean = ts.replace("Z", "+00:00")
            # Trim fractional to 6 digits
            if "." in clean:
                base, rest = clean.split(".", 1)
                frac = ""
                tail = ""
                for ch in rest:
                    if ch.isdigit():
                        frac += ch
                    else:
                        tail = rest[len(frac):]
                        break
                clean = f"{base}.{frac[:6]}{tail}"
            return datetime.fromisoformat(clean).timestamp()
        except Exception:
            return None

    t_first = _parse_ts(first_chunk_ts)
    t_ans = _parse_ts(first_answer_ts)
    if t_first and t_ans and t_ans >= t_first:
        gen_seconds = max(0.0, t_ans - t_first)
        # The first chunk arrival itself includes some retrieval latency we
        # can't see; assume retrieval = total - generation - thought-stream.
        # Better: retrieval_ms = total - (last_chunk - first_chunk + first_offset).
        # Simpler good-enough: split = first_answer offset from call start.
        # Use time-from-call-start to first-answer-chunk as retrieval+stream-warmup.
        # Since we only have the server timestamp deltas, use (t_ans - t_first)
        # as the generation phase and the rest as retrieval.
        retrieval_ms = max(0, total_call_ms - int(gen_seconds * 1000))
        generation_ms = int(gen_seconds * 1000)
    elif total_call_ms > 0:
        # Fallback: 70/30 split (retrieval typically dominates)
        retrieval_ms = int(total_call_ms * 0.7)
        generation_ms = total_call_ms - retrieval_ms

    return {
        "answer": answer,
        "sources": sources,
        "supports": supports,
        "thoughts": thoughts,
        "timings": {
            "sts_ms": int(sts_ms),
            "retrieval_ms": retrieval_ms,
            "generation_ms": generation_ms,
        },
        "session_id": session_id,
    }


@app.post("/api/chat")
async def chat(request: Request, body: ChatRequest):
    """Send a message in a conversation."""
    import asyncio

    token = request.headers.get("X-Entra-Id-Token")

    print(f"[DEBUG] Query: {body.query[:50]}...")
    print(f"[DEBUG] SharePoint Only: {body.sharepoint_only}")
    print(f"[DEBUG] Session ID: {body.session_id[:50] if body.session_id else 'None'}...")
    print(f"[DEBUG] Token present: {bool(token)}, length: {len(token) if token else 0}")

    # Save token for debugging
    if token:
        with open("/tmp/entra_token.txt", "w") as f:
            f.write(token)

    t_sts_start = time.perf_counter()
    gcp_token = exchange_token(token) if token else None
    sts_ms = (time.perf_counter() - t_sts_start) * 1000
    print(f"[DEBUG] GCP Token: {bool(gcp_token)} (STS {sts_ms:.0f}ms)")

    if not gcp_token:
        return {
            "answer": "Please login with Microsoft to chat.",
            "sources": [],
            "supports": [],
            "thoughts": [],
            "timings": {"sts_ms": int(sts_ms), "retrieval_ms": 0, "generation_ms": 0},
            "session_id": None,
        }

    # Run blocking requests in thread pool - DOES NOT BLOCK event loop
    # This allows /api/quick to be processed while this is running
    return await asyncio.to_thread(
        _do_chat_sync, gcp_token, body.query, body.session_id, body.sharepoint_only, sts_ms
    )


def _decode_jwt_payload(jwt: str) -> dict:
    """Decode JWT payload (no signature verification — display only)."""
    try:
        parts = jwt.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        # Pad base64
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return _json.loads(decoded)
    except Exception as e:
        print(f"[whoami] JWT decode error: {e}")
        return {}


@app.get("/api/whoami")
async def whoami(request: Request):
    """Identity & ACL trust strip data: username + STS validity + scope count.

    Called ONCE on auth (not per chat). Does the STS exchange to surface the
    GCP-side token expiry to the UI.
    """
    import asyncio
    token = request.headers.get("X-Entra-Id-Token")
    if not token:
        return {
            "authenticated": False,
            "username": None,
            "sts_valid_seconds": 0,
            "doc_scope_count": 0,
        }

    claims = _decode_jwt_payload(token)
    username = (
        claims.get("preferred_username")
        or claims.get("upn")
        or claims.get("email")
        or claims.get("unique_name")
        or "unknown@user"
    )

    # Exchange to get STS expiry
    def _do():
        try:
            resp = requests.post("https://sts.googleapis.com/v1/token", json={
                "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
                "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
                "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
                "scope": "https://www.googleapis.com/auth/cloud-platform",
                "subjectToken": token,
                "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
            }, timeout=10)
            if resp.ok:
                body = resp.json()
                return int(body.get("expires_in", 3600))
        except Exception as e:
            print(f"[whoami] STS error: {e}")
        return 0

    sts_valid_seconds = await asyncio.to_thread(_do)

    # Doc scope count = number of federated SharePoint connector data stores
    # We fan out to 5 entity-type datastores in the chat path.
    doc_scope_count = 5

    return {
        "authenticated": True,
        "username": username,
        "sts_valid_seconds": sts_valid_seconds,
        "doc_scope_count": doc_scope_count,
        "tenant": claims.get("tid") or "",
        "jwt_iat": claims.get("iat"),  # epoch seconds
        "jwt_exp": claims.get("exp"),  # epoch seconds
    }


# SharePoint Connector App client ID (Entra "Connector App" — see docs/SECURITY_FLOW.md)
# This is the app DE impersonates *as the user* against Microsoft Graph.
SHAREPOINT_CONNECTOR_APP_CLIENT_ID = "22c127d8-f3e5-4bbe-8b06-c37da3159068"

# Federated SharePoint connector resource path. Lives under the "sharepoint-data-def-connector"
# collection — see docs/SECURITY_FLOW.md and the chat dataStoreSpecs above.
SHAREPOINT_CONNECTOR_PATH = (
    f"projects/{PROJECT_NUMBER}/locations/global/"
    f"collections/sharepoint-data-def-connector/dataConnector"
)


@app.get("/api/connector-info")
async def connector_info(request: Request):
    """SharePoint connector metadata for the Auth Flow overlay.

    Returns the per-user site allow-list (`params.admin_filter.Site`) and the
    delegated MS Graph scopes bound to the user's refresh token. Called ONCE
    on overlay open and cached client-side.
    """
    import asyncio

    token = request.headers.get("X-Entra-Id-Token")
    gcp_token = await asyncio.to_thread(exchange_token, token) if token else None

    fallback = {
        "sites": [
            "/",
            "/sites/FinancialDocument",
            "/sites/Centura",
            "/sites/allcompany",
        ],
        "scopes": [
            "Sites.Read.All",
            "Files.Read.All",
            "Sites.Search.All",
            "AllSites.Read",
        ],
        "connector_app_client_id": SHAREPOINT_CONNECTOR_APP_CLIENT_ID,
        "source": "fallback",
    }

    if not gcp_token:
        return {**fallback, "error": "Authentication required"}

    def _do() -> dict:
        sites: list[str] = []
        scopes: list[str] = []

        # 1) GET dataConnector → admin_filter.Site list
        try:
            r = requests.get(
                f"https://discoveryengine.googleapis.com/v1alpha/{SHAREPOINT_CONNECTOR_PATH}",
                headers={"Authorization": f"Bearer {gcp_token}"},
                timeout=10,
            )
            if r.ok:
                body = r.json()
                params = body.get("params", {})
                admin_filter = params.get("admin_filter", {}) or {}
                raw_sites = admin_filter.get("Site") or admin_filter.get("site") or []
                if isinstance(raw_sites, list):
                    sites = [s for s in raw_sites if isinstance(s, str)]
            else:
                print(f"[connector-info] dataConnector GET {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[connector-info] dataConnector error: {e}")

        # 2) acquireAccessToken → returns scopes bound to the user's OAuth refresh token
        try:
            r = requests.post(
                f"https://discoveryengine.googleapis.com/v1alpha/{SHAREPOINT_CONNECTOR_PATH}:acquireAccessToken",
                headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
                json={},
                timeout=10,
            )
            if r.ok:
                body = r.json()
                # Response shape varies; try common keys
                scope_str = body.get("scope") or body.get("scopes") or ""
                if isinstance(scope_str, list):
                    scopes = [s for s in scope_str if isinstance(s, str)]
                elif isinstance(scope_str, str) and scope_str:
                    scopes = scope_str.split()
            else:
                print(f"[connector-info] acquireAccessToken {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[connector-info] acquireAccessToken error: {e}")

        return {"sites": sites, "scopes": scopes}

    live = await asyncio.to_thread(_do)

    return {
        "sites": live["sites"] or fallback["sites"],
        "scopes": live["scopes"] or fallback["scopes"],
        "connector_app_client_id": SHAREPOINT_CONNECTOR_APP_CLIENT_ID,
        "source": "live" if (live["sites"] or live["scopes"]) else "fallback",
    }


# Keep old endpoint for backwards compatibility
@app.post("/api/search")
async def search(request: Request, body: ChatRequest):
    """Alias for /api/chat for backwards compatibility."""
    return await chat(request, body)


class QuickAskRequest(BaseModel):
    query: str
    context: str = ""  # Previous conversation context


# Module-level cached credentials for /api/quick
_cached_creds = None
_cached_creds_lock = None

def _get_gcp_token_sync():
    """Get GCP token synchronously (for thread pool)."""
    import google.auth
    from google.auth.transport.requests import Request as AuthRequest
    global _cached_creds
    if _cached_creds is None:
        _cached_creds, _ = google.auth.default()
    if not _cached_creds.valid:
        _cached_creds.refresh(AuthRequest())
    return _cached_creds.token


@app.post("/api/quick")
async def quick_ask(request: Request, body: QuickAskRequest):
    """Quick response using Gemini 3.1 Flash Lite with Google Search grounding."""
    import asyncio
    import httpx

    try:
        # Run blocking auth in thread pool to avoid blocking event loop
        access_token = await asyncio.to_thread(_get_gcp_token_sync)
    except Exception as e:
        return {"answer": f"Auth error: {e}", "quick": True, "sources": []}

    # Build prompt
    prompt = body.query
    if body.context:
        prompt = f"Context:\n{body.context}\n\nQuestion: {body.query}\n\nGive a brief, helpful answer."
    else:
        prompt = f"{body.query}\n\nGive a brief, helpful answer."

    # Gemini 3.1 Flash Lite (global region) with Google Search.
    # Uses QUICK_PROJECT (ADC's own project) — PROJECT_NUMBER points at the
    # SharePoint/DE project where ADC has no aiplatform.endpoints.predict.
    url = f"https://aiplatform.googleapis.com/v1/projects/{QUICK_PROJECT}/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview:generateContent"

    # Use async httpx - won't block other requests
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.post(url,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "tools": [{"googleSearch": {}}],
                    "generationConfig": {
                        "maxOutputTokens": 500,
                        "temperature": 1,
                        "topP": 0.95
                    }
                }
            )

            if resp.status_code == 200:
                data = resp.json()
                candidate = data.get("candidates", [{}])[0]

                # Extract text from parts (may have multiple)
                parts = candidate.get("content", {}).get("parts", [])
                answer = ""
                for part in parts:
                    if part.get("text"):
                        answer += part.get("text", "")

                # Extract Google Search grounding sources
                sources = []
                grounding = candidate.get("groundingMetadata", {})
                for chunk in grounding.get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if web.get("uri") and web.get("title"):
                        sources.append({
                            "title": web.get("title", ""),
                            "url": web.get("uri", ""),
                            "snippet": ""
                        })

                if answer:
                    return {"answer": answer.strip(), "quick": True, "sources": sources[:3]}
            else:
                print(f"[Quick] API error: {resp.status_code} - {resp.text[:300]}")
        except Exception as e:
            print(f"[Quick] Error: {e}")

    return {"answer": "Quick response unavailable.", "quick": True, "sources": []}


class AgentRequest(BaseModel):
    query: str


@app.post("/api/agent")
async def agent_query(request: Request, body: AgentRequest):
    """Query the InsightComparator agent via Agent Engine SDK with Microsoft JWT."""
    try:
        import asyncio
        from agent_client import get_agent_client

        # Get Microsoft Entra ID token (NOT exchanged - agent does its own WIF exchange)
        microsoft_jwt = request.headers.get("X-Entra-Id-Token")
        user_id = "anonymous"

        if microsoft_jwt:
            user_id = "authenticated_user"
            print(f"[Agent] Passing Microsoft JWT to agent (length: {len(microsoft_jwt)})")

        client = get_agent_client()
        # Run blocking agent query in thread pool, pass Microsoft JWT for session state
        response = await asyncio.to_thread(client.query, body.query, user_id, microsoft_jwt)
        return {"answer": response, "agent": True}
    except ImportError as e:
        print(f"[Agent] Import error: {e}")
        return {"error": f"Agent module not available: {e}", "agent": True}
    except ValueError as e:
        print(f"[Agent] Config error: {e}")
        return {"error": f"Agent not configured: {e}", "agent": True}
    except Exception as e:
        print(f"[Agent] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "agent": True}


# ===== PDF Proxy (SharePoint -> browser) =====
# Cache the per-user SP access token for ~50min to avoid round-tripping
# acquireAccessToken on every page-fetch click. Keyed by (entra_jwt) so
# different users / tabs don't cross-pollinate.
import threading as _threading
_sp_token_cache: dict[str, tuple[str, float]] = {}
_sp_token_lock = _threading.Lock()


def _acquire_sp_user_token(gcp_token: str) -> str | None:
    """Call dataConnector:acquireAccessToken to get the user's SharePoint token."""
    try:
        r = requests.post(
            f"https://discoveryengine.googleapis.com/v1alpha/{SHAREPOINT_CONNECTOR_PATH}:acquireAccessToken",
            headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
            json={},
            timeout=10,
        )
        if not r.ok:
            print(f"[pdf-proxy] acquireAccessToken {r.status_code}: {r.text[:200]}")
            return None
        return r.json().get("accessToken")
    except Exception as e:
        print(f"[pdf-proxy] acquireAccessToken error: {e}")
        return None


def _parse_sp_url(sp_url: str) -> tuple[str | None, str | None]:
    """Return (site_web_url, server_relative_file_path) for a SharePoint file URL.

    Example input:
      https://sockcop.sharepoint.com/sites/allcompany/Shared%20Documents/Amgen-Product-Docs/aimovig/aimovig_pi.pdf?web=1
    Returns:
      ("https://sockcop.sharepoint.com/sites/allcompany",
       "/sites/allcompany/Shared Documents/Amgen-Product-Docs/aimovig/aimovig_pi.pdf")
    """
    from urllib.parse import urlparse, unquote
    try:
        u = urlparse(sp_url)
        if not u.netloc.endswith("sharepoint.com"):
            return None, None
        path = unquote(u.path)
        # Find the site segment (e.g., /sites/<name> or /teams/<name>)
        parts = [p for p in path.split("/") if p]
        site_url = f"https://{u.netloc}"
        if len(parts) >= 2 and parts[0] in ("sites", "teams"):
            site_url = f"https://{u.netloc}/{parts[0]}/{parts[1]}"
        # If no /sites/ or /teams/ prefix the file lives in the root web
        return site_url, path
    except Exception as e:
        print(f"[pdf-proxy] _parse_sp_url error: {e}")
        return None, None


@app.get("/api/pdf-proxy")
async def pdf_proxy(request: Request, url: str):
    """Fetch a SharePoint PDF as the calling user and stream the bytes.

    Uses Discovery Engine's `dataConnector:acquireAccessToken` to mint a
    SharePoint access token bound to the user's federated refresh token,
    then calls SP REST `GetFileByServerRelativeUrl/$value` for the binary.
    """
    import asyncio
    from fastapi import Response

    token = request.headers.get("X-Entra-Id-Token")
    if not token:
        return Response(content=b"Missing X-Entra-Id-Token", status_code=401, media_type="text/plain")

    # Token cache hit?
    now = time.time()
    sp_token = None
    with _sp_token_lock:
        cached = _sp_token_cache.get(token)
        if cached and cached[1] > now + 60:
            sp_token = cached[0]

    if not sp_token:
        gcp_token = await asyncio.to_thread(exchange_token, token)
        if not gcp_token:
            return Response(content=b"STS exchange failed", status_code=401, media_type="text/plain")
        sp_token = await asyncio.to_thread(_acquire_sp_user_token, gcp_token)
        if not sp_token:
            return Response(content=b"Could not acquire SharePoint token", status_code=502, media_type="text/plain")
        # SP tokens are typically 60min — cache for 50min
        with _sp_token_lock:
            _sp_token_cache[token] = (sp_token, now + 50 * 60)

    site_url, file_path = _parse_sp_url(url)
    if not site_url or not file_path:
        return Response(content=b"Bad SharePoint URL", status_code=400, media_type="text/plain")

    rest_url = (
        f"{site_url}/_api/web/GetFileByServerRelativeUrl('"
        f"{file_path}')/$value"
    )

    def _do_fetch():
        return requests.get(
            rest_url,
            headers={
                "Authorization": f"Bearer {sp_token}",
                "Accept": "application/pdf",
            },
            timeout=30,
        )

    r = await asyncio.to_thread(_do_fetch)
    if not r.ok:
        # Token might be stale — invalidate cache and retry once
        with _sp_token_lock:
            _sp_token_cache.pop(token, None)
        print(f"[pdf-proxy] SP fetch {r.status_code} for {rest_url[:120]}")
        return Response(content=r.content[:200] or b"SharePoint fetch failed",
                         status_code=r.status_code, media_type="text/plain")

    return Response(
        content=r.content,
        media_type="application/pdf",
        headers={
            "Content-Length": str(len(r.content)),
            "Cache-Control": "private, max-age=300",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
