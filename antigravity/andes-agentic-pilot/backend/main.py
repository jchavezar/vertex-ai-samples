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

import json
import os
from typing import Any, AsyncIterator, Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT", "vtxdemos")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

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
]


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


def _get_access_token() -> str:
    """Obtain an OAuth2 token via Application Default Credentials.

    In dev, run once: `gcloud auth application-default login`.
    On Cloud Run / GCE / GKE the metadata server provides it automatically.
    """
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(google.auth.transport.requests.Request())
    if credentials.token is None:
        raise RuntimeError("Failed to obtain access token from ADC")
    return credentials.token


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
async def search(req: SearchRequest) -> dict[str, Any]:
    query = (req.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    try:
        token = _get_access_token()
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
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                DISCOVERY_ENGINE_URL,
                headers=headers,
                json=payload,
            )
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

    return {
        "query": query,
        "totalSize": data.get("totalSize", len(normalized)),
        "results": normalized,
    }


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
1. **NO inventes números, tasas, montos exactos ni plazos**. Si no los tienes, di que dependen de la evaluación caso a caso y deriva a sucursal virtual o teléfono.
2. **NO asumas datos del afiliado** (RUT, edad, ingreso) si no te los dieron.
3. **Cita marcos legales** cuando aplique (ej. "Ley 20.506 — Bodas de Oro", "Ley 18.020 — Asignación Familiar").
4. Si el afiliado pregunta por un trámite, da los **pasos concretos** (ej. ingresar a sucursal virtual con RUT y clave, ir a sección X, adjuntar documento Y).
5. Si pregunta algo fuera de tu dominio (clima, política, otra empresa), redirige amablemente: "Soy especialista en Caja Los Andes. ¿En qué de tus beneficios puedo ayudarte?".
6. Usa **negritas** para destacar importes clave, fechas y nombres de productos. Usa listas con viñetas cuando enumeres.
7. Sé **breve**: 3-6 oraciones por turno cuando sea posible. Si la consulta exige detalle, divide en bloques claros.
8. Cuando recomiendes una acción (simular crédito, iniciar trámite), invita a continuar en la sucursal virtual.

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


async def _chat_event_stream(req: ChatRequest) -> AsyncIterator[bytes]:
    """Yield SSE frames: meta, text chunks, done (or error)."""
    model_name = (req.model or GEMINI_MODEL).strip()
    yield _sse("meta", {"model": model_name, "backend": "vertex-ai"})

    try:
        client = _build_genai_client()
        contents = _to_genai_contents(req.messages)
        config = genai_types.GenerateContentConfig(  # type: ignore[union-attr]
            system_instruction=ANDESIA_SYSTEM_INSTRUCTION,
            temperature=0.6,
            max_output_tokens=1024,
        )

        # google-genai exposes a sync iterator for streaming. We yield from it.
        stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield _sse("text", {"text": text})

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


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
