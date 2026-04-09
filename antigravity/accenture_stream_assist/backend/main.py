import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

from agent.tools.discovery_engine import DiscoveryEngineClient

app = FastAPI(title="Accenture Stream Assist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("stream_assist_api")
logging.basicConfig(level=logging.INFO)

de_client = DiscoveryEngineClient()

class SearchRequest(BaseModel):
    query: str

@app.post("/api/search")
async def search_stream_assist(request: Request, body: SearchRequest):
    # Extract optional token
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
    logger.info(f"Received search query: {body.query}")
    try:
        result = await de_client.search(query=body.query, user_token=token)
        return {
            "answer": result.answer,
            "sources": [{"title": s.title, "url": s.url, "snippet": s.snippet} for s in result.sources]
        }
    except Exception as e:
        logger.error(f"Search API Error: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
