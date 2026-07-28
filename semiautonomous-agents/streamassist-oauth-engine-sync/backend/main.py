"""
StreamAssist Federated Sync Portal - Diagnostic Controller

This server manages:
1. MSAL / WIF token exchange.
2. Dynamic custom domain allowlisting.
3. Interactive step-by-step diagnostic workflows.
4. Outbound Google and Microsoft REST logging (Headers, Payloads, status).
5. Engine User Data synchronization (AUTHORIZED / EXPIRED).
"""

import os
import json
import time
import base64
import secrets
import requests
from urllib.parse import urlencode, urlparse
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

app = FastAPI(title="StreamAssist Diagnostic Studio API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "")
ENGINE_ID = os.environ.get("ENGINE_ID", "")
CONNECTOR_ID = os.environ.get("CONNECTOR_ID", "")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "")
CONNECTOR_CLIENT_ID = os.environ.get("CONNECTOR_CLIENT_ID", "")
TENANT_ID = os.environ.get("TENANT_ID", "")
SHAREPOINT_DOMAIN = os.environ.get("SHAREPOINT_DOMAIN", "contoso.sharepoint.com")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", 8003))

# Endpoint parameters
ENDPOINT_GLOBAL = "discoveryengine.googleapis.com"
VERSION = "v1alpha"
LOCATION = os.environ.get("LOCATION", "us-central1")

# Global Base URL (For Engines, Widget Config, and Assistants)
BASE_URL_GLOBAL = f"https://{ENDPOINT_GLOBAL}/{VERSION}/projects/{PROJECT_NUMBER}/locations/global/collections"
ENGINE_URL = f"{BASE_URL_GLOBAL}/default_collection/engines/{ENGINE_ID}"
STREAMASSIST_URL = f"{ENGINE_URL}/assistants/default_assistant:streamAssist"

# Connector Base URL (The dataConnector resource resides in global region)
CONNECTOR_URL = f"{BASE_URL_GLOBAL}/{CONNECTOR_ID}"

SP_SCOPES = f"openid offline_access https://{SHAREPOINT_DOMAIN}/AllSites.Read https://{SHAREPOINT_DOMAIN}/Sites.Search.All"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

# ── Diagnostic Logging Helper ──────────────────────────────────────────────────

def _log_http_call(trace_list: list, method: str, url: str, headers: dict, body: any, response: requests.Response, elapsed_ms: int, response_body_override: any = None):
    """Formats and logs full HTTP transaction details for the UI diagnostic visualizer."""
    try:
        req_body_json = body if isinstance(body, dict) else (json.loads(body) if isinstance(body, str) else body)
    except:
        req_body_json = str(body)

    # Sanitize tokens from headers for security
    sanitized_headers = {}
    for k, v in headers.items():
        if k.lower() in ["authorization", "x-entra-id-token"]:
            parts = v.split(" ")
            if len(parts) == 2:
                sanitized_headers[k] = f"{parts[0]} {parts[1][:15]}..."
            else:
                sanitized_headers[k] = f"{v[:15]}..."
        else:
            sanitized_headers[k] = v

    # Parse response body
    if response_body_override is not None:
        resp_body = response_body_override
    else:
        try:
            resp_body = response.json()
        except:
            try:
                resp_body = response.text
            except:
                resp_body = "<Stream content consumed>"

    # Generate equivalent cURL string
    curl_headers = " ".join([f"-H '{k}: {v}'" for k, v in sanitized_headers.items()])
    curl_body = f"-d '{json.dumps(req_body_json)}'" if req_body_json else ""
    curl_cmd = f"curl -X {method} '{url}' {curl_headers} {curl_body}"

    trace_list.append({
        "stage": url.split("/")[-1].split("?")[0].split(":")[0],
        "method": method,
        "url": url,
        "request_headers": sanitized_headers,
        "request_body": req_body_json,
        "response_headers": dict(response.headers) if hasattr(response, 'headers') else {},
        "response_body": resp_body,
        "status_code": response.status_code if hasattr(response, 'status_code') else 200,
        "duration_ms": elapsed_ms,
        "curl": curl_cmd
    })


# ── Core Workflows ────────────────────────────────────────────────────────────

