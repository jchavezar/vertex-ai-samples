"""
StreamAssist Quantum Light Studio — Next-Generation Backend
FastAPI server implementing:
1. Native Async SSE Streaming with real-time token/thought/citation parsing.
2. Dynamic Discovery Engine Widget Configuration discovery.
3. Microsoft Entra ID -> Google STS Workload Identity Federation (WIF) exchange.
4. DataConnector per-user SharePoint token binding and validation.
5. Comprehensive HTTP Telemetry and Stream Event Async Field extraction.
"""

import os
import sys
import json
import time
import base64
import secrets
import asyncio
import httpx
import requests
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load local .env or fallback
load_dotenv(override=True)

app = FastAPI(
    title="StreamAssist Quantum Light Studio API",
    description="Next-Generation Enterprise Grounding Hub for Gemini Enterprise & SharePoint",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "545964020693")
PROJECT_ID = os.environ.get("PROJECT_ID", "sharepoint-wif-agent")
LOCATION = os.environ.get("LOCATION", "us-central1")
ENGINE_ID = os.environ.get("ENGINE_ID", "gemini-enterprise")
CONNECTOR_ID = os.environ.get("CONNECTOR_ID", "sharepoint-data-def-connector")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "sp-wif-pool-v2")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "entra-provider")
CONNECTOR_CLIENT_ID = os.environ.get("CONNECTOR_CLIENT_ID", "7868d053-cf9c-4848-be5a-f9bbf8279234")
TENANT_ID = os.environ.get("TENANT_ID", "de46a3fd-0d68-4b25-8343-6eb5d71afce9")
SHAREPOINT_DOMAIN = os.environ.get("SHAREPOINT_DOMAIN", "sockcop.sharepoint.com")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", 8004))

REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://vertexaisearch.cloud.google.com/oauth-redirect")
SP_SCOPES = f"openid offline_access https://{SHAREPOINT_DOMAIN}/AllSites.Read https://{SHAREPOINT_DOMAIN}/Sites.Search.All"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

ENDPOINT_GLOBAL = "discoveryengine.googleapis.com"
VERSION = "v1alpha"
BASE_URL_GLOBAL = f"https://{ENDPOINT_GLOBAL}/{VERSION}/projects/{PROJECT_NUMBER}/locations/global/collections"
ENGINE_URL = f"{BASE_URL_GLOBAL}/default_collection/engines/{ENGINE_ID}"
STREAMASSIST_URL = f"{ENGINE_URL}/assistants/default_assistant:streamAssist"
WIDGET_CONFIG_URL = f"{ENGINE_URL}/widgetConfigs/default_search_widget_config"
CONNECTOR_URL = f"{BASE_URL_GLOBAL}/{CONNECTOR_ID}"

_pending_consents: dict[str, str] = {}
_cached_adc_token: Optional[str] = None
_cached_adc_expiry: float = 0


# ── Auth Helpers ──────────────────────────────────────────────────────────────

def get_google_adc_token() -> str:
    """Retrieves a fresh Google Cloud ADC token."""
    global _cached_adc_token, _cached_adc_expiry
    now = time.time()
    if _cached_adc_token and now < _cached_adc_expiry:
        return _cached_adc_token

    import google.auth
    import google.auth.transport.requests
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    _cached_adc_token = credentials.token
    _cached_adc_expiry = now + 3000
    return _cached_adc_token


def _exchange_wif_token(entra_jwt: str, trace: Optional[list] = None) -> Optional[str]:
    """Exchanges an Entra ID token for a GCP WIF Access Token via STS."""
    url = "https://sts.googleapis.com/v1/token"
    headers = {"Content-Type": "application/json"}
    body = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    start = time.time()
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        token = resp.json().get("access_token") if resp.ok else None
        if trace is not None:
            trace.append({
                "stage": "STS WIF Token Exchange",
                "endpoint": "POST sts.googleapis.com/v1/token",
                "status": resp.status_code,
                "duration_ms": elapsed,
                "input": {
                    "audience": body["audience"],
                    "grantType": body["grantType"],
                    "subjectToken": f"{entra_jwt[:25]}...{entra_jwt[-10:]}" if entra_jwt else "",
                },
                "output": {"access_token": f"{token[:25]}..."} if token else {"error": resp.text[:250]},
            })
        return token
    except Exception as e:
        if trace is not None:
            trace.append({
                "stage": "STS WIF Token Exchange",
                "endpoint": "POST sts.googleapis.com/v1/token",
                "status": 500,
                "duration_ms": round((time.time() - start) * 1000),
                "error": str(e),
            })
        return None


