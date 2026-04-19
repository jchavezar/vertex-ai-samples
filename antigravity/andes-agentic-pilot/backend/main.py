"""Caja Los Andes — agentic pilot backend.

Two endpoints:
  POST /api/ask     mock ADK benefit-finder agent (kept from original)
  POST /api/search  proxy to Vertex AI Search (Discovery Engine v1alpha)
                    for the cajalosandes.cl content corpus.

Auth uses Application Default Credentials so we never shell out to gcloud
from production code (the dev only needs `gcloud auth application-default
login` once on their machine).
"""

from __future__ import annotations

import asyncio
import time
import base64
import json
import logging
import os
import uuid

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
from typing import Any, AsyncIterator, Literal

import httpx
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Optional Google ADK imports — preserved for the existing /api/ask path. We
# guard them so the file still imports if google-adk isn't installed yet.
try:  # pragma: no cover - import side-effects only
    from google.adk.agents import LlmAgent  # type: ignore
except Exception:  # pragma: no cover
    LlmAgent = None  # type: ignore

# google-auth is required for Vertex AI Search
import google.auth
import google.auth.transport.requests

# google-genai for the live Andesia chat (Gemini on Vertex AI)
try:  # pragma: no cover
    from google import genai
    from google.genai import types as genai_types
except Exception:  # pragma: no cover
    genai = None  # type: ignore
    genai_types = None  # type: ignore


# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #

CCLA_DE_PROJECT = os.getenv("CCLA_DE_PROJECT", "254356041555")
CCLA_DE_ENGINE = os.getenv("CCLA_DE_ENGINE", "caja-los-andes_1776511755096")
CCLA_DE_LOCATION = os.getenv("CCLA_DE_LOCATION", "global")
CCLA_DE_COLLECTION = os.getenv("CCLA_DE_COLLECTION", "default_collection")
CCLA_DE_SERVING_CONFIG = os.getenv("CCLA_DE_SERVING_CONFIG", "default_search")

# Vertex AI / Gemini config for the live chat endpoint.
# Default to gemini-3-flash-preview in the global region — Gemini 2.5 and below
# are being deprecated. Override via env vars for keynote experiments
# (e.g. GEMINI_MODEL=gemini-3.1-pro-preview for richer reasoning).
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT", "vtxdemos")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "global")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
# AI Overview wants the lightest/fastest tier — answer is 1-2 sentences over
# pre-fetched snippets, so flash-lite is more than enough and cuts TTFT.
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "gemini-3.1-flash-lite-preview")
# For the live demo we want predictable ~3-5s image gen. The 3.1 preview
# ("Nano Banana Pro") reasons heavily and frequently runs >20s or returns no
# image part. The 2.5 GA model is the original Nano Banana — fast & reliable.
NANO_BANANA_MODEL = os.getenv("NANO_BANANA_MODEL", "gemini-2.5-flash-image")

# Live API (native audio). Only available on regional endpoints (NOT global)
# and only for the gemini-live-2.5-flash-native-audio family today.
LIVE_API_LOCATION = os.getenv("LIVE_API_LOCATION", "us-central1")
LIVE_API_MODEL = os.getenv("LIVE_API_MODEL", "gemini-live-2.5-flash-native-audio")
LIVE_API_VOICE = os.getenv("LIVE_API_VOICE", "Aoede")
LIVE_API_LANGUAGE = os.getenv("LIVE_API_LANGUAGE", "es-US")

DISCOVERY_ENGINE_URL = (
    "https://discoveryengine.googleapis.com/v1alpha"
    f"/projects/{CCLA_DE_PROJECT}/locations/{CCLA_DE_LOCATION}"
    f"/collections/{CCLA_DE_COLLECTION}/engines/{CCLA_DE_ENGINE}"
    f"/servingConfigs/{CCLA_DE_SERVING_CONFIG}:search"
)

ALLOWED_ORIGINS = [
    "http://localhost:5180",
    "http://127.0.0.1:5180",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://caja-los-andes.sonrobots.net",
]

# Path to bundled SPA (set by Dockerfile to /app/static).
SPA_DIR = os.getenv("SPA_DIR", "")


# --------------------------------------------------------------------------- #
# App                                                                          #
# --------------------------------------------------------------------------- #

app = FastAPI(title="CCLA Agentic Pilot Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# /api/ask — preserved (mock benefit-finder)                                   #
# TODO: this still references model "gemini-3-pro-preview" via LlmAgent below; #
# the real model alias should be revisited before production.                  #
# --------------------------------------------------------------------------- #


class BenefitRequest(BaseModel):
    user_type: str
    query: str


class BenefitResponse(BaseModel):
    summary: str
    recommended_action: str


# Define the agent ONLY if ADK is importable (keeps backend bootable in dev
# environments without ADK installed yet).
benefit_agent = None
if LlmAgent is not None:  # pragma: no cover - environment dependent
    try:
        benefit_agent = LlmAgent(
            name="benefit_finder",
            model="gemini-3-pro-preview",  # TODO confirm available alias
            instruction=(
                "You are a helpful assistant for Caja de los Andes members. "
                "Find benefits based on the query and user type."
            ),
            output_schema=BenefitResponse,
            output_key="benefit_data",
        )
    except Exception:
        benefit_agent = None


@app.post("/api/ask")
async def ask_agent(req: BenefitRequest) -> dict[str, str]:
    """Mock benefit-finder. Returns a deterministic placeholder response."""
    return {
        "summary": (
            f"Simulated benefit response for {req.user_type} "
            f"looking for: {req.query}"
        ),
        "recommended_action": (
            "Contact the virtual branch (Sucursal Virtual) for more details."
        ),
    }


# --------------------------------------------------------------------------- #
# /api/search — Vertex AI Search proxy                                         #
# --------------------------------------------------------------------------- #


class SearchRequest(BaseModel):
    query: str
    page_size: int = 10


# Reusable HTTP client for Discovery Engine + GCP metadata (avoids
# per-request TCP+TLS handshake — that handshake was adding 100-300ms to
# every search call).
_HTTP_CLIENT: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        _HTTP_CLIENT = httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=5.0),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=50,
                keepalive_expiry=300.0,
            ),
        )
    return _HTTP_CLIENT