def _exchange_token(entra_jwt: str, trace: list) -> Optional[str]:
    """Exchanges Entra JWT for GCP access token and logs headers/payloads."""
    url = "https://sts.googleapis.com/v1/token"
    headers = {"Content-Type": "application/json"}
    body = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }
    
    start = time.time()
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "POST", url, headers, body, resp, elapsed)
        return resp.json().get("access_token") if resp.ok else None
    except Exception as e:
        # Create mock response for logs
        mock_resp = requests.Response()
        mock_resp.status_code = 500
        mock_resp._content = json.dumps({"error": f"Connection failed: {str(e)}"}).encode()
        _log_http_call(trace, "POST", url, headers, body, mock_resp, 0)
        return None


def _gcp_headers(gcp_token: str) -> dict:
    return {
        "Authorization": f"Bearer {gcp_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }


def _allowlist_domain(gcp_token: str, custom_domain: str, trace: list) -> bool:
    """Proactively allowlists the custom domain under widgetConfigs/default_search_widget_config."""
    widget_config_id = "default_search_widget_config"
    url = f"{BASE_URL_GLOBAL}/default_collection/engines/{ENGINE_ID}/widgetConfigs/{widget_config_id}?updateMask=accessSettings"
    headers = _gcp_headers(gcp_token)
    body = {
        "name": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/{widget_config_id}",
        "accessSettings": {
            "allowlistedDomains": [custom_domain],
            "enableWebApp": True
        }
    }

    start = time.time()
    try:
        resp = requests.patch(url, headers=headers, json=body, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "PATCH", url, headers, body, resp, elapsed)
        return resp.ok
    except Exception as e:
        mock_resp = requests.Response()
        mock_resp.status_code = 500
        mock_resp._content = json.dumps({"error": str(e)}).encode()
        _log_http_call(trace, "PATCH", url, headers, body, mock_resp, 0)
        return False


def _sync_engine_state(gcp_token: str, auth_state: str, trace: list) -> bool:
    """Updates EngineUserData with target Auth State (AUTHORIZED or EXPIRED)."""
    get_url = f"{ENGINE_URL}:getEngineUserData"
    update_url = f"{ENGINE_URL}:updateEngineUserData?updateMask=connectorAuthStates"
    headers = _gcp_headers(gcp_token)
    connector_full_name = f"projects/{PROJECT_NUMBER}/locations/global/collections/{CONNECTOR_ID}/dataConnector"

    # Step A: Get existing user data
    start_get = time.time()
    try:
        get_resp = requests.post(get_url, headers=headers, json={}, timeout=10)
        elapsed_get = round((time.time() - start_get) * 1000)
        _log_http_call(trace, "POST", get_url, headers, {}, get_resp, elapsed_get)
        if not get_resp.ok:
            if get_resp.status_code == 404:
                print(f"[Sync] getEngineUserData returned 404 (Method not found). Gracefully skipping engine state synchronization as this is expected if the private preview metadata APIs are not enabled on this engine type.")
                return True
            return False
        engine_user_data = get_resp.json()
    except Exception as e:
        print(f"[Sync] Exception in getEngineUserData: {e}")
        return True

    # Modify existing state entries
    connector_auth_states = engine_user_data.get("connectorAuthStates", [])
    found = False
    for state in connector_auth_states:
        if state.get("dataConnector") == connector_full_name:
            state["authState"] = auth_state
            found = True
            break
    if not found:
        connector_auth_states.append({
            "dataConnector": connector_full_name,
            "authState": auth_state
        })

    # Step B: Write back
    update_body = {
        "engine": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}",
        "engineUserData": {
            "connectorAuthStates": connector_auth_states
        },
        "addEntitiesOnly": True
    }

    start_update = time.time()
    try:
        update_resp = requests.post(update_url, headers=headers, json=update_body, timeout=15)
        elapsed_update = round((time.time() - start_update) * 1000)
        _log_http_call(trace, "POST", update_url, headers, update_body, update_resp, elapsed_update)
        return update_resp.ok
    except Exception as e:
        return False


# ── REST API Endpoints ────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "config": {"project": PROJECT_NUMBER, "engine": ENGINE_ID, "connector": CONNECTOR_ID}}


