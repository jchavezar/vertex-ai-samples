"""Vector search over the Firestore knowledge base populated by pipeline/."""
from __future__ import annotations

import os
from functools import lru_cache

from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

PROJECT = os.environ.get("FIRESTORE_PROJECT", "sharepoint-wif")
COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "mcp_docs")
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
    """Embed the query, run Firestore find_nearest, return chunks with PDF citations."""
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
        results.append({
            "id": doc.id,
            "text": data.get("text", ""),
            "pdf_name": data.get("pdf_name", ""),
            "page": data.get("page"),
            "pdf_uri": data.get("pdf_uri", ""),
            "citation": f"{data.get('pdf_name', 'doc')} — p.{data.get('page', '?')}",
        })
    return results


def list_pdfs() -> list[dict]:
    """Return distinct PDFs in the collection (name, gs uri, page count)."""
    pdfs: dict[str, dict] = {}
    for doc in _db().collection(COLLECTION).stream():
        data = doc.to_dict()
        name = data.get("pdf_name", "unknown")
        entry = pdfs.setdefault(name, {"pdf_name": name, "pdf_uri": data.get("pdf_uri", ""), "pages": 0})
        entry["pages"] += 1
    return sorted(pdfs.values(), key=lambda x: x["pdf_name"])