class ClientDisconnected(Exception):
    """Raised when the HTTP client closes the connection mid-request so we can
    short-circuit upstream Discovery Engine calls instead of letting them run
    to completion and burn CPU/quota."""


async def _race_with_disconnect(
    coro: Any, request: Request | None, *, poll: float = 0.1
) -> Any:
    """Await `coro` while polling `request.is_disconnected()`. If the client
    drops first, the coroutine task is cancelled and ClientDisconnected is
    raised. Without this, every aborted keystroke leaves a stale DE call
    running on the backend, contending CPU and DE rate-limit tokens."""
    task = asyncio.create_task(coro)
    if request is None:
        return await task
    try:
        while True:
            done, _ = await asyncio.wait({task}, timeout=poll)
            if task in done:
                return task.result()
            if await request.is_disconnected():
                task.cancel()
                try:
                    await task
                except BaseException:
                    pass
                raise ClientDisconnected()
    except asyncio.CancelledError:
        task.cancel()
        try:
            await task
        except BaseException:
            pass
        raise


# ── Simple in-process LRU cache for /api/search results ───────────────────
# Discovery Engine round-trips are 300ms-1s. While the user types/backspaces,
# the same query often repeats — caching makes those instant. TTL is short
# enough (60s) to stay fresh; LRU bounded so memory can't blow up.
from collections import OrderedDict

_SEARCH_CACHE: "OrderedDict[str, tuple[float, dict[str, Any]]]" = OrderedDict()
_SEARCH_CACHE_MAX = 256
_SEARCH_CACHE_TTL = 60.0


def _search_cache_get(key: str) -> dict[str, Any] | None:
    entry = _SEARCH_CACHE.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        _SEARCH_CACHE.pop(key, None)
        return None
    _SEARCH_CACHE.move_to_end(key)
    return value


def _search_cache_put(key: str, value: dict[str, Any]) -> None:
    _SEARCH_CACHE[key] = (time.time() + _SEARCH_CACHE_TTL, value)
    _SEARCH_CACHE.move_to_end(key)
    while len(_SEARCH_CACHE) > _SEARCH_CACHE_MAX:
        _SEARCH_CACHE.popitem(last=False)


# ── ADC token via Cloud Run metadata server ────────────────────────────────
# On Cloud Run / GCE / GKE the metadata server hands out access tokens for
# the default service account at no network cost beyond one local hop. We
# cache the token in-process and only refresh ~60s before its expiry.
_METADATA_TOKEN_URL = (
    "http://metadata.google.internal/computeMetadata/v1/instance/"
    "service-accounts/default/token"
)
_TOKEN_CACHE: dict[str, Any] = {"token": None, "expires_at": 0.0}
_TOKEN_LOCK = asyncio.Lock()


async def _get_access_token_async() -> str:
    """Return a valid GCP access token. Lock-free fast path when cached;
    one network call to the metadata server only when (re)fetching."""
    now = time.time()
    if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] - now > 60:
        return _TOKEN_CACHE["token"]
    async with _TOKEN_LOCK:
        now = time.time()
        if _TOKEN_CACHE["token"] and _TOKEN_CACHE["expires_at"] - now > 60:
            return _TOKEN_CACHE["token"]
        client = _get_http_client()
        try:
            r = await client.get(
                _METADATA_TOKEN_URL,
                headers={"Metadata-Flavor": "Google"},
                timeout=httpx.Timeout(5.0, connect=2.0),
            )
            r.raise_for_status()
            data = r.json()
        except Exception as exc:
            # Local dev: fall back to google.auth ADC.
            return await asyncio.to_thread(_get_access_token_local_fallback)
        _TOKEN_CACHE["token"] = data["access_token"]
        _TOKEN_CACHE["expires_at"] = now + float(data.get("expires_in", 3600))
        return _TOKEN_CACHE["token"]


def _get_access_token_local_fallback() -> str:
    """ADC path for local development (off Cloud Run). Imported lazily
    so production never pays the import cost."""
    import google.auth
    import google.auth.transport.requests
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not creds.valid:
        creds.refresh(google.auth.transport.requests.Request())
    if creds.token is None:
        raise RuntimeError("Failed to obtain access token from ADC")
    return creds.token


def _get_access_token() -> str:
    """Sync wrapper for callers outside the event loop (e.g. startup)."""
    return _get_access_token_local_fallback()