def _get_bearer_token(request: Request, body_token: Optional[str] = None, auth_mode: str = "auto") -> tuple[str, str]:
    """Resolves the best available GCP access token."""
    entra_jwt = request.headers.get("X-Entra-Id-Token") or body_token
    if auth_mode in ["wif", "auto"] and entra_jwt:
        wif_token = _exchange_wif_token(entra_jwt)
        if wif_token:
            return wif_token, "WIF_ENTRA"
    
    # Fallback to ADC token
    try:
        adc_token = get_google_adc_token()
        return adc_token, "GOOGLE_ADC"
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failure: {str(e)}")


def _gcp_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }


# ── REST API Endpoints ────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "StreamAssist Quantum Light Studio", "timestamp": time.time()}


@app.get("/api/config")
async def get_config():
    """Returns backend configuration for UI state."""
    return {
        "PROJECT_NUMBER": PROJECT_NUMBER,
        "PROJECT_ID": PROJECT_ID,
        "LOCATION": LOCATION,
        "ENGINE_ID": ENGINE_ID,
        "CONNECTOR_ID": CONNECTOR_ID,
        "WIF_POOL_ID": WIF_POOL_ID,
        "WIF_PROVIDER_ID": WIF_PROVIDER_ID,
        "CONNECTOR_CLIENT_ID": CONNECTOR_CLIENT_ID,
        "TENANT_ID": TENANT_ID,
        "SHAREPOINT_DOMAIN": SHAREPOINT_DOMAIN,
        "BACKEND_PORT": BACKEND_PORT,
        "STREAMASSIST_URL": STREAMASSIST_URL,
        "DATA_STORES": [f"{CONNECTOR_ID}_{et}" for et in ENTITY_TYPES],
        "SP_SCOPES": SP_SCOPES,
    }


@app.get("/api/discovery/widget-config")
async def get_widget_config(request: Request):
    """Dynamically queries Discovery Engine Widget Configuration to discover datastores."""
    token, auth_source = _get_bearer_token(request)
    headers = _gcp_headers(token)
    try:
        resp = requests.get(WIDGET_CONFIG_URL, headers=headers, timeout=15)
        if resp.ok:
            data = resp.json()
            collections = data.get("collectionComponents", [])
            datastores = []
            if collections:
                datastores = [ds.get("name") for ds in collections[0].get("dataStoreComponents", [])]
            return {
                "success": True,
                "auth_source": auth_source,
                "widget_config": data,
                "discovered_datastores": datastores,
                "collection_name": collections[0].get("name") if collections else None
            }
        else:
            return {
                "success": False,
                "status_code": resp.status_code,
                "error": resp.text,
                "auth_source": auth_source,
                "fallback_datastores": [
                    f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}_{et}"
                    for et in ENTITY_TYPES
                ]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback_datastores": [
                f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}_{et}"
                for et in ENTITY_TYPES
            ]
        }


class StreamAssistRequest(BaseModel):
    query: str
    session_token: Optional[str] = None
    entra_token: Optional[str] = None
    auth_mode: Optional[str] = "auto"


