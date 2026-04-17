import os
import json
import logging
import vertexai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from vertexai import agent_engines
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(__file__), "..", "..", "agent", ".env")
load_dotenv(dotenv_path=_env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Observability Orchestra UI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID", "5346318665211969536")

vertexai.init(project=PROJECT_ID, location=LOCATION)

_agent = None

def get_agent():
    global _agent
    if _agent is None:
        logger.info(f"Connecting to Agent Engine: {AGENT_ENGINE_ID}")
        _agent = agent_engines.get(AGENT_ENGINE_ID)
        logger.info("Connected successfully")
    return _agent


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "ui-user"


@app.get("/health")
async def health():
    return {"status": "ok", "agent_engine_id": AGENT_ENGINE_ID}


@app.post("/api/session")
async def create_session():
    try:
        agent = get_agent()
        session = agent.create_session(user_id="ui-user")
        session_id = session.get("id") if isinstance(session, dict) else session.id
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        return {"error": str(e)}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    async def sse_generator():
        try:
            agent = get_agent()

            session_id = request.session_id
            if not session_id:
                session = agent.create_session(user_id=request.user_id)
                session_id = session.get("id") if isinstance(session, dict) else session.id
                yield {"data": json.dumps({"type": "session", "session_id": session_id})}

            current_author = None
            for event in agent.stream_query(
                user_id=request.user_id,
                session_id=session_id,
                message=request.message,
            ):
                author = None
                text = None

                if isinstance(event, dict):
                    author = event.get("author")
                    content = event.get("content", {})
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, dict) and part.get("text"):
                            text = part["text"]
                elif hasattr(event, "author"):
                    author = event.author
                    if hasattr(event, "content") and hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                text = part.text

                if author and author != current_author:
                    current_author = author
                    yield {"data": json.dumps({"type": "agent_switch", "agent": author})}

                if text:
                    yield {"data": json.dumps({"type": "chunk", "text": text, "agent": current_author or "assistant"})}

            yield {"data": json.dumps({"type": "done"})}

        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield {"data": json.dumps({"type": "error", "message": str(e)})}

    return EventSourceResponse(sse_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True)
else:
    from fastapi.staticfiles import StaticFiles
    import mimetypes
    mimetypes.add_type("application/javascript", ".js")
    dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
    if os.path.exists(dist):
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
        logger.info(f"Serving frontend from {dist}")