def _normalize_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Flatten a Discovery-Engine result into what the React UI needs."""
    document = raw.get("document", {}) or {}
    derived = document.get("derivedStructData", {}) or {}
    struct = document.get("structData", {}) or {}

    title = (
        derived.get("title")
        or struct.get("title")
        or document.get("name")
        or "(sin título)"
    )

    snippet = ""
    snippets = derived.get("snippets") or []
    if isinstance(snippets, list) and snippets:
        snippet = snippets[0].get("snippet") or ""
    if not snippet:
        extractive = derived.get("extractive_answers") or derived.get(
            "extractiveAnswers"
        )
        if isinstance(extractive, list) and extractive:
            snippet = extractive[0].get("content", "")
    if not snippet:
        snippet = derived.get("htmlTitle") or struct.get("description") or ""

    link = (
        derived.get("link")
        or derived.get("htmlFormattedUrl")
        or struct.get("link")
        or struct.get("url")
        or ""
    )

    favicon = derived.get("favicon") or struct.get("favicon")

    return {
        "id": document.get("id"),
        "title": title,
        "snippet": snippet,
        "link": link,
        "favicon": favicon,
    }


@app.post("/api/search")
async def search(req: SearchRequest, request: Request) -> dict[str, Any]:
    query = (req.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    cache_key = f"{query.lower()}|{req.page_size}"
    cached = _search_cache_get(cache_key)
    if cached is not None:
        logging.getLogger("andesia.search").info(
            "discovery_engine cache HIT q=%r", query[:50],
        )
        return cached

    try:
        token = await _get_access_token_async()
    except Exception as exc:
        # Surface a clean error so the React UI can render it.
        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo obtener un access token via Application Default "
                f"Credentials: {exc}. Ejecuta `gcloud auth "
                "application-default login` localmente."
            ),
        ) from exc

    payload: dict[str, Any] = {
        "query": query,
        "pageSize": req.page_size,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"},
        "languageCode": "es-CL",
        "userInfo": {"timeZone": "America/Santiago"},
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        client = _get_http_client()
        _t0 = time.perf_counter()
        response = await _race_with_disconnect(
            client.post(DISCOVERY_ENGINE_URL, headers=headers, json=payload),
            request,
        )
        _de_ms = (time.perf_counter() - _t0) * 1000
        logging.getLogger("andesia.search").info(
            "discovery_engine call q=%r ms=%.0f status=%d",
            query[:50], _de_ms, response.status_code,
        )
    except ClientDisconnected:
        logging.getLogger("andesia.search").info(
            "discovery_engine ABORT (client gone) q=%r", query[:50],
        )
        # 499 = nginx/Cloud Run convention for "client closed request".
        raise HTTPException(status_code=499, detail="client disconnected")
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Discovery Engine call failed: {exc}",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Discovery Engine error: {response.text[:400]}",
        )

    data = response.json()
    raw_results = data.get("results", []) or []
    normalized = [_normalize_result(r) for r in raw_results]

    payload_out = {
        "query": query,
        "totalSize": data.get("totalSize", len(normalized)),
        "results": normalized,
    }
    _search_cache_put(cache_key, payload_out)
    return payload_out


# --------------------------------------------------------------------------- #
# /api/chat — live Andesia chat (Gemini streaming via Vertex AI)               #
# --------------------------------------------------------------------------- #


ANDESIA_SYSTEM_INSTRUCTION = """Eres **Andesia**, la asistente IA oficial de **Caja Los Andes**
(caja de compensación de asignación familiar más grande de Chile, con +4M de afiliados).

Tu rol: orientar a afiliados (trabajadores activos y pensionados) sobre los
productos y beneficios de Caja Los Andes, con tono cercano, claro y empático,
en español de Chile.

## Contexto de productos y beneficios (resumen)
- **Crédito social**: principal producto. Tasas competitivas, descuento por planilla. Requiere ser afiliado.
- **Crédito hipotecario**, **automotriz** y **consumo** con tarifas preferentes.
- **Bono Bodas de Oro** (Ley 20.506): bono único para matrimonios que cumplen 50 años, con pago vía CCAF.
- **Asignación familiar**: subsidio mensual por carga reconocida (Ley 18.020).
- **Subsidio de cesantía**: para trabajadores afiliados que pierden su empleo.
- **Beneficios para pensionados**: bonos de invierno, navidad, ayuda médica, recreación.
- **Centros recreacionales / vacaciones**: convenios con hoteles y centros propios (ej. Termas de Jahuel, Olmué).
- **Sucursal Virtual**: portal web/app para trámites en línea.
- **Tapp Caja Los Andes**: billetera/app de pagos.
- **Centro de ayuda**: 600 422 2200 / WhatsApp.

## Reglas de comportamiento
1. **SIEMPRE consulta primero el sitio oficial cajalosandes.cl** vía la herramienta de búsqueda
   integrada (Vertex AI Search) ANTES de responder cualquier pregunta sobre requisitos,
   productos, beneficios, montos, plazos, trámites, oficinas o convenios. No respondas de
   memoria — esos datos cambian. Una vez recibidos los resultados, redacta tu respuesta
   citando las fuentes.
2. **NO inventes números, tasas, montos exactos ni plazos**. Si la búsqueda no los devuelve,
   di que dependen de la evaluación caso a caso y deriva a sucursal virtual o teléfono.
3. **NO asumas datos del afiliado** (RUT, edad, ingreso) si no te los dieron.
4. **Cita marcos legales** cuando aplique (ej. "Ley 20.506 — Bodas de Oro", "Ley 18.020 — Asignación Familiar").
5. Si el afiliado pregunta por un trámite, da los **pasos concretos** (ej. ingresar a sucursal virtual con RUT y clave, ir a sección X, adjuntar documento Y).
6. Si pregunta algo fuera de tu dominio (clima, política, otra empresa), redirige amablemente: "Soy especialista en Caja Los Andes. ¿En qué de tus beneficios puedo ayudarte?".
7. Usa **negritas** para destacar importes clave, fechas y nombres de productos. Usa listas con viñetas cuando enumeres.
8. Sé **breve**: 3-6 oraciones por turno cuando sea posible. Si la consulta exige detalle, divide en bloques claros.
9. Cuando recomiendes una acción (simular crédito, iniciar trámite), invita a continuar en la sucursal virtual.