@app.post("/api/stream-assist")
async def stream_assist_sse(request: Request, body: StreamAssistRequest):
    """
    Core Server-Sent Events (SSE) Streaming endpoint for StreamAssist using native httpx async streaming.
    """
    gcp_token, auth_source = _get_bearer_token(request, body.entra_token, body.auth_mode or "auto")
    
    ds_base = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}"
    data_store_specs = [{"dataStore": f"{ds_base}_{et}"} for et in ENTITY_TYPES]

    payload = {
        "query": {"text": body.query},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": data_store_specs
            }
        }
    }
    if body.session_token:
        payload["session"] = body.session_token

    headers = _gcp_headers(gcp_token)

    async def event_generator():
        yield f"data: {json.dumps({'type': 'init', 'auth_source': auth_source, 'endpoint': STREAMASSIST_URL})}\n\n"
        start_time = time.time()
        ttft_logged = False
        chunks_count = 0
        seen_citations = []

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                async with client.stream("POST", STREAMASSIST_URL, headers=headers, json=payload) as resp:
                    if resp.status_code != 200:
                        error_text = await resp.aread()
                        yield f"data: {json.dumps({'type': 'error', 'status_code': resp.status_code, 'message': error_text.decode('utf-8', errors='ignore')})}\n\n"
                        yield f"data: {json.dumps({'type': 'done', 'status': 'failed'})}\n\n"
                        return

                    decoder = json.JSONDecoder()
                    buffer = ""

                    async for chunk_bytes in resp.aiter_bytes():
                        if not chunk_bytes:
                            continue
                        buffer += chunk_bytes.decode("utf-8", errors="ignore")

                        while True:
                            buffer = buffer.strip()
                            if buffer.startswith("["):
                                buffer = buffer[1:].strip()
                            if buffer.startswith("]"):
                                buffer = buffer[1:].strip()
                            if buffer.startswith(","):
                                buffer = buffer[1:].strip()
                            if not buffer:
                                break

                            try:
                                chunk, index = decoder.raw_decode(buffer)
                                buffer = buffer[index:].strip()

                                if isinstance(chunk, dict):
                                    chunks_count += 1
                                    yield f"data: {json.dumps({'type': 'raw_chunk', 'chunk': chunk})}\n\n"

                                    assist_token = chunk.get("assistToken")
                                    if assist_token:
                                        yield f"data: {json.dumps({'type': 'assist_token', 'token': assist_token})}\n\n"

                                    session_info = chunk.get("sessionInfo", {})
                                    if isinstance(session_info, dict) and session_info.get("session"):
                                        yield f"data: {json.dumps({'type': 'session', 'session': session_info.get('session'), 'queryId': session_info.get('queryId')})}\n\n"

                                    answer = chunk.get("answer", {})
                                    if isinstance(answer, dict):
                                        state = answer.get("state")
                                        if state:
                                            yield f"data: {json.dumps({'type': 'state', 'state': state})}\n\n"

                                        for reply in answer.get("replies", []):
                                            if not isinstance(reply, dict):
                                                continue
                                            gc = reply.get("groundedContent", {})
                                            if isinstance(gc, dict):
                                                content = gc.get("content", {})
                                                if isinstance(content, dict):
                                                    if content.get("thought") is True:
                                                        thought_text = content.get("text", "")
                                                        if thought_text:
                                                            yield f"data: {json.dumps({'type': 'thought', 'delta': thought_text})}\n\n"
                                                    elif content.get("text"):
                                                        text_val = content["text"]
                                                        if not ttft_logged:
                                                            ttft_ms = round((time.time() - start_time) * 1000)
                                                            ttft_logged = True
                                                            yield f"data: {json.dumps({'type': 'ttft', 'duration_ms': ttft_ms})}\n\n"
                                                        yield f"data: {json.dumps({'type': 'text', 'delta': text_val})}\n\n"

                                                    inline_data = content.get("inlineData", {})
                                                    if isinstance(inline_data, dict) and inline_data.get("mimeType") == "application/json+suggestions":
                                                        try:
                                                            raw_b64 = inline_data.get("data", "")
                                                            decoded_json = json.loads(base64.b64decode(raw_b64).decode("utf-8"))
                                                            questions = decoded_json.get("recommendedQuestionsResponse", {}).get("questions", [])
                                                            if questions:
                                                                yield f"data: {json.dumps({'type': 'suggestions', 'questions': questions})}\n\n"
                                                        except Exception:
                                                            pass

                                                tgm = gc.get("textGroundingMetadata", {})
                                                if isinstance(tgm, dict):
                                                    for ref in tgm.get("references", []):
                                                        if isinstance(ref, dict):
                                                            doc_meta = ref.get("documentMetadata", {})
                                                            citation = {
                                                                "title": doc_meta.get("title") or "SharePoint Document",
                                                                "uri": doc_meta.get("uri", ""),
                                                                "document": doc_meta.get("document", ""),
                                                                "domain": doc_meta.get("domain", SHAREPOINT_DOMAIN),
                                                                "mimeType": doc_meta.get("mimeType", ""),
                                                                "pageIdentifier": doc_meta.get("pageIdentifier", ""),
                                                                "snippet": ref.get("content", "")
                                                            }
                                                            if citation["uri"] and citation["uri"] not in [c.get("uri") for c in seen_citations]:
                                                                seen_citations.append(citation)
                                                                yield f"data: {json.dumps({'type': 'citation', 'citation': citation})}\n\n"

                                                    segments = tgm.get("segments", [])
                                                    if segments:
                                                        yield f"data: {json.dumps({'type': 'segments', 'segments': segments})}\n\n"

                            except json.JSONDecodeError:
                                break
                            except Exception:
                                break

            except Exception as conn_err:
                yield f"data: {json.dumps({'type': 'error', 'message': str(conn_err)})}\n\n"

        total_duration = round((time.time() - start_time) * 1000)
        metrics = {
            "type": "metrics",
            "total_duration_ms": total_duration,
            "chunks_count": chunks_count,
            "citations_count": len(seen_citations)
        }
        yield f"data: {json.dumps(metrics)}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'status': 'succeeded'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class WifExchangeRequest(BaseModel):
    entra_jwt: str


