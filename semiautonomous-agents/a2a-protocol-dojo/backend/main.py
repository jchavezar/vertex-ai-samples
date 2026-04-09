"""
A2A Protocol Dojo — Backend Gateway.

Serves lesson content and proxies A2A calls to demo agents.
Port: 8000
"""

import asyncio
import json
import os
import uuid
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="A2A Protocol Dojo Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LESSONS_DIR = Path(__file__).parent / "lessons"
ALLOWED_PORTS = {8001, 8002}
AGENT_NAMES = {8001: "Echo Agent", 8002: "Gemini Agent"}


def parse_lesson(filepath: Path) -> dict:
    """Parse lesson markdown with YAML frontmatter."""
    text = filepath.read_text()
    if text.startswith("---"):
        _, fm, content = text.split("---", 2)
        meta = yaml.safe_load(fm)
        meta["content"] = content.strip()
    else:
        meta = {"title": filepath.stem, "content": text}
    return meta


@app.get("/api/lessons")
def list_lessons():
    lessons = []
    for f in sorted(LESSONS_DIR.glob("*.md")):
        meta = parse_lesson(f)
        lesson_id = int(f.stem.split("_")[0])
        lessons.append({
            "id": lesson_id,
            "title": meta.get("title", f.stem),
            "description": meta.get("description", ""),
            "hasDemo": meta.get("hasDemo", False),
            "demoComponent": meta.get("demoComponent"),
        })
    return lessons


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: int):
    for f in LESSONS_DIR.glob(f"{lesson_id:02d}_*.md"):
        meta = parse_lesson(f)
        return {
            "id": lesson_id,
            "title": meta.get("title", f.stem),
            "description": meta.get("description", ""),
            "hasDemo": meta.get("hasDemo", False),
            "demoComponent": meta.get("demoComponent"),
            "content": meta.get("content", ""),
        }
    raise HTTPException(404, f"Lesson {lesson_id} not found")


def _validate_port(port: int):
    if port not in ALLOWED_PORTS:
        raise HTTPException(400, f"Port {port} not allowed. Use {ALLOWED_PORTS}")


@app.get("/api/agents")
async def list_agents():
    agents = []
    async with httpx.AsyncClient(timeout=2) as client:
        for port in ALLOWED_PORTS:
            healthy = False
            card = None
            try:
                r = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
                if r.status_code == 200:
                    healthy = True
                    card = r.json()
            except Exception:
                pass
            agents.append({
                "port": port,
                "name": AGENT_NAMES.get(port, f"Agent:{port}"),
                "healthy": healthy,
                "card": card,
            })
    return agents


@app.get("/api/agents/{port}/card")
async def get_agent_card(port: int):
    _validate_port(port)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
            return r.json()
    except Exception as e:
        raise HTTPException(503, f"Agent on port {port} not reachable: {e}")


@app.get("/api/agents/{port}/health")
async def agent_health(port: int):
    _validate_port(port)
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
            return {"healthy": r.status_code == 200}
    except Exception:
        return {"healthy": False}


class SendMessageBody(BaseModel):
    message: str


@app.post("/api/agents/{port}/send")
async def send_message(port: int, body: SendMessageBody):
    _validate_port(port)
    msg_id = str(uuid.uuid4())
    jsonrpc_payload = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": body.message}],
                "messageId": msg_id,
            }
        },
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"http://localhost:{port}/",
                json=jsonrpc_payload,
            )
            return {"request": jsonrpc_payload, "response": r.json()}
    except Exception as e:
        raise HTTPException(503, f"Agent on port {port} not reachable: {e}")


@app.post("/api/agents/{port}/stream")
async def stream_message(port: int, body: SendMessageBody):
    _validate_port(port)
    msg_id = str(uuid.uuid4())
    jsonrpc_payload = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "message/stream",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": body.message}],
                "messageId": msg_id,
            }
        },
    }

    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream(
                    "POST",
                    f"http://localhost:{port}/",
                    json=jsonrpc_payload,
                    headers={"Accept": "text/event-stream"},
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n"
                        else:
                            yield "\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/demo/task-lifecycle")
async def demo_task_lifecycle():
    """Simulate A2A task lifecycle for lesson 3 demo."""
    task_id = str(uuid.uuid4())

    async def lifecycle_events():
        # Submitted
        yield f"data: {json.dumps({'state': 'submitted', 'taskId': task_id, 'timestamp': 0})}\n\n"
        await asyncio.sleep(1)

        # Working
        yield f"data: {json.dumps({'state': 'working', 'taskId': task_id, 'timestamp': 1})}\n\n"
        await asyncio.sleep(2)

        # Completed
        yield f"data: {json.dumps({'state': 'completed', 'taskId': task_id, 'timestamp': 3, 'artifact': 'Task finished successfully!'})}\n\n"

    return StreamingResponse(
        lifecycle_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.post("/api/demo/orchestration")
async def demo_orchestration(body: SendMessageBody):
    """Demo multi-agent orchestration for lesson 7."""
    async def orchestration_events():
        # Step 1: Discovery
        yield f"data: {json.dumps({'step': 'discovery', 'message': 'Discovering available agents...'})}\n\n"
        await asyncio.sleep(0.5)

        agents_found = []
        async with httpx.AsyncClient(timeout=3) as client:
            for port in ALLOWED_PORTS:
                try:
                    r = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
                    if r.status_code == 200:
                        card = r.json()
                        agents_found.append({"port": port, "name": card.get("name", f"agent:{port}")})
                except Exception:
                    pass

        yield f"data: {json.dumps({'step': 'agents_found', 'agents': agents_found})}\n\n"
        await asyncio.sleep(0.5)

        # Step 2: Delegate to each agent
        results = []
        for agent in agents_found:
            yield f"data: {json.dumps({'step': 'delegating', 'agent': agent['name'], 'port': agent['port']})}\n\n"
            msg_id = str(uuid.uuid4())
            payload = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": body.message}],
                        "messageId": msg_id,
                    }
                },
            }
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.post(f"http://localhost:{agent['port']}/", json=payload)
                    resp = r.json()
                    result_data = resp.get("result", {})
                    artifacts = result_data.get("artifacts", [])
                    text = ""
                    for art in artifacts:
                        for part in art.get("parts", []):
                            text += part.get("text", "")
                    results.append({"agent": agent["name"], "response": text or "(no text)"})
            except Exception as e:
                results.append({"agent": agent["name"], "response": f"Error: {e}"})

            yield f"data: {json.dumps({'step': 'result', 'agent': agent['name'], 'response': results[-1]['response']})}\n\n"
            await asyncio.sleep(0.3)

        # Step 3: Aggregate
        yield f"data: {json.dumps({'step': 'complete', 'results': results})}\n\n"

    return StreamingResponse(
        orchestration_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
