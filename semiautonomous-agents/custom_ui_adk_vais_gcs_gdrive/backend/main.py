"""
main.py
FastAPI proxy between custom Next.js UI and the deployed Agent Engine.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import AsyncIterator

import requests
import google.auth
import google.auth.transport.requests
import vertexai
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from vertexai import agent_engines

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("backend")

# Env configuration
PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
AGENT_ENGINE_RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

vertexai.init(project=PROJECT, location=LOCATION)

app = FastAPI(title="adk-search-chatbot backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    import threading
    def load():
        try:
            log.info("Eager loading Reasoning Engine: %s", AGENT_ENGINE_RESOURCE)
            _engine()
            log.info("Reasoning Engine successfully loaded.")
        except Exception as e:
            log.error("Failed to eager load Reasoning Engine during startup: %s", e)
    threading.Thread(target=load, daemon=True).start()

_gcp_token_cache: str | None = None
_gcp_token_expiry: float = 0.0

def _get_cached_gcp_token() -> str:
    global _gcp_token_cache, _gcp_token_expiry
    # Refresh token if it is expired or about to expire in 5 minutes
    if _gcp_token_cache is None or time.time() > _gcp_token_expiry - 300:
        log.info("Fetching and caching a fresh GCP ADC token.")
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        _gcp_token_cache = creds.token
        
        # Safe parsing of credentials expiry
        if getattr(creds, "expiry", None):
            try:
                from datetime import datetime
                if isinstance(creds.expiry, datetime):
                    _gcp_token_expiry = creds.expiry.timestamp()
                else:
                    expiry_dt = datetime.fromisoformat(str(creds.expiry).replace("Z", "+00:00"))
                    _gcp_token_expiry = expiry_dt.timestamp()
            except Exception as e:
                log.warning("Failed parsing token expiry, defaulting to 55 minutes: %s", e)
                _gcp_token_expiry = time.time() + 3300
        else:
            _gcp_token_expiry = time.time() + 3300
    return _gcp_token_cache

_engine_cache: object | None = None


def _engine():
    global _engine_cache
    if _engine_cache is None:
        if not AGENT_ENGINE_RESOURCE:
            raise HTTPException(503, "AGENT_ENGINE_RESOURCE not configured on backend")
        _engine_cache = agent_engines.get(AGENT_ENGINE_RESOURCE)
    return _engine_cache


class SearchRequest(BaseModel):
    query: str
    access_token: str | None = None


@app.post("/api/datastores/search")
def search_datastores(body: SearchRequest):
    """Query Vertex AI Search (Discovery Engine) live for GDrive and GCS files."""
    try:
        # 1. Obtain GCP access credentials via ADC (with caching)
        gcp_token = _get_cached_gcp_token()
        
        # 2. Extract configuration
        # csearch-gdrive-acl_1780275206896 is located in global
        proj_number = "254356041555"
        engine_id = "csearch-gdrive-acl_1780275206896"
        location = "global"
        collection_id = "default_collection"
        
        api_url = (
            f"https://discoveryengine.googleapis.com/v1alpha"
            f"/projects/{proj_number}/locations/{location}"
            f"/collections/{collection_id}/engines/{engine_id}"
            f"/servingConfigs/default_search:search"
        )
        
        # Use client-side Google Workspace OAuth token if provided, falling back to Service Account (GCS only)
        token_to_use = body.access_token if body.access_token else gcp_token
        
        headers = {
            "Authorization": f"Bearer {token_to_use}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": proj_number,
        }
        
        # Build search body
        request_body = {
            "query": body.query or "",
            "pageSize": 20,
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {
                "snippetSpec": {"returnSnippet": True}
            }
        }
        
        log.info("Sending Search request to Discovery Engine for query: %s (using %s token)", 
                 body.query, "user OAuth" if body.access_token else "GCP service account")
        response = requests.post(api_url, headers=headers, json=request_body)
        
        log.info("Discovery Engine API search response status: %s", response.status_code)
        
        if response.status_code != 200:
            log.error("Discovery Engine API search failed: %s - %s", response.status_code, response.text)
            return {"results": []}
            
        data = response.json()
        raw_results = data.get("results", [])
        log.info("Discovery Engine returned %s raw search results", len(raw_results))
        if not raw_results:
            log.info("Raw response from Discovery Engine: %s", json.dumps(data)[:500])
        
        parsed_results = []
        for i, item in enumerate(raw_results):
            doc = item.get("document", {})
            doc_id = doc.get("id", f"doc-{i}")
            derived_data = doc.get("derivedStructData", {})
            
            # Extract fields with safe fallbacks
            name = derived_data.get("title") or doc.get("name", "").split("/")[-1] or f"File {i}"
            link = derived_data.get("link") or f"https://drive.google.com/open?id={doc_id}"
            mime_type = derived_data.get("mimeType") or "application/octet-stream"
            
            # Extract snippet
            snippet = ""
            snippets_list = derived_data.get("snippets", [])
            if snippets_list and isinstance(snippets_list, list):
                snippet = snippets_list[0].get("snippet", "")
            if not snippet:
                snippet = "No direct preview snippet available from Discovery Engine indexing."
                
            owner = "Enterprise System"
            owner_email = "sys@vtxdemos.com"
            modified_time = "Recently synchronized"
            file_size = "N/A"
            
            # Try to get more metadata if available
            if "owner" in derived_data:
                owner = derived_data["owner"]
            if "ownerEmail" in derived_data:
                owner_email = derived_data["ownerEmail"]
            if "modifiedTime" in derived_data:
                modified_time = derived_data["modifiedTime"]
            if "fileSize" in derived_data:
                fs = derived_data["fileSize"]
                try:
                    file_size = f"{int(fs) // 1024} KB" if int(fs) > 1024 else f"{fs} B"
                except Exception:
                    file_size = str(fs)
            
            # GCS link conversion: gs:// to https://storage.cloud.google.com/
            if link.startswith("gs://"):
                parts = link[5:].split("/", 1)
                if len(parts) == 2:
                    bucket_name, object_name = parts
                    link = f"https://storage.cloud.google.com/{bucket_name}/{object_name}"
            
            parsed_results.append({
                "id": doc_id,
                "name": name,
                "mimeType": mime_type,
                "source": "Vertex AI Search (Drive)" if "drive" in link or "google" in link else "Vertex AI Search (GCS)",
                "owner": owner,
                "ownerEmail": owner_email,
                "modifiedTime": modified_time,
                "link": link,
                "fileSize": file_size,
                "telemetrySummary": f"Aura Telemetry Loaded: Metadata successfully retrieved from active Google Drive Datastore sync.",
                "snippet": snippet
            })
            
        return {"results": parsed_results}
        
    except Exception as e:
        log.exception("Error querying Discovery Engine Search API")
        return {"results": []}


class ChatRequest(BaseModel):
    message: str
    access_token: str
    user_id: str = Field(default="anon")
    session_id: str | None = None
    thinking_level: str | None = None
    model: str | None = None


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "agent_engine_configured": bool(AGENT_ENGINE_RESOURCE),
        "project": PROJECT,
        "location": LOCATION,
    }


@app.post("/api/session")
def create_session(body: ChatRequest):
    """Create a new Agent Engine session or loads/configures an existing one."""
    engine = _engine()
    
    # Store access token in session state for Drive datastore auth
    state = {
        "temp:drive_access_token": body.access_token, 
        "drive_access_token": body.access_token
    }
    if body.thinking_level:
        state["thinking_level"] = body.thinking_level
        state["temp:thinking_level"] = body.thinking_level
        
    session = engine.create_session(user_id=body.user_id, state=state)
    sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", None)
    log.info("Initialized session %s for user=%s", sid, body.user_id)
    return {"session_id": sid, "user_id": body.user_id}


def _serialize_event(event) -> dict:
    """Normalize stream_query events into UI-friendly payloads."""
    if isinstance(event, dict):
        ev = event
    else:
        try:
            ev = event.model_dump()
        except Exception:
            ev = {"raw": str(event)}

    out = {"type": "event", "raw": ev}
    content = ev.get("content") if isinstance(ev, dict) else None
    
    # Expose token flow or thoughts if they are in usage_metadata
    usage = ev.get("usage_metadata") if isinstance(ev, dict) else None
    if isinstance(usage, dict):
        out["usage_metadata"] = {
            "prompt_token_count": usage.get("prompt_token_count"),
            "candidates_token_count": usage.get("candidates_token_count"),
            "total_token_count": usage.get("total_token_count"),
            "thoughts_token_count": usage.get("thoughts_token_count"),
        }

    if isinstance(content, dict):
        for part in content.get("parts", []) or []:
            if not isinstance(part, dict):
                continue
            # Handle standard model output
            if part.get("text") and not part.get("thought"):
                out.setdefault("text", "")
                out["text"] += part["text"]
            # Handle thoughts/reasoning blocks
            if part.get("thought") or (part.get("text") and part.get("thought") is True):
                out.setdefault("thought", "")
                out["thought"] += part.get("text") or ""
            # Grounding results / standard function-calls
            if part.get("function_call"):
                out["tool_call"] = {
                    "name": part["function_call"].get("name"),
                    "args": part["function_call"].get("args"),
                }
            if part.get("function_response"):
                fr = part["function_response"]
                out["tool_result"] = {
                    "name": fr.get("name"), 
                    "preview": json.dumps(fr.get("response", {}))[:200] + "...",
                    "response": fr.get("response", {})
                }
    return out


async def _sse_stream(
    user_id: str,
    session_id: str,
    message: str,
    access_token: str | None = None,
    thinking_level: str | None = None,
    model: str | None = None,
) -> AsyncIterator[bytes]:
    engine = _engine()
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    SENTINEL = object()

    def producer():
        try:
            msg_to_send = message
            if access_token:
                msg_to_send = f"[ACCESS_TOKEN:{access_token}] {msg_to_send}"
            if thinking_level:
                msg_to_send = f"[THINKING_LEVEL:{thinking_level}] {msg_to_send}"
            if model:
                msg_to_send = f"[MODEL_NAME:{model}] {msg_to_send}"
                
            for event in engine.stream_query(
                user_id=user_id,
                session_id=session_id,
                message=msg_to_send,
            ):
                loop.call_soon_threadsafe(queue.put_nowait, event)
        except Exception as e:
            log.exception("Exception in producer stream_query")
            loop.call_soon_threadsafe(queue.put_nowait, {"_error": str(e)})
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, SENTINEL)

    asyncio.get_event_loop().run_in_executor(None, producer)

    while True:
        item = await queue.get()
        if item is SENTINEL:
            yield b"event: done\ndata: {}\n\n"
            return
        if isinstance(item, dict) and "_error" in item:
            payload = {"type": "error", "error": item["_error"]}
            yield f"data: {json.dumps(payload)}\n\n".encode()
            yield b"event: done\ndata: {}\n\n"
            return
        payload = _serialize_event(item)
        yield f"data: {json.dumps(payload)}\n\n".encode()


@app.post("/api/chat")
async def chat(body: ChatRequest):
    if not body.session_id:
        raise HTTPException(400, "session_id is required")
        
    log.info("Streaming query with thinking level %s and model %s for session=%s user=%s", body.thinking_level or "unspecified", body.model or "unspecified", body.session_id, body.user_id)
    return StreamingResponse(
        _sse_stream(
            user_id=body.user_id,
            session_id=body.session_id,
            message=body.message,
            access_token=body.access_token,
            thinking_level=body.thinking_level,
            model=body.model,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


