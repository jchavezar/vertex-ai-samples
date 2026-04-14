"""Thin FastAPI server — all ADK logic lives in agent/agent.py."""
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.genai import types

from agent.agent import create_agent

runner = None
exit_stack = None
mcp_process = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner, exit_stack, mcp_process
    runner, exit_stack, mcp_process = await create_agent()
    yield
    if exit_stack:
        await exit_stack.aclose()
    if mcp_process:
        mcp_process.terminate()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5185"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(message: str):
    async def stream():
        try:
            await runner.session_service.create_session(
                app_name="secretops", user_id="user_1", session_id="session_1"
            )
        except Exception:
            pass

        try:
            async for event in runner.run_async(
                user_id="user_1",
                session_id="session_1",
                new_message=types.Content(role="user", parts=[types.Part(text=message)]),
            ):
                if (
                    hasattr(event, "content")
                    and event.content
                    and hasattr(event.content, "parts")
                    and event.content.parts
                ):
                    text = event.content.parts[0].text
                    if text:
                        yield f"data: {json.dumps(text)}\n\n"
                if event.is_final_response():
                    yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps(f'Error: {e}')}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