## Demo en vivo
Esta conversación es parte de una demostración en vivo de capacidades de IA generativa
sobre **Vertex AI / Gemini**. Si el usuario pregunta "¿qué eres?" o similar, puedes
explicar brevemente que eres un agente Gemini desplegado en Vertex AI, con conocimiento
del catálogo de productos y beneficios de Caja Los Andes.
"""


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None  # optional override


def _build_genai_client() -> "genai.Client":  # type: ignore[name-defined]
    if genai is None:
        raise RuntimeError(
            "google-genai no está instalado. Agrega google-genai a pyproject.toml."
        )
    # Vertex AI backend; auth via ADC.
    return genai.Client(
        vertexai=True,
        project=VERTEX_PROJECT,
        location=VERTEX_LOCATION,
    )


def _to_genai_contents(messages: list[ChatMessage]) -> list[Any]:
    """Convert chat history to google-genai Content list."""
    if genai_types is None:
        raise RuntimeError("google-genai types unavailable")
    contents: list[Any] = []
    for m in messages:
        role = "user" if m.role == "user" else "model"
        contents.append(
            genai_types.Content(
                role=role,
                parts=[genai_types.Part.from_text(text=m.content)],
            )
        )
    return contents


def _sse(event_type: str, payload: dict[str, Any]) -> bytes:
    """Encode a single Server-Sent Event frame."""
    body = json.dumps({"type": event_type, **payload}, ensure_ascii=False)
    return f"data: {body}\n\n".encode("utf-8")


def _build_grounding_tools() -> list[Any]:
    """Return both built-in grounding tools: Google Search + Vertex AI Search
    (CCLA cajalosandes.cl engine). Gemini decides which to call per turn."""
    if genai_types is None:
        return []
    tools: list[Any] = []

    # 1) Google Search (built-in, no setup beyond Gemini 3 support)
    try:
        tools.append(genai_types.Tool(google_search=genai_types.GoogleSearch()))
    except Exception:
        pass

    # 2) Vertex AI Search retrieval — grounds answers on the cajalosandes.cl
    #    Discovery Engine app (engine, not raw datastore).
    try:
        engine_path = (
            f"projects/{CCLA_DE_PROJECT}/locations/{CCLA_DE_LOCATION}"
            f"/collections/{CCLA_DE_COLLECTION}/engines/{CCLA_DE_ENGINE}"
        )
        tools.append(
            genai_types.Tool(
                retrieval=genai_types.Retrieval(
                    vertex_ai_search=genai_types.VertexAISearch(engine=engine_path),
                )
            )
        )
    except Exception:
        pass

    return tools


def _emit_grounding_events(chunk: Any) -> list[bytes]:
    """Inspect a streaming chunk for grounding metadata and emit SSE frames
    for any new tool calls / citations / web queries we can surface."""
    out: list[bytes] = []
    candidates = getattr(chunk, "candidates", None) or []
    for cand in candidates:
        gm = getattr(cand, "grounding_metadata", None)
        if not gm:
            continue
        # Web search queries Gemini issued
        for q in (getattr(gm, "web_search_queries", None) or []):
            out.append(_sse("tool_call", {"tool": "google_search", "query": str(q)}))
        # Grounding chunks → citations
        for gc in (getattr(gm, "grounding_chunks", None) or []):
            web = getattr(gc, "web", None)
            ret = getattr(gc, "retrieved_context", None)
            if web is not None:
                out.append(_sse("citation", {
                    "source": "google_search",
                    "title": getattr(web, "title", "") or "",
                    "uri": getattr(web, "uri", "") or "",
                }))
            elif ret is not None:
                out.append(_sse("citation", {
                    "source": "vertex_ai_search",
                    "title": getattr(ret, "title", "") or "Caja Los Andes",
                    "uri": getattr(ret, "uri", "") or "",
                }))
    return out


async def _chat_event_stream(req: ChatRequest) -> AsyncIterator[bytes]:
    """Yield SSE frames: meta, tool_call, citation, text chunks, done (or error)."""
    model_name = (req.model or GEMINI_MODEL).strip()
    yield _sse("meta", {"model": model_name, "backend": "vertex-ai"})

    try:
        client = _build_genai_client()
        contents = _to_genai_contents(req.messages)
        tools = _build_grounding_tools()
        config = genai_types.GenerateContentConfig(  # type: ignore[union-attr]
            system_instruction=ANDESIA_SYSTEM_INSTRUCTION,
            temperature=0.6,
            max_output_tokens=1024,
            tools=tools or None,
        )

        # Track citations so we don't re-emit duplicates as Gemini streams.
        seen_citations: set[str] = set()
        seen_queries: set[str] = set()

        stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield _sse("text", {"text": text})
            for ev in _emit_grounding_events(chunk):
                # rough dedup so we don't flood the inspector
                key = ev.decode("utf-8", "ignore")
                if "tool_call" in key:
                    if key in seen_queries:
                        continue
                    seen_queries.add(key)
                else:
                    if key in seen_citations:
                        continue
                    seen_citations.add(key)
                yield ev

        yield _sse("done", {})
    except Exception as exc:  # pragma: no cover
        yield _sse("error", {"message": str(exc)[:500]})


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")
    if req.messages[-1].role != "user":
        raise HTTPException(
            status_code=400, detail="last message must be from the user"
        )
    return StreamingResponse(
        _chat_event_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


class VitrinaImageRequest(BaseModel):
    prompt: str


@app.post("/api/vitrina/generate")
def vitrina_generate(req: VitrinaImageRequest) -> dict[str, Any]:
    """Generate a Vitrina IA card image with Nano Banana
    (gemini-3.1-flash-image-preview, global region) and return base64 PNG."""
    import base64

    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    client = _build_genai_client()
    # Match user-provided spec: 1K square-ish, all safety OFF, low thinking
    # for demo speed (HIGH costs latency we can't afford on stage).
    safety = [
        genai_types.SafetySetting(category=c, threshold="OFF")
        for c in (
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_HARASSMENT",
        )
    ]
    cfg_kwargs: dict[str, Any] = {
        "temperature": 1,
        "top_p": 0.95,
        "max_output_tokens": 32768,
        "response_modalities": ["TEXT", "IMAGE"],
        "safety_settings": safety,
    }
    # NOTE: image_config + thinking_config are rejected by gemini-3.1-flash-image-preview
    # on the Vertex AI backend (only the direct Gemini API supports them today).
    # Keeping the call to the simpler shape that's known-good in our region.
    config = genai_types.GenerateContentConfig(**cfg_kwargs)  # type: ignore[union-attr]

    img_b64: str | None = None
    mime = "image/png"
    text_out: list[str] = []
    try:
        # Stream so the first image part lands earlier than a blocking call.
        for chunk in client.models.generate_content_stream(
            model=NANO_BANANA_MODEL, contents=prompt, config=config,
        ):
            cand = (chunk.candidates or [None])[0]
            if cand is None or cand.content is None:
                continue
            for part in (cand.content.parts or []):
                inline = getattr(part, "inline_data", None)
                if inline and inline.data and not img_b64:
                    img_b64 = base64.b64encode(inline.data).decode("ascii")
                    mime = inline.mime_type or "image/png"
                if getattr(part, "text", None):
                    text_out.append(part.text)
            if img_b64:
                break
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"nano banana failed: {exc}")

    if not img_b64:
        raise HTTPException(
            status_code=502,
            detail=f"no image returned (text='{' '.join(text_out)[:200]}')",
        )
    return {
        "model": NANO_BANANA_MODEL,
        "mime": mime,
        "image_b64": img_b64,
        "prompt": prompt,
    }


# --------------------------------------------------------------------------- #
# /api/live — bidirectional WebSocket bridge to Gemini Live API (native audio) #
# --------------------------------------------------------------------------- #
#
# Wire protocol (browser <-> this endpoint):
#   client -> server BINARY frames    : raw PCM 16-bit LE @ 16 kHz mic chunks
#   client -> server TEXT frames      : JSON control messages
#       {"type":"text","text":"..."}        send a text turn
#       {"type":"end_turn"}                  signal end of audio turn
#   server -> client BINARY frames    : raw PCM 16-bit LE @ 24 kHz tts chunks
#   server -> client TEXT frames      : JSON events
#       {"type":"meta","model":..., "voice":..., "language":...}
#       {"type":"input_transcript","text":"..."}
#       {"type":"output_transcript","text":"..."}
#       {"type":"turn_complete"}
#       {"type":"interrupted"}
#       {"type":"error","message":"..."}


def _build_live_client() -> "genai.Client":  # type: ignore[name-defined]
    """Live API needs a regional Vertex endpoint (global isn't supported)."""
    if genai is None:
        raise RuntimeError("google-genai not installed")
    return genai.Client(
        vertexai=True,
        project=VERTEX_PROJECT,
        location=LIVE_API_LOCATION,
    )


@app.websocket("/api/live")
async def live_ws(ws: WebSocket) -> None:
    await ws.accept()
    sid = uuid.uuid4().hex[:8]
    log = logging.getLogger("andesia.live")
    # Toggle from the client (query string, e.g. /api/live?grounding=1).
    # When enabled, Andesia voz cita fuentes reales de cajalosandes.cl /
    # google search; cuesta ~700ms-1.5s extra al primer audio en turnos
    # que disparan la herramienta.
    grounding_on = (ws.query_params.get("grounding") or "").lower() in {"1", "true", "on", "yes"}
    log.info("[live %s] accept peer=%s grounding=%s", sid, ws.client, grounding_on)

    if genai is None or genai_types is None:
        await ws.send_json({"type": "error", "message": "google-genai not installed"})
        await ws.close()
        return

    cfg_kwargs: dict[str, Any] = dict(
        response_modalities=["AUDIO"],
        speech_config=genai_types.SpeechConfig(
            voice_config=genai_types.VoiceConfig(
                prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                    voice_name=LIVE_API_VOICE,
                ),
            ),
            language_code=LIVE_API_LANGUAGE,
        ),
        system_instruction=ANDESIA_SYSTEM_INSTRUCTION,
        # Closed-caption transcripts both ways for the on-screen overlay.
        input_audio_transcription=genai_types.AudioTranscriptionConfig(),
        output_audio_transcription=genai_types.AudioTranscriptionConfig(),
    )
    if grounding_on:
        tools = _build_grounding_tools()
        if tools:
            cfg_kwargs["tools"] = tools
    config = genai_types.LiveConnectConfig(**cfg_kwargs)

    try:
        client = _build_live_client()
    except Exception as exc:
        await ws.send_json({"type": "error", "message": f"client init failed: {exc}"})
        await ws.close()
        return

    try:
        async with client.aio.live.connect(model=LIVE_API_MODEL, config=config) as session:
            log.info("[live %s] upstream connected model=%s voice=%s",
                     sid, LIVE_API_MODEL, LIVE_API_VOICE)
            await ws.send_json({
                "type": "meta",
                "model": LIVE_API_MODEL,
                "voice": LIVE_API_VOICE,
                "language": LIVE_API_LANGUAGE,
                "input_sample_rate": 16000,
                "output_sample_rate": 24000,
                "grounding": grounding_on,
                "sid": sid,
            })

            # rolling counters for log heartbeat
            stats = {"in_bytes": 0, "in_chunks": 0,
                     "out_bytes": 0, "out_chunks": 0,
                     "in_tx": 0, "out_tx": 0,
                     "turns": 0, "interrupts": 0}

            async def heartbeat() -> None:
                while True:
                    await asyncio.sleep(5.0)
                    log.info(
                        "[live %s] HB in=%d/%d out=%d/%d in_tx=%d out_tx=%d turns=%d int=%d",
                        sid, stats["in_chunks"], stats["in_bytes"],
                        stats["out_chunks"], stats["out_bytes"],
                        stats["in_tx"], stats["out_tx"],
                        stats["turns"], stats["interrupts"],
                    )

            async def pump_client_to_session() -> None:
                while True:
                    msg = await ws.receive()
                    if msg.get("type") == "websocket.disconnect":
                        log.info("[live %s] client disconnect", sid)
                        return
                    if (data := msg.get("bytes")) is not None:
                        stats["in_bytes"] += len(data)
                        stats["in_chunks"] += 1
                        try:
                            await session.send_realtime_input(
                                audio=genai_types.Blob(
                                    data=data,
                                    mime_type="audio/pcm;rate=16000",
                                )
                            )
                        except Exception as exc:
                            log.exception("[live %s] send_realtime_input failed: %s", sid, exc)
                            raise
                    elif (text := msg.get("text")) is not None:
                        try:
                            payload = json.loads(text)
                        except Exception:
                            continue
                        kind = payload.get("type")
                        log.info("[live %s] client TEXT kind=%s", sid, kind)
                        if kind == "text":
                            await session.send_client_content(
                                turns=genai_types.Content(
                                    role="user",
                                    parts=[
                                        genai_types.Part.from_text(
                                            text=str(payload.get("text", ""))
                                        )
                                    ],
                                ),
                                turn_complete=True,
                            )
                        elif kind == "end_turn":
                            try:
                                await session.send_realtime_input(audio_stream_end=True)
                            except TypeError:
                                pass

            # Dedup keys for grounding events so we don't spam the client when
            # the same chunk shows up across multiple model_turn fragments.
            seen_grounding: set[str] = set()

            async def emit_grounding_from_server_content(sc: Any) -> None:
                """Pull web_search_queries + grounding_chunks off a server_content
                payload and forward to the client as compact events. The Live API
                attaches grounding_metadata to server_content (not to candidates
                like in /api/chat) — different shape."""
                gm = getattr(sc, "grounding_metadata", None)
                if gm is None:
                    return
                queries = list(getattr(gm, "web_search_queries", None) or [])
                for q in queries:
                    qstr = str(q).strip()
                    if not qstr:
                        continue
                    key = f"q::{qstr}"
                    if key in seen_grounding:
                        continue
                    seen_grounding.add(key)
                    await ws.send_json({"type": "tool_call", "tool": "google_search", "query": qstr})
                for gc in (getattr(gm, "grounding_chunks", None) or []):
                    web = getattr(gc, "web", None)
                    ret = getattr(gc, "retrieved_context", None)
                    if web is not None:
                        uri = str(getattr(web, "uri", "") or "")
                        title = str(getattr(web, "title", "") or "")
                        key = f"w::{uri}::{title}"
                        if key in seen_grounding:
                            continue
                        seen_grounding.add(key)
                        await ws.send_json({
                            "type": "grounding_chunk",
                            "kind": "web",
                            "uri": uri,
                            "title": title or uri,
                        })
                    elif ret is not None:
                        uri = str(getattr(ret, "uri", "") or "")
                        title = str(getattr(ret, "title", "") or "")
                        text = str(getattr(ret, "text", "") or "")
                        key = f"r::{uri}::{title}"
                        if key in seen_grounding:
                            continue
                        seen_grounding.add(key)
                        await ws.send_json({
                            "type": "grounding_chunk",
                            "kind": "corpus",
                            "uri": uri,
                            "title": title or "Caja Los Andes corpus",
                            # Short hover/preview snippet for the side panel.
                            "snippet": text[:280],
                            # Full extracted text used by Gemini for grounding.
                            # Capped at 4000 chars so we don't blow up the WS.
                            "text": text[:4000],
                        })

            async def pump_session_to_client() -> None:
                # session.receive() yields ONE turn then completes. We must
                # re-enter it for every subsequent user turn, otherwise the
                # session stays alive on the wire but Gemini stops processing
                # incoming mic audio and the WS dies on keepalive timeout.
                while True:
                    turn_started = stats["turns"]
                    async for response in session.receive():
                        sc = getattr(response, "server_content", None)
                        if sc is not None:
                            await emit_grounding_from_server_content(sc)
                            in_t = getattr(sc, "input_transcription", None)
                            out_t = getattr(sc, "output_transcription", None)
                            if in_t is not None and getattr(in_t, "text", None):
                                stats["in_tx"] += 1
                                log.info("[live %s] input_tx=%r", sid, in_t.text[:80])
                                await ws.send_json({"type": "input_transcript", "text": in_t.text})
                            if out_t is not None and getattr(out_t, "text", None):
                                stats["out_tx"] += 1
                                await ws.send_json({"type": "output_transcript", "text": out_t.text})
                            if getattr(sc, "interrupted", False):
                                stats["interrupts"] += 1
                                log.info("[live %s] interrupted", sid)
                                await ws.send_json({"type": "interrupted"})
                            if getattr(sc, "turn_complete", False):
                                stats["turns"] += 1
                                log.info("[live %s] turn_complete (#%d)", sid, stats["turns"])
                                await ws.send_json({"type": "turn_complete"})
                        if (audio := getattr(response, "data", None)) is not None:
                            stats["out_bytes"] += len(audio)
                            stats["out_chunks"] += 1
                            await ws.send_bytes(audio)
                    log.info(
                        "[live %s] receive() iterator ended after turn #%d; re-entering",
                        sid, stats["turns"],
                    )
                    if stats["turns"] == turn_started:
                        # Iterator ended without a turn_complete — upstream
                        # likely closed. Bail out so gather propagates.
                        log.info("[live %s] upstream closed without turn_complete; exiting", sid)
                        return

            hb_task = asyncio.create_task(heartbeat())
            try:
                await asyncio.gather(
                    pump_client_to_session(),
                    pump_session_to_client(),
                )
            finally:
                hb_task.cancel()
                log.info("[live %s] FINAL stats=%s", sid, stats)
    except WebSocketDisconnect:
        log.info("[live %s] WebSocketDisconnect", sid)
        return
    except Exception as exc:
        log.exception("[live %s] fatal: %s", sid, exc)
        try:
            await ws.send_json({"type": "error", "message": str(exc)[:500]})
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# /api/suggest — predicted full questions while user types                     #
# --------------------------------------------------------------------------- #