@app.post("/api/auth/exchange-wif")
async def exchange_wif(body: WifExchangeRequest):
    """Executes and traces Google STS token exchange for Microsoft Entra ID token."""
    trace = []
    gcp_token = _exchange_wif_token(body.entra_jwt, trace)
    return {
        "success": bool(gcp_token),
        "has_token": bool(gcp_token),
        "trace": trace
    }


@app.get("/api/sharepoint/auth-url")
async def get_sp_auth_url(request: Request):
    """Generates the Microsoft OAuth URL for SharePoint consent."""
    origin = request.headers.get("origin") or f"http://localhost:5175"
    nonce = secrets.token_urlsafe(16)
    entra_jwt = request.headers.get("X-Entra-Id-Token", "")
    if entra_jwt:
        _pending_consents[nonce] = entra_jwt

    params = {
        "client_id": CONNECTOR_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SP_SCOPES,
        "response_mode": "query",
        "state": base64.b64encode(json.dumps({"origin": origin, "useBroadcastChannel": "false", "nonce": nonce}).encode()).decode(),
        "prompt": "consent",
    }
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"
    return {"auth_url": url, "nonce": nonce, "scopes": SP_SCOPES}


@app.get("/api/sharepoint/check-connection")
async def check_sp_connection(request: Request):
    """Validates if SharePoint token is bound under the active WIF/GCP identity."""
    token, auth_source = _get_bearer_token(request)
    headers = _gcp_headers(token)
    start = time.time()
    try:
        resp = requests.post(
            f"{CONNECTOR_URL}/dataConnector:acquireAccessToken",
            headers=headers,
            json={},
            timeout=15
        )
        elapsed = round((time.time() - start) * 1000)
        connected = resp.ok and bool(resp.json().get("accessToken"))
        return {
            "connected": connected,
            "auth_source": auth_source,
            "status_code": resp.status_code,
            "duration_ms": elapsed,
            "response": resp.json() if resp.ok else resp.text
        }
    except Exception as e:
        return {
            "connected": False,
            "auth_source": auth_source,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting StreamAssist Quantum Light Studio Backend on port {BACKEND_PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
