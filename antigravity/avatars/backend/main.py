import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.adk as adk
from google.adk.models import BaseLlm, LlmRequest, LlmResponse, LLMRegistry
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from typing import AsyncGenerator
from dotenv import load_dotenv

from pathlib import Path

# Load .env from root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK (kept for future use if needed, or can be removed if strictly following 'remove summary')
# session_service = InMemorySessionService()

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
