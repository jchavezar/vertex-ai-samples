"""Vector search engine over Firestore knowledge base for the MCP Server.

Retrieves page-level chunks with rich metadata and full PDF grounding links for Gemini Enterprise.
"""
from __future__ import annotations

import os
from functools import lru_cache

from google import genai
from google.cloud import firestore
from google.cloud.firestore import FieldFilter
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


def vector_search(query: str, page: str | None = None, pdf_name: str | None = None, top_k: int = 5) -> list[dict]:
    """Retrieves relevant chunks from Firestore, supporting hybrid direct page queries and semantic vector search.

    Args:
        query: User search query.
        page: Optional logical/printed page number filter.
        pdf_name: Optional document name substring filter.
        top_k: Number of chunks to return (1-25).

    Returns:
        List of chunks with rich grounding metadata (GCS URIs, HTTPS links, etc.)
    """
    if top_k < 1 or top_k > 25:
        top_k = 5

    results = []

    # Case 1: If page is specified, run direct query lookup (bypassing vector embeddings)
    if page:
        page = str(page).strip()
        # Query 1: try matching printed_page (e.g. printed_page == '1' or 'ix')
        q1 = _db().collection(COLLECTION).where(filter=FieldFilter("printed_page", "==", page))
        docs = list(q1.get())

        # Query 2: fallback to physical page integer if page consists only of digits.
        # We query both in parallel and combine, rather than skipping, because printed_page
        # mapping might match for one PDF but fail/be empty for another target PDF.
        if page.isdigit():
            q2 = _db().collection(COLLECTION).where(filter=FieldFilter("page", "==", int(page)))
            docs_physical = list(q2.get())
            # Combine preserving order, avoiding duplicates by document ID
            seen_ids = {d.id for d in docs}
            for d in docs_physical:
                if d.id not in seen_ids:
                    docs.append(d)

        for doc in docs:
            data = doc.to_dict()
            doc_pdf_name = data.get("pdf_name", "")
            
            # Apply pdf_name substring filter in Python if specified
            if pdf_name and pdf_name.lower() not in doc_pdf_name.lower():
                continue

            pdf_name_val = data.get("pdf_name", "unknown")
            page_val = data.get("page", "?")
            printed_page_val = data.get("printed_page", "")
            gcs_pdf_uri = data.get("gcs_pdf_uri", "")
            https_pdf_url = data.get("https_pdf_url", "")
            page_position = data.get("page_position", {})

            # Format citation with logical printed page if available
            logical_page_str = f"Page {page_val} (Printed: {printed_page_val})" if printed_page_val else f"Page {page_val}"
            results.append({
                "id": doc.id,
                "text": data.get("text", ""),
                "pdf_name": pdf_name_val,
                "page": page_val,
                "printed_page": printed_page_val,
                "gcs_pdf_uri": gcs_pdf_uri,
                "https_pdf_url": https_pdf_url,
                "page_position": page_position,
                "citation": f"{pdf_name_val} — {logical_page_str} ({page_position.get('label', 'unspecified')})",
            })
        return results[:top_k]

    # Case 2: If page is NOT specified, run standard vector search
    embedding = _embed(query)
    # If pdf_name filter is specified, fetch more results to perform post-filtering
    fetch_limit = 25 if pdf_name else top_k
    vector_query = _db().collection(COLLECTION).find_nearest(
        vector_field="embedding",
        query_vector=embedding,
        distance_measure=DistanceMeasure.COSINE,
        limit=fetch_limit,
    )

    for doc in vector_query.get():
        data = doc.to_dict()
        doc_pdf_name = data.get("pdf_name", "")

        # Apply pdf_name substring filter in Python if specified
        if pdf_name and pdf_name.lower() not in doc_pdf_name.lower():
            continue

        pdf_name_val = data.get("pdf_name", "unknown")
        page_val = data.get("page", "?")
        printed_page_val = data.get("printed_page", "")
        gcs_pdf_uri = data.get("gcs_pdf_uri", "")
        https_pdf_url = data.get("https_pdf_url", "")
        page_position = data.get("page_position", {})

        logical_page_str = f"Page {page_val} (Printed: {printed_page_val})" if printed_page_val else f"Page {page_val}"
        results.append({
            "id": doc.id,
            "text": data.get("text", ""),
            "pdf_name": pdf_name_val,
            "page": page_val,
            "printed_page": printed_page_val,
            "gcs_pdf_uri": gcs_pdf_uri,
            "https_pdf_url": https_pdf_url,
            "page_position": page_position,
            "citation": f"{pdf_name_val} — {logical_page_str} ({page_position.get('label', 'unspecified')})",
        })
        if len(results) >= top_k:
            break

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