class SuggestRequest(BaseModel):
    partial: str
    max: int = 3


SUGGEST_SYSTEM = """Eres el motor de autocompletar del buscador de Caja Los Andes.
Devuelves preguntas completas cortas (<=10 palabras), naturales, en español de
Chile, sobre productos/beneficios de Caja Los Andes (créditos, asignación
familiar, bono Bodas de Oro, sucursal virtual, turismo, seguros, pensionados,
licencias médicas).

REGLAS DE FORMATO ESTRICTAS — sigue al pie de la letra:
- UNA pregunta por línea
- NADA de viñetas (sin "*", "-", "•", "·"), NADA de numeración (sin "1.")
- NADA de texto introductorio, NADA de comillas, NADA de markdown
- Cada línea debe terminar con "?"
- Devuelve EXACTAMENTE {n} líneas, ni una más
- Nunca inventes datos numéricos en las preguntas
"""


@app.post("/api/suggest")
async def suggest(req: SuggestRequest) -> dict[str, Any]:
    partial = (req.partial or "").strip()
    n = max(1, min(5, req.max))
    if not partial:
        return {"suggestions": [
            "¿Qué tasa tiene el crédito social?",
            "¿Cómo solicito el bono Bodas de Oro?",
            "¿Cuánto recibo por asignación familiar?",
        ][:n]}

    if genai is None or genai_types is None:
        return {"suggestions": []}

    try:
        client = _build_genai_client()
        # Gemini 3 thinking eats output tokens by default — for autocomplete
        # we want fast, no-thinking output.
        cfg_args: dict[str, Any] = {
            "system_instruction": SUGGEST_SYSTEM.replace("{n}", str(n)),
            "temperature": 0.4,
            "max_output_tokens": 400,
        }
        try:
            cfg_args["thinking_config"] = genai_types.ThinkingConfig(thinking_level="LOW")
        except Exception:
            pass
        config = genai_types.GenerateContentConfig(**cfg_args)
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f'parcial: "{partial}"',
            config=config,
        )
        raw = (resp.text or "").strip()
        suggestions: list[str] = []
        import re
        for ln in raw.splitlines():
            s = ln.strip()
            if not s:
                continue
            # strip leading bullets / numbering / quotes
            s = re.sub(r"^[\s\*\-\•\·\d\.\)]+", "", s)
            s = s.strip(" \"'`*").strip()
            if len(s) < 4 or "?" not in s:
                continue
            suggestions.append(s)
            if len(suggestions) >= n:
                break
        return {"suggestions": suggestions[:n]}
    except Exception as exc:
        return {"suggestions": [], "error": str(exc)[:200]}