@app.get("/api/diagnostic/configuration")
async def get_config():
    """Returns the current backend configuration so the UI diagnostic wizard can print it."""
    return {
        "PROJECT_NUMBER": PROJECT_NUMBER,
        "ENGINE_ID": ENGINE_ID,
        "CONNECTOR_ID": CONNECTOR_ID,
        "WIF_POOL_ID": WIF_POOL_ID,
        "WIF_PROVIDER_ID": WIF_PROVIDER_ID,
        "CONNECTOR_CLIENT_ID": CONNECTOR_CLIENT_ID,
        "TENANT_ID": TENANT_ID,
        "SHAREPOINT_DOMAIN": SHAREPOINT_DOMAIN,
        "BACKEND_PORT": BACKEND_PORT,
        "SCOPES": SP_SCOPES
    }


@app.post("/api/diagnostic/sts-exchange")
async def diagnostic_sts(request: Request):
    """Runs ONLY the WIF Token Exchange and returns complete REST payloads."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        raise HTTPException(status_code=400, detail="Missing X-Entra-Id-Token header")
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    return {"success": bool(gcp_token), "gcp_token": gcp_token, "_trace": trace}


@app.post("/api/diagnostic/allowlist-domain")
async def diagnostic_allowlist(request: Request):
    """Runs ONLY the custom domain allowlisting and returns the PATCH telemetry."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         raise HTTPException(status_code=400, detail="Missing X-Entra-Id-Token header")
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         raise HTTPException(status_code=401, detail="Identity federation failed")

    raw_origin = request.headers.get("origin") or "http://localhost:5174"
    domain = raw_origin.replace("http://", "").replace("https://", "").split(":")[0]
    
    ok = _allowlist_domain(gcp_token, domain, trace)
    return {"success": ok, "allowlisted_domain": domain, "_trace": trace}


@app.get("/api/sharepoint/auth-url")
async def get_auth_url(request: Request):
    """Gets consent URL by querying widgetConfig with customDomain."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         raise HTTPException(status_code=400, detail="Missing X-Entra-Id-Token header")
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         raise HTTPException(status_code=401, detail="Identity federation failed")

    raw_origin = request.headers.get("origin") or "http://localhost:5174"
    domain = raw_origin.replace("http://", "").replace("https://", "").split(":")[0]

    # Proactive allowlisting
    _allowlist_domain(gcp_token, domain, trace)

    # Fetch widgetConfig with custom domain parameter
    widget_url = f"{BASE_URL_GLOBAL}/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
    headers = _gcp_headers(gcp_token)
    params = {"getWidgetConfigRequestOption.customDomain": domain}

    start = time.time()
    try:
        resp = requests.get(widget_url, headers=headers, params=params, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "GET", f"{widget_url}?customDomain={domain}", headers, None, resp, elapsed)
        widget_ok = resp.ok
    except Exception as e:
        widget_ok = False

    auth_url = ""
    if widget_ok:
        for component in resp.json().get("collectionComponents", []):
            if component.get("id") == CONNECTOR_ID:
                auth_url = component.get("connectorAuthState", {}).get("authorizationUri", "")
                break

    # Assembly fallback
    if not auth_url:
        nonce = secrets.token_urlsafe(16)
        state = base64.b64encode(json.dumps({
            "origin": raw_origin,
            "useBroadcastChannel": "false",
            "nonce": nonce
        }).encode()).decode()
        
        fallback_params = {
            "client_id": CONNECTOR_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": "https://vertexaisearch.cloud.google.com/oauth-redirect",
            "scope": SP_SCOPES,
            "response_mode": "query",
            "state": state,
            "prompt": "login",
        }
        auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(fallback_params)}"

    return {"auth_url": auth_url, "_trace": trace}


class ExchangeRequest(BaseModel):
    fullRedirectUrl: str


@app.post("/api/oauth/exchange")
async def oauth_exchange(request: Request, body: ExchangeRequest):
    """Exchanges and stores refresh tokens, then synchronizes engine state."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         raise HTTPException(status_code=400, detail="Missing X-Entra-Id-Token header")
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         raise HTTPException(status_code=401, detail="Federation failed")

    # Step 4: Call acquireAndStoreRefreshToken
    store_url = f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken"
    headers = _gcp_headers(gcp_token)
    store_body = {"fullRedirectUri": body.fullRedirectUrl}

    start = time.time()
    try:
        resp = requests.post(store_url, headers=headers, json=store_body, timeout=30)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "POST", store_url, headers, store_body, resp, elapsed)
        store_ok = resp.ok
        if not store_ok:
            print(f"DEBUG EXCH: store_url={store_url}")
            print(f"DEBUG EXCH: store_body={store_body}")
            print(f"DEBUG EXCH: status_code={resp.status_code}")
            print(f"DEBUG EXCH: response_body={resp.text}")
    except Exception as e:
        print(f"DEBUG EXCH: Exception occurred: {str(e)}")
        store_ok = False

    if not store_ok:
        return {"success": False, "error": "Token storage failed", "_trace": trace}

    # Step 5: Sync to AUTHORIZED
    sync_ok = _sync_engine_state(gcp_token, "AUTHORIZED", trace)

    return {"success": store_ok and sync_ok, "sync_status": sync_ok, "_trace": trace}


