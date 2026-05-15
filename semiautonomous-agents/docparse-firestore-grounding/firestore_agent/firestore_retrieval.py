"""Firestore retrieval with VECTOR SEARCH and grounding metadata."""
import os
import json
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.adk.tools import FunctionTool


def retrieve_with_pdf_grounding(query: str) -> str:
    """
    Search the docparse PDF knowledge base using semantic vector search.

    CRITICAL: Call this tool for EVERY user question before answering.
    This tool retrieves data from extracted PDF reports with page-level citations.

    Args:
        query: The user's question or search query

    Returns:
        JSON string with retrieved chunks and grounding metadata
    """
    project = os.environ.get("FIRESTORE_PROJECT", "sharepoint-wif")
    collection_name = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")

    try:
        from google import genai
        from google.genai import types

        # STEP 1: Embed the query
        client = genai.Client(
            vertexai=True,
            project=project,
            location="global"
        )

        embed_response = client.models.embed_content(
            model="text-embedding-005",
            contents=query
        )
        query_embedding = embed_response.embeddings[0].values

        # STEP 2: Vector search in Firestore
        db = firestore.Client(project=project)
        collection = db.collection(collection_name)

        # Use find_nearest for vector search
        # query_embedding is already a list of floats from the embed API
        vector_query = collection.find_nearest(
            vector_field="embedding",
            query_vector=query_embedding,
            distance_measure=DistanceMeasure.COSINE,
            limit=10
        )

        results = vector_query.get()

        chunks = []
        grounding_chunks = []

        for doc in results:
            data = doc.to_dict()
            doc_id = doc.id
            original_text = data.get("text", "")

            # Parse doc_id: <docname>_p<page>
            parts = doc_id.rsplit("_p", 1)
            doc_name = parts[0].replace("_", " ")
            page_num = parts[1] if len(parts) > 1 else "unknown"

            chunks.append(original_text)
            grounding_chunks.append({
                "text": original_text[:500],
                "title": f"{doc_name} - Page {page_num}",
                "uri": f"gs://sharepoint-wif-docparse/{doc_id}.pdf#page={page_num}"
            })

        if not chunks:
            return json.dumps({
                "status": "no_results",
                "message": "No matching documents found in knowledge base",
                "chunks": [],
                "grounding": []
            })

        # Return top 5 chunks with grounding metadata
        return json.dumps({
            "status": "success",
            "chunks": chunks[:5],
            "grounding": grounding_chunks[:5],
            "total_found": len(chunks)
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"{type(e).__name__}: {str(e)[:300]}",
            "chunks": [],
            "grounding": []
        })


firestore_retrieval_tool = FunctionTool(retrieve_with_pdf_grounding)