# --------------------------------------------------------------------------- #
# /api/search/answer — AI Overview: streams a 1-paragraph answer with cites   #
# --------------------------------------------------------------------------- #


class SearchAnswerRequest(BaseModel):
    query: str


SEARCH_ANSWER_SYSTEM = """Eres "AI Overview" del buscador de Caja Los Andes.
Recibes una consulta y fragmentos numerados [1], [2]… de cajalosandes.cl.

REGLAS ESTRICTAS:
- Responde en MÁXIMO 2 oraciones, español de Chile, tono claro y directo.
- Cita SIEMPRE con [n] inline al usar un dato concreto.
- Cero markdown, cero listas, cero encabezados — solo prosa breve.
- Nada de "Según el sitio…", "Caja Los Andes ofrece…", ni preámbulos.
- Si los fragmentos no responden, di en una frase que conviene revisar la
  sucursal virtual o llamar al 600 4222 200.
- Nunca inventes montos, tasas, plazos ni requisitos no presentes en los fragmentos.
"""


async def _search_answer_stream(
    req: SearchAnswerRequest, request: Request | None = None
) -> AsyncIterator[bytes]:
    query = (req.query or "").strip()
    if not query:
        yield _sse("error", {"message": "query vacío"})
        return

    # 1) hit Discovery Engine first to grab top snippets
    try:
        token = await _get_access_token_async()
        payload = {
            "query": query, "pageSize": 5,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "languageCode": "es-CL",
            "userInfo": {"timeZone": "America/Santiago"},
        }
        client_http = _get_http_client()
        r = await _race_with_disconnect(
            client_http.post(
                DISCOVERY_ENGINE_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
            ),
            request,
        )
        raw_results = (r.json().get("results", []) or [])[:5]
        normalized = [_normalize_result(x) for x in raw_results]
    except ClientDisconnected:
        logging.getLogger("andesia.search").info(
            "answer ABORT (client gone before DE) q=%r", query[:50],
        )
        return
    except Exception as exc:
        yield _sse("error", {"message": f"search failed: {exc}"})
        return

    # 2) emit citations index up front so the UI can pre-render badges
    cites: list[dict[str, Any]] = []
    for i, n in enumerate(normalized, start=1):
        cites.append({
            "n": i,
            "title": n.get("title", ""),
            "link": n.get("link", ""),
        })
    yield _sse("citations", {"items": cites})

    if not normalized:
        yield _sse("text", {"text": "No encontré contenido en cajalosandes.cl que responda eso. Intenta con otras palabras o explora la navegación principal."})
        yield _sse("done", {})
        return

    # 3) stream Gemini answer grounded on those snippets
    if genai is None or genai_types is None:
        yield _sse("error", {"message": "google-genai no disponible"})
        return

    context_lines = []
    for i, n in enumerate(normalized, start=1):
        snippet = (n.get("snippet") or "").replace("\n", " ").strip()
        title = n.get("title", "")
        context_lines.append(f"[{i}] {title} — {snippet}")
    context = "\n".join(context_lines)

    user_prompt = f"Consulta: {query}\n\nFragmentos:\n{context}"

    try:
        client = _build_genai_client()
        cfg_args: dict[str, Any] = {
            "system_instruction": SEARCH_ANSWER_SYSTEM,
            "temperature": 0.2,
            "max_output_tokens": 256,
        }
        # flash-lite ignores thinking_config but we set LOW just in case the env
        # is overridden back to a thinking model.
        try:
            cfg_args["thinking_config"] = genai_types.ThinkingConfig(thinking_level="LOW")
        except Exception:
            pass
        config = genai_types.GenerateContentConfig(**cfg_args)
        stream = client.models.generate_content_stream(
            model=ANSWER_MODEL, contents=user_prompt, config=config,
        )
        for chunk in stream:
            if chunk.text:
                yield _sse("text", {"text": chunk.text})
        yield _sse("done", {})
    except Exception as exc:
        yield _sse("error", {"message": str(exc)[:300]})


