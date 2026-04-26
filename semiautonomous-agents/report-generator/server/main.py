"""FastAPI server for the report-generator UI.

Endpoints:
- GET  /                         - serves ui/index.html
- GET  /api/agent-graph          - JSON topology for the diagram
- POST /api/intake               - SSE stream of intake-agent turns
- POST /api/generate             - SSE stream of pipeline progress + final paths
- GET  /api/files/{name}         - downloads a generated PDF/DOCX
- POST /api/ms365-upload         - on-demand upload of the latest .docx to OneDrive

The main pipeline runs in-process; no separate worker.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sse_starlette.sse import EventSourceResponse

from agent.agent import root_agent
from agent.intake import intake_agent
from agent.schemas import ReportBrief

from .graph import agent_to_graph

load_dotenv(override=True)

ROOT_DIR = Path(__file__).resolve().parents[1]
UI_DIR = ROOT_DIR / "ui"
OUTPUTS_DIR = Path(os.environ.get("REPORT_OUTPUT_DIR", ROOT_DIR / "outputs"))
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "report-generator"

app = FastAPI(title="Report Generator")

if (UI_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")


# --- Sessions -----------------------------------------------------------------

_session_service = InMemorySessionService()
_intake_runner = Runner(
    app_name=APP_NAME,
    agent=intake_agent,
    session_service=_session_service,
)
_pipeline_runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=_session_service,
)


def _user_id_from(request: Request) -> str:
    return request.headers.get("x-user-id", "anon")


async def _get_or_create_session(user_id: str, session_id: str | None) -> str:
    if session_id:
        existing = await _session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if existing is not None:
            return session_id
    new_id = session_id or uuid.uuid4().hex
    await _session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=new_id
    )
    return new_id


# --- Static UI ----------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    index_html = UI_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(404, "ui/index.html missing")
    return HTMLResponse(index_html.read_text())


# --- Agent topology -----------------------------------------------------------

@app.get("/api/agent-graph")
async def agent_graph() -> JSONResponse:
    return JSONResponse(agent_to_graph(root_agent))


# --- Intake (conversational) --------------------------------------------------

_BRIEF_FENCE_RE = re.compile(
    r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE
)


def _try_extract_brief(text: str) -> dict[str, Any] | None:
    m = _BRIEF_FENCE_RE.search(text or "")
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
        ReportBrief.model_validate(data)  # validate but return raw dict
        return data
    except (json.JSONDecodeError, ValueError):
        return None


@app.post("/api/intake")
async def intake(request: Request) -> EventSourceResponse:
    body = await request.json()
    message = (body.get("message") or "").strip()
    user_id = _user_id_from(request)
    session_id = await _get_or_create_session(user_id, body.get("session_id"))

    if not message:
        raise HTTPException(400, "message required")

    async def stream() -> AsyncGenerator[dict[str, Any], None]:
        yield {"event": "session", "data": json.dumps({"session_id": session_id})}
        accumulated = ""
        content = Content(role="user", parts=[Part(text=message)])
        try:
            async for ev in _intake_runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                if ev.content and ev.content.parts:
                    for part in ev.content.parts:
                        if part.text:
                            accumulated += part.text
                            yield {
                                "event": "token",
                                "data": json.dumps(
                                    {"author": ev.author, "text": part.text}
                                ),
                            }
            brief = _try_extract_brief(accumulated)
            if brief is not None:
                yield {"event": "brief", "data": json.dumps(brief)}
            yield {"event": "done", "data": "{}"}
        except Exception as e:  # noqa: BLE001
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(stream())


# --- Generation pipeline ------------------------------------------------------

def _format_topic_message(brief: dict[str, Any]) -> str:
    visuals = ", ".join(brief.get("visuals") or []) or "default"
    formats = ", ".join(brief.get("formats") or ["pdf", "docx"])
    return (
        f"Topic: {brief.get('topic')}\n"
        f"Audience: {brief.get('audience','general technical reader')}\n"
        f"Angle: {brief.get('angle','')}\n"
        f"Length: {brief.get('length','standard')}\n"
        f"Tone: {brief.get('tone','analytical')}\n"
        f"Preferred visual blocks: {visuals}\n"
        f"Output formats: {formats}\n"
        f"Notes: {brief.get('notes','')}"
    )


_HEARTBEAT_INTERVAL = 2.0


async def _run_pipeline_with_heartbeat(
    user_id: str, session_id: str, content: Content
) -> AsyncGenerator[dict[str, Any], None]:
    """Merge ADK pipeline events with periodic heartbeats.

    ADK's runner can be silent for 10-30s between agent stages (Gemini
    latency); the heartbeat keeps the SSE connection alive and tells the
    client which stage is still running and for how long.
    """
    import time

    queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    t0 = time.monotonic()

    async def runner_task() -> None:
        try:
            async for ev in _pipeline_runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                payload: dict[str, Any] = {"author": ev.author or "agent"}
                if ev.content and ev.content.parts:
                    text_chunks = [p.text for p in ev.content.parts if p.text]
                    if text_chunks:
                        payload["text"] = "".join(text_chunks)
                await queue.put({"kind": "agent", "payload": payload})
        except Exception as e:  # noqa: BLE001
            import traceback
            await queue.put({
                "kind": "error",
                "payload": {"error": str(e), "trace": traceback.format_exc()},
            })
        finally:
            await queue.put(None)  # sentinel: pipeline finished

    async def heartbeat_task() -> None:
        while True:
            await asyncio.sleep(_HEARTBEAT_INTERVAL)
            await queue.put({
                "kind": "heartbeat",
                "payload": {"elapsed_s": round(time.monotonic() - t0, 1)},
            })

    runner = asyncio.create_task(runner_task())
    beat = asyncio.create_task(heartbeat_task())

    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            yield {"event": item["kind"], "data": json.dumps(item["payload"])}
    finally:
        beat.cancel()
        if not runner.done():
            runner.cancel()
        try:
            await runner
        except (asyncio.CancelledError, Exception):
            pass


@app.post("/api/generate")
async def generate(request: Request) -> EventSourceResponse:
    body = await request.json()
    brief = body.get("brief")
    user_id = _user_id_from(request)
    if not brief or not brief.get("topic"):
        raise HTTPException(400, "brief.topic required")

    # Validate (and normalise) the brief.
    brief = ReportBrief.model_validate(brief).model_dump()
    session_id = uuid.uuid4().hex
    await _session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id,
        state={"brief": brief},
    )

    async def stream() -> AsyncGenerator[dict[str, Any], None]:
        yield {"event": "session", "data": json.dumps({"session_id": session_id})}
        yield {"event": "graph", "data": json.dumps(agent_to_graph(root_agent))}

        content = Content(role="user", parts=[Part(text=_format_topic_message(brief))])
        async for evt in _run_pipeline_with_heartbeat(user_id, session_id, content):
            yield evt

        session = await _session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        state = session.state if session else {}
        result = {
            "pdf_path": state.get("pdf_path"),
            "docx_path": state.get("docx_path"),
            "pdf_name": Path(state["pdf_path"]).name if state.get("pdf_path") else None,
            "docx_name": Path(state["docx_path"]).name if state.get("docx_path") else None,
        }
        yield {"event": "result", "data": json.dumps(result)}
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(stream())


# --- File serving -------------------------------------------------------------

@app.get("/api/files/{name}")
async def get_file(name: str) -> FileResponse:
    # Prevent path traversal — only serve files inside OUTPUTS_DIR.
    safe_name = Path(name).name
    candidate = (OUTPUTS_DIR / safe_name).resolve()
    if not candidate.is_file() or OUTPUTS_DIR.resolve() not in candidate.parents:
        raise HTTPException(404, "not found")
    return FileResponse(str(candidate), filename=safe_name)


# --- MS365 OneDrive upload (on-demand, separate from pipeline) ---------------

MS365_MCP_URL = os.environ.get("MS365_MCP_URL", "http://localhost:8080/mcp")
_URL_RE = re.compile(r"https?://[^\s\"'<>)]+")


def _parse_mcp_response(text: str) -> dict[str, Any]:
    """MCP responses arrive as either plain JSON or an SSE-framed JSON line."""
    text = text.strip()
    if text.startswith("event:"):
        for line in text.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def _mcp_text(parsed: dict[str, Any]) -> str:
    """Extract the textual content from an MCP tools/call result."""
    result = parsed.get("result") or {}
    for c in result.get("content", []):
        if c.get("type") == "text":
            return c.get("text", "")
    sc = result.get("structuredContent") or {}
    return sc.get("result") or json.dumps(result)[:600]


async def _mcp_session(client: httpx.AsyncClient) -> dict[str, str]:
    base = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    init = {
        "jsonrpc": "2.0", "id": "init", "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "report-generator", "version": "0.1"},
        },
    }
    r = await client.post(MS365_MCP_URL, json=init, headers=base)
    sid = r.headers.get("mcp-session-id")
    if not sid:
        raise HTTPException(502, f"MCP init failed: {r.status_code} {r.text[:200]}")
    headers = {**base, "mcp-session-id": sid}
    await client.post(
        MS365_MCP_URL,
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=headers,
    )
    return headers


async def _mcp_call(
    client: httpx.AsyncClient, headers: dict[str, str], tool: str, arguments: dict
) -> dict[str, Any]:
    payload = {
        "jsonrpc": "2.0", "id": uuid.uuid4().hex, "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    r = await client.post(MS365_MCP_URL, json=payload, headers=headers, timeout=120)
    if r.status_code >= 400:
        raise HTTPException(502, f"MCP {tool} failed: {r.status_code} {r.text[:300]}")
    return _parse_mcp_response(r.text)


def _extract_web_url(listing_text: str, filename: str) -> str | None:
    """Find the OneDrive webUrl for `filename` inside a free-form listing."""
    try:
        parsed = json.loads(listing_text)
        items = parsed if isinstance(parsed, list) else parsed.get("value") or parsed.get("items") or []
        for it in items:
            if isinstance(it, dict) and it.get("name") == filename:
                return it.get("webUrl") or it.get("web_url") or it.get("url")
    except (json.JSONDecodeError, TypeError):
        pass
    lines = listing_text.splitlines()
    for i, line in enumerate(lines):
        if filename in line:
            for probe in lines[max(0, i - 1): i + 4]:
                m = _URL_RE.search(probe)
                if m:
                    return m.group(0)
    m = _URL_RE.search(listing_text)
    return m.group(0) if m else None


@app.post("/api/ms365-upload")
async def ms365_upload(request: Request) -> JSONResponse:
    """Upload a generated file to OneDrive via the ms365 MCP server, then return its webUrl.

    Body: { "filename": "<name>.docx", "remote_folder": "/Reports" }
    Kept OUT of the main pipeline so it never adds latency to generation.
    """
    body = await request.json()
    filename = body.get("filename")
    remote_folder = body.get("remote_folder", "/Reports")
    if not filename:
        raise HTTPException(400, "filename required")
    safe = (OUTPUTS_DIR / Path(filename).name).resolve()
    if not safe.is_file():
        raise HTTPException(404, "file not found")

    import base64
    content_b64 = base64.b64encode(safe.read_bytes()).decode()

    async with httpx.AsyncClient(timeout=120.0) as client:
        headers = await _mcp_session(client)

        upload = await _mcp_call(client, headers, "sp_upload_file", {
            "drive_id": "me",
            "folder_path": remote_folder,
            "file_name": safe.name,
            "content": content_b64,
            "is_base64": True,
        })
        upload_text = _mcp_text(upload)
        if "Not logged in" in upload_text or upload_text.startswith("Error"):
            return JSONResponse(
                {
                    "ok": False,
                    "message": upload_text,
                    "hint": (
                        "MS365 not authenticated. From any Claude Code session with the ms365 MCP, "
                        "run ms365_login (visit https://login.microsoft.com/device with the device code), "
                        "then ms365_complete_login. Then click upload again."
                    ),
                },
                status_code=401 if "Not logged in" in upload_text else 502,
            )

        # Prefer the URL inside the upload response itself; fall back to listing.
        web_url = _extract_web_url(upload_text, safe.name)
        if not web_url:
            listing = await _mcp_call(client, headers, "onedrive_list_files", {
                "folder_path": remote_folder, "limit": 200,
            })
            web_url = _extract_web_url(_mcp_text(listing), safe.name)

    return JSONResponse({
        "ok": True,
        "filename": safe.name,
        "folder": remote_folder,
        "web_url": web_url,
        "upload_message": upload_text,
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8775")),
        reload=False,
    )
