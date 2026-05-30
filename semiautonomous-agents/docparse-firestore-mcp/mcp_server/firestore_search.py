"""Vector search engine over Firestore knowledge base for the MCP Server.

Retrieves page-level chunks with rich metadata and full PDF grounding links for Gemini Enterprise.
"""
from __future__ import annotations

import os
from functools import lru_cache

from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

PROJECT = os.environ.get("FIRESTORE_PROJECT", "sharepoint-wif")
COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-005")


@lru_cache(maxsize=1)
def _genai_client() -> genai.Client:
    return genai.Client(vertexai=True, project=PROJECT, location="global")


@lru_cache(maxsize=1)
def _db() -> firestore.Client:
    return firestore.Client(project=PROJECT)


def _embed(query: str) -> list[float]:
    resp = _genai_client().models.embed_content(model=EMBED_MODEL, contents=query)
    return resp.embeddings[0].values


def vector_search(query: str, top_k: int = 5) -> list[dict]:
    """Embeds user query and runs a nearest-neighbor vector search in Firestore.

    Args:
        query: User search query.
        top_k: Number of chunks to return (1-25).

    Returns:
        List of chunks with rich grounding metadata (GCS URIs, HTTPS links, etc.)
    """
    if top_k < 1 or top_k > 25:
        top_k = 5

    embedding = _embed(query)
    vector_query = _db().collection(COLLECTION).find_nearest(
        vector_field="embedding",
        query_vector=embedding,
        distance_measure=DistanceMeasure.COSINE,
        limit=top_k,
    )

    results = []
    for doc in vector_query.get():
        data = doc.to_dict()
        
        # Pull rich metadata fields
        pdf_name = data.get("pdf_name", "unknown")
        page = data.get("page", "?")
        gcs_pdf_uri = data.get("gcs_pdf_uri", "")
        https_pdf_url = data.get("https_pdf_url", "")
        page_position = data.get("page_position", {})

        results.append({
            "id": doc.id,
            "text": data.get("text", ""),
            "pdf_name": pdf_name,
            "page": page,
            "gcs_pdf_uri": gcs_pdf_uri,
            "https_pdf_url": https_pdf_url,
            "page_position": page_position,
            "citation": f"{pdf_name} — Page {page} ({page_position.get('label', 'unspecified')})",
        })
    return results


def list_pdfs() -> list[dict]:
    """Enumerate distinct PDFs indexed in Firestore with page-level stats."""
    pdfs: dict[str, dict] = {}
    for doc in _db().collection(COLLECTION).stream():
        data = doc.to_dict()
        name = data.get("pdf_name", "unknown")
        entry = pdfs.setdefault(name, {
            "pdf_name": name,
            "gcs_pdf_uri": data.get("gcs_pdf_uri", ""),
            "https_pdf_url": data.get("https_pdf_url", "").split("#")[0] if "https_pdf_url" in data else "",
            "pages": 0
        })
        entry["pages"] += 1
    return sorted(pdfs.values(), key=lambda x: x["pdf_name"])