@app.post("/api/search/answer")
async def search_answer(
    req: SearchAnswerRequest, request: Request
) -> StreamingResponse:
    return StreamingResponse(
        _search_answer_stream(req, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --------------------------------------------------------------------------- #
# /api/extract — Gemini 3 Flash document understanding                         #
# Sends the user's uploaded file (image or PDF) directly to Gemini and asks    #
# for a structured JSON of fields. No DocAI / no Vision — Gemini multimodal    #
# handles OCR + entity extraction in one call.                                 #
# --------------------------------------------------------------------------- #


EXTRACT_MODEL = os.getenv("EXTRACT_MODEL", "gemini-3-flash-preview")
EXTRACT_MAX_BYTES = int(os.getenv("EXTRACT_MAX_BYTES", str(15 * 1024 * 1024)))


class _ExtractField(BaseModel):
    label: str
    value: str
    confidence: float = 0.9
    category: str | None = None


class _ExtractTotal(BaseModel):
    label: str
    value: str
    confidence: float = 0.9


class _ExtractSchema(BaseModel):
    """Strict schema we hand to Gemini to force a parseable JSON shape — beats
    relying on system-prompt instructions, which can drift with long docs."""

    doc_type: str
    summary: str
    fields: list[_ExtractField]
    totals: list[_ExtractTotal] = []
    warnings: list[str] = []


def _coerce_json_text(text: str) -> Any:
    """Best-effort JSON parser. Strips ```json fences, finds the outermost
    braces, and as a last resort escapes lone control chars. Raises ValueError
    if nothing works."""
    if not text:
        raise ValueError("empty text")
    s = text.strip()
    # Strip markdown fences if Gemini added them despite response_mime_type.
    if s.startswith("```"):
        s = s.strip("`")
        # remove leading "json" tag if present
        if s.lower().startswith("json"):
            s = s[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # Carve out the largest balanced {...} substring.
    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        candidate = s[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Strip raw control chars (newlines/tabs INSIDE strings break json).
            cleaned = "".join(
                ch if (ch >= " " or ch in ("\n", "\r", "\t")) else " "
                for ch in candidate
            )
            # Replace literal newlines INSIDE quoted strings with \n. Cheap
            # heuristic: just collapse all bare \n inside strings to spaces.
            return json.loads(cleaned.replace("\n", " ").replace("\r", " ").replace("\t", " "))
    raise ValueError("no JSON object found in model output")

EXTRACT_SYSTEM_INSTRUCTION = """Eres un experto en extracción de datos estructurados
de documentos administrativos chilenos (liquidaciones de pensión, licencias médicas,
cédulas de identidad, certificados, formularios, comprobantes, contratos, recibos).

Recibirás UN documento (imagen o PDF). Devuelve EXCLUSIVAMENTE un JSON válido con la
forma:

{
  "doc_type": "<tipo de documento, ej: 'Liquidación de pensión IPS', 'Cédula de identidad', 'Comprobante bancario'>",
  "summary": "<una línea, máx 120 chars, describiendo el documento>",
  "fields": [
    {"label": "<nombre legible del campo en español>", "value": "<valor extraído tal cual>", "confidence": <float 0-1>, "category": "identidad|monetario|fecha|documento|otro"}
  ],
  "totals": [
    {"label": "<ej: 'Líquido a pagar'>", "value": "<ej: '$ 487.320'>", "confidence": <float>}
  ],
  "warnings": ["<string solo si hay algo importante: doc cortado, ilegible, mismatch>"]
}

Reglas:
- Mantén los valores en su formato original (ej. "12.345.678-5", "$ 542.800", "MARZO 2026").
- "fields" debe tener entre 6 y 20 entradas representativas (lo más relevante).
- "totals" solo si aplica (montos finales, saldos, totales). Vacío [] si no.
- "warnings" puede ir vacío [].
- Confidence honesta: 0.95+ solo si el dato es claramente legible.
- NO incluyas explicaciones fuera del JSON. NO uses bloques markdown ```json. Solo el JSON."""


@app.post("/api/extract")
async def extract_document(file: UploadFile = File(...)) -> dict[str, Any]:
    if genai is None or genai_types is None:
        raise HTTPException(status_code=503, detail="google-genai not installed")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty file")
    if len(raw) > EXTRACT_MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"file too large (>{EXTRACT_MAX_BYTES} bytes)")

    mime = (file.content_type or "").lower()
    # Browsers sometimes send octet-stream — sniff a couple of common cases.
    if not mime or mime == "application/octet-stream":
        if raw[:4] == b"%PDF":
            mime = "application/pdf"
        elif raw[:3] == b"\xff\xd8\xff":
            mime = "image/jpeg"
        elif raw[:8] == b"\x89PNG\r\n\x1a\n":
            mime = "image/png"
        else:
            mime = "application/pdf"  # safe default for the demo

    log = logging.getLogger("andesia.extract")
    log.info("extract filename=%s mime=%s bytes=%d model=%s", file.filename, mime, len(raw), EXTRACT_MODEL)

    t0 = time.monotonic()
    try:
        client = _build_genai_client()
        contents = [
            genai_types.Content(  # type: ignore[union-attr]
                role="user",
                parts=[
                    genai_types.Part.from_bytes(data=raw, mime_type=mime),  # type: ignore[union-attr]
                    genai_types.Part.from_text(text="Extrae los datos estructurados del documento adjunto siguiendo el JSON schema indicado."),  # type: ignore[union-attr]
                ],
            )
        ]
        config = genai_types.GenerateContentConfig(  # type: ignore[union-attr]
            system_instruction=EXTRACT_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=_ExtractSchema,
            temperature=0.0,
            max_output_tokens=4096,
        )
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=EXTRACT_MODEL,
            contents=contents,
            config=config,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        # Prefer the parsed pydantic instance google-genai exposes when we pass
        # a response_schema — bypasses the JSON parse step entirely. Falls back
        # to text + lenient JSON parsing if .parsed isn't populated.
        parsed_obj = getattr(resp, "parsed", None)
        if parsed_obj is not None and hasattr(parsed_obj, "model_dump"):
            parsed = parsed_obj.model_dump()
        else:
            text = (getattr(resp, "text", None) or "").strip()
            if not text:
                raise HTTPException(status_code=502, detail="empty model response")
            try:
                parsed = _coerce_json_text(text)
            except (ValueError, json.JSONDecodeError) as parse_err:
                log.warning("extract JSON parse failed: %s | head=%r", parse_err, text[:300])
                raise HTTPException(
                    status_code=502,
                    detail=f"model returned non-JSON: {str(parse_err)[:120]}",
                )
        return {
            "filename": file.filename,
            "mime": mime,
            "bytes": len(raw),
            "elapsed_ms": elapsed_ms,
            "model": EXTRACT_MODEL,
            "extraction": parsed,
        }
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("extract failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)[:500])


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# --------------------------------------------------------------------------- #
# Static SPA mount (production only — Dockerfile sets SPA_DIR=/app/static)     #
# Mounted last so /api/* takes precedence.                                     #
# --------------------------------------------------------------------------- #


if SPA_DIR and os.path.isdir(SPA_DIR):
    _spa_index = os.path.join(SPA_DIR, "index.html")

    # Serve the built assets at /assets/* etc.
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(SPA_DIR, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        # Try a real file first (favicon, fonts, icons, images at root).
        candidate = os.path.join(SPA_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        # Otherwise hand the SPA shell back so React Router (or future routes) work.
        return FileResponse(_spa_index)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
