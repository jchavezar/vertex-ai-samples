
import os
import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv

from utils.discovery_engine import DiscoveryEngineClient
from mcp_service.mcp_sharepoint import SharePointMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AccentureUnifiedBackend")

app = FastAPI(title="Accenture SharePoint Synthesis Hub")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Clients
# We assume env vars are set for these
de_client = DiscoveryEngineClient()
genai_client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")

# Models
class SearchRequest(BaseModel):
    query: str

class ModificationRequest(BaseModel):
    item_id: str
    prompt: str

class CommitRequest(BaseModel):
    item_id: str
    content: str

# Helper to extract token from request
def get_auth_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

# --- SEARCH ENDPOINTS ---

@app.post("/api/search")
async def unified_search(request: Request, search_req: SearchRequest):
    """
    Unified Grounded Search using Discovery Engine and SharePoint Datastores.
    Executes WIF token exchange if Entra ID token is provided.
    """
    logger.info(f"Unified Search triggered for query: {search_req.query}")
    
    # Try to get Entra ID token for WIF exchange
    user_token = request.headers.get("X-Entra-Id-Token")
    if user_token == "null" or user_token == "undefined":
         user_token = None

    try:
        result = await de_client.search(search_req.query, user_token=user_token)
        return {
            "answer": result.answer,
            "sources": [
                {
                    "title": src.title,
                    "url": src.url,
                    "snippet": src.snippet
                } for src in result.sources
            ]
        }
    except Exception as e:
        logger.exception(f"Search failed: {e}")
        return {"error": str(e), "answer": "Synthesized search failed.", "sources": []}

@app.post("/api/search/stream")
async def unified_search_stream(request: Request, search_req: SearchRequest):
    """
    Streaming version of unified search.
    Expects POST with { "query": "..." } and headers.
    """
    user_token = request.headers.get("X-Entra-Id-Token")
    if user_token == "null" or user_token == "undefined":
         user_token = None

    async def sse_generator():
        try:
            async for chunk in de_client.stream_search(search_req.query, user_token=user_token):
                yield {"event": "message", "data": json.dumps({"text": chunk})}
            yield {"event": "done", "data": "[DONE]"}
        except Exception as e:
            logger.exception(f"Stream search failed: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(sse_generator())

# --- SHAREPOINT ACTION ENDPOINTS ---

@app.get("/api/sharepoint/list")
async def list_sharepoint_folder(request: Request, folder_id: str = "root"):
    """Lists files and folders in the target SharePoint share."""
    token = get_auth_token(request)
    try:
        sp = SharePointMCP(token=token)
        items = sp.list_folder_contents(folder_id)
        return {"items": items}
    except Exception as e:
        logger.exception("Failed to list folder")
        return {"error": str(e)}

@app.get("/api/sharepoint/content")
async def get_sharepoint_content(request: Request, item_id: str):
    """Fetches and converts document content to text/markdown."""
    token = get_auth_token(request)
    try:
         sp = SharePointMCP(token=token)
         content = sp.get_document_content(item_id)
         return {"content": content}
    except Exception as e:
         logger.exception("Failed to get content")
         return {"error": str(e)}

@app.get("/api/sharepoint/preview_url")
async def get_sharepoint_preview_url(request: Request, item_id: str):
    """Generates an embeddable preview URL."""
    token = get_auth_token(request)
    try:
         sp = SharePointMCP(token=token)
         preview_url = sp.get_preview_url(item_id)
         return {"preview_url": preview_url}
    except Exception as e:
         logger.exception("Failed to get preview URL")
         return {"error": str(e)}

@app.post("/api/sharepoint/propose_modification")
async def propose_modification(request: Request, data: ModificationRequest):
    """
    Uses Gemini to propose edits to a document based on user prompt.
    Simplified text-only flow.
    """
    token = get_auth_token(request)
    try:
        sp = SharePointMCP(token=token)
        content = sp.get_document_content(data.item_id)
        
        # Use simple text rewrite instruction with GenAI SDK
        model_id = "gemini-2.5-pro" # Using Pro for better compliance with rewrite rules
        system_prompt = (
            "You are a professional enterprise document editor. "
            "Modify the provided document content based on the user's instructions. "
            "Return ONLY the fully modified content. Do not include any meta-talk, explanations, or backticks unless they are part of the document."
        )
        user_msg = f"DOCUMENT CONTENT:\n{content}\n\nUSER MODIFICATION PROMPT: {data.prompt}"
        
        response = genai_client.models.generate_content(
            model=model_id,
            contents=user_msg,
            config=types.GenerateContentConfig(system_instruction=system_prompt)
        )
        return {"modified_content": response.text}
    except Exception as e:
        logger.exception("Propose modification failed")
        return {"error": str(e)}

@app.post("/api/sharepoint/commit_modification")
async def commit_modification(request: Request, data: CommitRequest):
    """Commit the modified content back to SharePoint (with auto-backup)."""
    token = get_auth_token(request)
    try:
        sp = SharePointMCP(token=token)
        result = sp.update_document_content(data.item_id, data.content)
        return {"status": "success", "result": result}
    except Exception as e:
         logger.exception("Commit failed")
         return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use standard port 8000 for visibility
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
