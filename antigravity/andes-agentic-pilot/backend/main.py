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

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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


# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #

CCLA_DE_PROJECT = os.getenv("CCLA_DE_PROJECT", "254356041555")
CCLA_DE_ENGINE = os.getenv("CCLA_DE_ENGINE", "caja-los-andes_1776511755096")
CCLA_DE_LOCATION = os.getenv("CCLA_DE_LOCATION", "global")
CCLA_DE_COLLECTION = os.getenv("CCLA_DE_COLLECTION", "default_collection")
CCLA_DE_SERVING_CONFIG = os.getenv("CCLA_DE_SERVING_CONFIG", "default_search")

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


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