@app.post("/api/sharepoint/disconnect")
async def disconnect(request: Request):
    """Disconnects and sets connector status to EXPIRED in the engine metadata."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         raise HTTPException(status_code=400, detail="Missing X-Entra-Id-Token")
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         raise HTTPException(status_code=401, detail="Federation failed")

    ok = _sync_engine_state(gcp_token, "EXPIRED", trace)
    return {"success": ok, "_trace": trace}


@app.get("/api/sharepoint/check-connection")
async def check_connection(request: Request):
    """Verifies connection with acquireAccessToken."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         return {"connected": False, "_trace": []}
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         return {"connected": False, "_trace": trace}

    url = f"{CONNECTOR_URL}/dataConnector:acquireAccessToken"
    headers = _gcp_headers(gcp_token)

    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json={}, timeout=15)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "POST", url, headers, {}, resp, elapsed)
        connected = resp.ok and bool(resp.json().get("accessToken"))
    except:
        connected = False

    return {"connected": connected, "_trace": trace}


# ── Search API ────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    session_token: Optional[str] = None


@app.post("/api/search/stream")
async def search_stream(request: Request, body: SearchRequest):
    """Executes a real-time SSE streaming search, forwarding events as they arrive from Google."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
        raise HTTPException(status_code=401, detail="Federation failed")

    start = time.time()
    ds_base = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}"
    
    payload = {
        "query": {
            "text": body.query
        },
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": f"{ds_base}_{et}"} for et in ENTITY_TYPES],
            },
            "toolRegistry": "default_tool_registry"
        },
        "languageCode": "en-US",
        "answerGenerationMode": "NORMAL",
        "assistSkippingMode": "REQUEST_ASSIST"
    }
    if body.session_token:
        payload["session"] = body.session_token

    headers = _gcp_headers(gcp_token)

    import asyncio
    import threading

    async def event_generator():
        # Step 1 & 2: Token Exchange & Federation is complete
        yield "data: " + json.dumps({"type": "token_exchange", "status": "done", "_trace": trace}) + "\n\n"
        # Step 3: Resolving SharePoint Authorization
        yield "data: " + json.dumps({"type": "status", "step": 3}) + "\n\n"
        # Step 4: SharePoint Semantic Search Active
        yield "data: " + json.dumps({"type": "status", "step": 4}) + "\n\n"

        q = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def stream_reader_worker():
            try:
                resp = requests.post(STREAMASSIST_URL, headers=headers, json=payload, stream=True, timeout=60)
                if resp.status_code != 200:
                    loop.call_soon_threadsafe(q.put_nowait, {
                        "type": "error",
                        "message": f"Google StreamAssist returned status code {resp.status_code}: {resp.text}"
                    })
                    loop.call_soon_threadsafe(q.put_nowait, {"type": "done", "response": resp})
                    return

                decoder = json.JSONDecoder()
                buffer = ""
                for chunk_str in resp.iter_content(chunk_size=None, decode_unicode=True):
                    if not chunk_str:
                        continue
                    buffer += chunk_str

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
                                loop.call_soon_threadsafe(q.put_nowait, {"type": "google_chunk", "chunk": chunk})
                                sa_resp = chunk.get("streamAssistResponse", {}) or chunk
                                if isinstance(sa_resp, dict):
                                    session_info = sa_resp.get("sessionInfo", {}) or chunk.get("sessionInfo", {})
                                    if isinstance(session_info, dict) and session_info.get("session"):
                                        session_name = session_info.get("session")
                                        loop.call_soon_threadsafe(q.put_nowait, {"type": "session", "token": session_name})

                                    answer_obj = sa_resp.get("answer", {}) or chunk.get("answer", {})
                                    if isinstance(answer_obj, dict):
                                        for reply in answer_obj.get("replies", []):
                                            if not isinstance(reply, dict):
                                                continue
                                            gc = reply.get("groundedContent", {})
                                            if not isinstance(gc, dict):
                                                continue
                                            content = gc.get("content", {})
                                            if isinstance(content, dict):
                                                # Step 5: Grounded synthesis starts
                                                loop.call_soon_threadsafe(q.put_nowait, {"type": "status", "step": 5})

                                                if content.get("thought"):
                                                    tval = content.get("text") or ""
                                                    loop.call_soon_threadsafe(q.put_nowait, {"type": "thought", "delta": tval})
                                                elif content.get("text"):
                                                    val = content["text"]
                                                    loop.call_soon_threadsafe(q.put_nowait, {"type": "text", "delta": val})

                                                inline_data = content.get("inlineData", {})
                                                if isinstance(inline_data, dict) and inline_data.get("mimeType") == "application/json+suggestions":
                                                    try:
                                                        encoded_data = inline_data.get("data", "")
                                                        decoded_bytes = base64.b64decode(encoded_data)
                                                        decoded_json = json.loads(decoded_bytes)
                                                        qs = decoded_json.get("recommendedQuestionsResponse", {}).get("questions", [])
                                                        if qs:
                                                            loop.call_soon_threadsafe(q.put_nowait, {"type": "suggestions", "suggestions": qs})
                                                    except Exception as sug_err:
                                                        print(f"Error decoding suggestion chips: {sug_err}")

                                            # References parse
                                            for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                                                if not isinstance(ref, dict):
                                                    continue
                                                try:
                                                    doc_meta = ref.get("documentMetadata", {})
                                                    if isinstance(doc_meta, dict) and doc_meta.get("uri"):
                                                        citation = {
                                                            "title": doc_meta.get("title", "Untitled Document"),
                                                            "url": doc_meta["uri"],
                                                            "description": doc_meta.get("description", ""),
                                                            "file_type": doc_meta.get("mimeType", ""),
                                                            "author": doc_meta.get("author", ""),
                                                            "entity_type": doc_meta.get("entityType", "")
                                                        }
                                                        loop.call_soon_threadsafe(q.put_nowait, {"type": "citation", "citation": citation})
                                                except Exception as ref_err:
                                                    print(f"Error parsing references: {ref_err}")

                        except json.JSONDecodeError:
                            # Need more incoming data from the stream to complete the current JSON object
                            break
                        except Exception as loop_e:
                            print(f"Streaming parse loop internal error: {loop_e}")
                            break
                loop.call_soon_threadsafe(q.put_nowait, {"type": "done", "response": resp})
            except Exception as e:
                loop.call_soon_threadsafe(q.put_nowait, {"type": "error", "message": f"Stream reader thread error: {str(e)}"})
                loop.call_soon_threadsafe(q.put_nowait, {"type": "done", "response": None})

        # Start thread
        thread = threading.Thread(target=stream_reader_worker, daemon=True)
        thread.start()

        google_chunks = []
        answer_parts = []
        thought_parts = []
        sources = []
        session_name = None
        resp_obj = None

        try:
            while True:
                event = await q.get()
                etype = event["type"]
                if etype == "done":
                    resp_obj = event.get("response")
                    break
                elif etype == "error":
                    yield "data: " + json.dumps({"type": "error", "message": event["message"]}) + "\n\n"
                    # Keep reading to clean up the done message
                    continue
                elif etype == "google_chunk":
                    google_chunks.append(event["chunk"])
                elif etype == "session":
                    session_name = event["token"]
                    yield "data: " + json.dumps(event) + "\n\n"
                elif etype == "status":
                    yield "data: " + json.dumps(event) + "\n\n"
                elif etype == "thought":
                    thought_parts.append(event["delta"])
                    yield "data: " + json.dumps(event) + "\n\n"
                elif etype == "text":
                    answer_parts.append(event["delta"])
                    yield "data: " + json.dumps(event) + "\n\n"
                elif etype == "suggestions":
                    yield "data: " + json.dumps(event) + "\n\n"
                elif etype == "citation":
                    citation = event["citation"]
                    if citation not in sources:
                        sources.append(citation)
                        yield "data: " + json.dumps(event) + "\n\n"

            # Check if answer is completely empty
            if not "".join(answer_parts):
                skipped_reasons = []
                for chunk in google_chunks:
                    if isinstance(chunk, dict):
                        sa_resp = chunk.get("streamAssistResponse", {}) or chunk
                        answer_obj = sa_resp.get("answer", {}) or chunk.get("answer", {}) if isinstance(sa_resp, dict) else {}
                        if isinstance(answer_obj, dict):
                            reasons = answer_obj.get("assistSkippedReasons", [])
                            if reasons:
                                skipped_reasons.extend(reasons)
                if skipped_reasons:
                    fallback = f"Google AI skipped this query: {', '.join(skipped_reasons)}. Please ask a specific question about your documents."
                else:
                    fallback = "No grounded answers found in the connected SharePoint. Please try a different search query."
                yield "data: " + json.dumps({"type": "text", "delta": fallback}) + "\n\n"

            # Write raw dump
            try:
                with open("raw_stream_assist_response.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(google_chunks, indent=2))
            except Exception as w_err:
                print(f"Failed to dump response: {w_err}")

            # Log HTTP Call and yield search trace
            elapsed = round((time.time() - start) * 1000)
            if resp_obj is not None:
                _log_http_call(trace, "POST", STREAMASSIST_URL, headers, payload, resp_obj, elapsed, response_body_override=google_chunks)
            yield "data: " + json.dumps({"type": "search_trace", "trace": trace}) + "\n\n"
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"

        except Exception as loop_err:
            print(f"Stream error: {loop_err}")
            yield "data: " + json.dumps({"type": "error", "message": str(loop_err)}) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/search")
async def search(request: Request, body: SearchRequest):
    """Executes search with user WIF authentication using the direct streamAssist endpoint."""
    entra_jwt = request.headers.get("X-Entra-Id-Token")
    if not entra_jwt:
         raise HTTPException(status_code=401, detail="Unauthenticated")
    
    trace = []
    gcp_token = _exchange_token(entra_jwt, trace)
    if not gcp_token:
         raise HTTPException(status_code=401, detail="Federation failed")

    start = time.time()
    ds_base = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}"
    
    # Correct payload format using text as required by direct streamAssist
    payload = {
        "query": {
            "text": body.query
        },
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": f"{ds_base}_{et}"} for et in ENTITY_TYPES],
            },
            "toolRegistry": "default_tool_registry"
        },
        "languageCode": "en-US",
        "answerGenerationMode": "NORMAL",
        "assistSkippingMode": "REQUEST_ASSIST"
    }
    if body.session_token:
        payload["session"] = body.session_token

    headers = _gcp_headers(gcp_token)
    try:
        resp = requests.post(STREAMASSIST_URL, headers=headers, json=payload, timeout=60)
        elapsed = round((time.time() - start) * 1000)
        _log_http_call(trace, "POST", STREAMASSIST_URL, headers, payload, resp, elapsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        # Dump the raw response to a local JSON file for inspection/testing
        try:
            with open("raw_stream_assist_response.json", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("[Diagnostic] Successfully dumped raw Google response to raw_stream_assist_response.json")
        except Exception as write_err:
            print(f"[Diagnostic] Failed to dump raw response: {write_err}")

        # Try to parse the entire response as a structured JSON block (e.g. pretty-printed list of chunks)
        chunks = []
        try:
            parsed = json.loads(resp.text)
            chunks = parsed if isinstance(parsed, list) else [parsed]
        except Exception as block_err:
            # Fallback to line-by-line NDJSON/LJSON parsing if response was streamed line-by-line
            for line in resp.text.splitlines():
                if line.strip():
                    try:
                        chunks.append(json.loads(line))
                    except:
                        pass

        answer_parts, session_name, sources = [], None, []
        thought_parts = []
        suggestions = []

        import base64

        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
                
            # Support both direct and widget-wrapped response formats
            sa_resp = chunk.get("streamAssistResponse", {}) or chunk
            if not isinstance(sa_resp, dict):
                sa_resp = chunk
                
            session_info = sa_resp.get("sessionInfo", {}) or chunk.get("sessionInfo", {})
            if isinstance(session_info, dict):
                session_name = session_info.get("session") or session_name
            
            answer_obj = sa_resp.get("answer", {}) or chunk.get("answer", {})
            if not isinstance(answer_obj, dict):
                continue
                
            for reply in answer_obj.get("replies", []):
                if not isinstance(reply, dict):
                    continue
                gc = reply.get("groundedContent", {})
                if not isinstance(gc, dict):
                    continue
                content = gc.get("content", {})
                if isinstance(content, dict):
                    # Capture intermediate thought/thinking processes if present
                    if content.get("thought"):
                        thought_parts.append(content["text"])
                    elif content.get("text"):
                        answer_parts.append(content["text"])
                    
                    # Look for encoded follow-up questions (suggestions)
                    inline_data = content.get("inlineData", {})
                    if isinstance(inline_data, dict) and inline_data.get("mimeType") == "application/json+suggestions":
                        try:
                            encoded_data = inline_data.get("data", "")
                            decoded_bytes = base64.b64decode(encoded_data)
                            decoded_json = json.loads(decoded_bytes)
                            qs = decoded_json.get("recommendedQuestionsResponse", {}).get("questions", [])
                            if qs:
                                suggestions.extend(qs)
                        except Exception as sug_err:
                            print(f"Error decoding suggestion chips: {sug_err}")
                
                # Parse references
                for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                    if not isinstance(ref, dict):
                        continue
                    try:
                        doc_meta = ref.get("documentMetadata", {})
                        if isinstance(doc_meta, dict) and doc_meta.get("uri"):
                            sources.append({
                                "title": doc_meta.get("title", "Untitled Document"),
                                "url": doc_meta["uri"],
                                "description": doc_meta.get("description", ""),
                                "file_type": doc_meta.get("mimeType", ""),
                                "author": doc_meta.get("author", ""),
                                "entity_type": doc_meta.get("entityType", "")
                            })
                    except Exception as ref_err:
                        print(f"Error parsing reference block: {ref_err}")
                        continue

        seen = set()
        unique_sources = [s for s in sources if s["url"] not in seen and not seen.add(s["url"])]

        answer_text = "".join(answer_parts)
        if not answer_text:
            skipped_reasons = []
            for chunk in chunks:
                if isinstance(chunk, dict):
                    sa_resp = chunk.get("streamAssistResponse", {}) or chunk
                    answer_obj = sa_resp.get("answer", {}) or chunk.get("answer", {}) if isinstance(sa_resp, dict) else {}
                    if isinstance(answer_obj, dict):
                        reasons = answer_obj.get("assistSkippedReasons", [])
                        if reasons:
                            skipped_reasons.extend(reasons)
            if skipped_reasons:
                answer_text = f"Google AI skipped this query: {', '.join(skipped_reasons)}. Please ask a specific question about your documents (e.g., 'What files do we have?')."
            else:
                answer_text = "No grounded answers found in the connected SharePoint. Please try a different search query."

        return {
            "answer": answer_text,
            "sources": unique_sources,
            "session_token": session_name,
            "thought": "".join(thought_parts) if thought_parts else None,
            "suggestions": suggestions,
            "_trace": trace
        }
    except Exception as e:
        import traceback
        print(f"[Search Error] {traceback.format_exc()}")
        return {
            "error": f"Internal parser error: {str(e)}",
            "traceback": traceback.format_exc(),
            "_trace": trace
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
