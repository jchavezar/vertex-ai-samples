"""
StreamAssist Chat API with multi-turn conversation support.
Uses Discovery Engine sessions for conversation continuity.
"""
import os
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


def extract_sources(data) -> List[dict]:
    """Extract grounding sources from streamAssist response."""
    sources = []
    seen = set()

    def find_sources(obj, path=""):
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                find_sources(item, f"{path}[{i}]")
        elif isinstance(obj, dict):
            # Log keys at this level for debugging
            if any(k in obj for k in ["groundingMetadata", "textGroundingMetadata", "searchResults", "citations", "references"]):
                print(f"[DEBUG SOURCES] Found potential source keys at {path}: {list(obj.keys())}")

            # Pattern 1: textGroundingMetadata (first query)
            if "textGroundingMetadata" in obj:
                for ref in obj["textGroundingMetadata"].get("references", []):
                    doc = ref.get("documentMetadata", {})
                    title = doc.get("title", "Document")
                    url = doc.get("uri", "#")
                    snippet = ref.get("content", "")[:200]
                    key = f"{title}-{url}"
                    if key not in seen and title and title != "Document":
                        seen.add(key)
                        sources.append({"title": title, "url": url, "snippet": snippet})

            # Pattern 2: groundingMetadata
            if "groundingMetadata" in obj:
                gm = obj["groundingMetadata"]
                # groundingChunks
                for chunk in gm.get("groundingChunks", []):
                    ctx = chunk.get("retrievedContext", {})
                    title = ctx.get("title", "")
                    url = ctx.get("uri", "#")
                    snippet = ctx.get("text", "")[:200]
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen.add(key)
                        sources.append({"title": title, "url": url, "snippet": snippet})
                # supportingChunks
                for chunk in gm.get("supportingChunks", []):
                    ctx = chunk.get("retrievedContext", chunk)
                    title = ctx.get("title", "")
                    url = ctx.get("uri", "#")
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen.add(key)
                        sources.append({"title": title, "url": url, "snippet": ""})

            # Pattern 3: searchResults (alternative structure)
            if "searchResults" in obj:
                for result in obj["searchResults"]:
                    doc = result.get("document", result)
                    title = doc.get("title", doc.get("name", ""))
                    url = doc.get("uri", doc.get("link", "#"))
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen.add(key)
                        sources.append({"title": title, "url": url, "snippet": ""})

            # Pattern 4: citations
            if "citations" in obj:
                for cite in obj["citations"]:
                    title = cite.get("title", cite.get("source", ""))
                    url = cite.get("uri", cite.get("url", "#"))
                    key = f"{title}-{url}"
                    if key not in seen and title:
                        seen.add(key)
                        sources.append({"title": title, "url": url, "snippet": ""})

            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    find_sources(v, f"{path}.{k}")

    find_sources(data)
    print(f"[DEBUG] Extracted {len(sources)} sources")
    return sources[:5]


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


@app.post("/api/chat")
async def chat(request: Request, body: ChatRequest):
    """Send a message in a conversation."""
    token = request.headers.get("X-Entra-Id-Token")

    print(f"[DEBUG] Query: {body.query[:50]}...")
    print(f"[DEBUG] SharePoint Only: {body.sharepoint_only}")
    print(f"[DEBUG] Session ID: {body.session_id[:50] if body.session_id else 'None'}...")
    print(f"[DEBUG] Token present: {bool(token)}, length: {len(token) if token else 0}")

    # Save token for debugging
    if token:
        with open("/tmp/entra_token.txt", "w") as f:
            f.write(token)

    gcp_token = exchange_token(token) if token else None
    print(f"[DEBUG] GCP Token: {bool(gcp_token)}")

    if not gcp_token:
        return {"answer": "Please login with Microsoft to chat.", "sources": [], "session_id": None}

    # Create session if not provided
    session_id = body.session_id
    if not session_id:
        create_resp = requests.post(
            f"{BASE_URL}/sessions",
            headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
            json={"displayName": body.query[:30]},
            timeout=10
        )
        if create_resp.ok:
            session_id = create_resp.json().get("name")

    # Build payload
    payload = {"query": {"text": body.query}}

    # Add session for conversation continuity
    if session_id:
        payload["session"] = session_id

    # Restrict to SharePoint datastore when enabled
    if body.sharepoint_only:
        payload["toolsSpec"] = {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{
                    "dataStore": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"
                }]
            }
        }

    # Call StreamAssist
    resp = requests.post(
        f"{BASE_URL}/assistants/default_assistant:streamAssist",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=90
    )

    if not resp.ok:
        return {"answer": f"API Error: {resp.status_code} - {resp.text[:200]}", "sources": [], "session_id": session_id}

    # Parse response
    data = resp.json()

    # Debug: Save full response to see structure
    import json
    with open("/tmp/last_response.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"[DEBUG] Response chunks: {len(data)}")

    answer_parts = []

    for chunk in data:
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            is_thought = content.get("thought", False)
            if text and not is_thought:
                answer_parts.append(text)

    answer = "".join(answer_parts) or "I couldn't find relevant information. Try rephrasing your question."
    sources = extract_sources(data)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id
    }


# Keep old endpoint for backwards compatibility
@app.post("/api/search")
async def search(request: Request, body: ChatRequest):
    """Alias for /api/chat for backwards compatibility."""
    return await chat(request, body)


class QuickAskRequest(BaseModel):
    query: str
    context: str = ""  # Previous conversation context


@app.post("/api/quick")
async def quick_ask(request: Request, body: QuickAskRequest):
    """Quick response using Gemini 3.1 Flash Lite with Google Search grounding."""
    import httpx
    import google.auth
    from google.auth.transport.requests import Request as AuthRequest

    try:
        creds, _ = google.auth.default()
        creds.refresh(AuthRequest())
        access_token = creds.token
    except Exception as e:
        return {"answer": f"Auth error: {e}", "quick": True, "sources": []}

    # Build prompt
    prompt = body.query
    if body.context:
        prompt = f"Context:\n{body.context}\n\nQuestion: {body.query}\n\nGive a brief, helpful answer."
    else:
        prompt = f"{body.query}\n\nGive a brief, helpful answer."

    # Gemini 3.1 Flash Lite (global region) with Google Search
    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview:generateContent"

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
