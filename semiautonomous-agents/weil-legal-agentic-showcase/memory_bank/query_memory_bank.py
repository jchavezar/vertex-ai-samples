"""
Weil, Gotshal & Manges LLP — Centralized Firestore RAG MemoryBank Retrieval & ADK Tool
======================================================================================
Queries the centralized Google Cloud Firestore MemoryBank (`vtxdemos.weil_memory_bank`)
using Hybrid Dense Vector Search (`text-embedding-005`) + Lexical Keyword Boosting, and
optionally synthesizes grounded executive answers via `gemini-3.8-flash`.

Usage:
  # Check MemoryBank statistics & session registry:
  python3 memory_bank/query_memory_bank.py --stats

  # Semantic + keyword search with grounded Gemini 3.8 Flash synthesis:
  python3 memory_bank/query_memory_bank.py --query "What are Andrew Simon's priorities for Privacy Pro and Gemma?" --synthesize

  # Import as a native Google ADK Function Tool:
  from memory_bank.query_memory_bank import search_weil_memory_bank
"""

import os
import math
import argparse
from typing import List, Dict, Any, Optional

from google.cloud import firestore
from google import genai
from google.genai import types

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

PROJECT_ID = "vtxdemos"
MEMORY_COLLECTION = "weil_memory_bank"
SESSIONS_COLLECTION = "weil_sessions_registry"
EMBEDDING_MODEL = "text-embedding-005"
SYNTHESIS_MODEL = "gemini-3.8-flash"


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_from_firestore(
    query: str,
    top_k: int = 5,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Executes Hybrid RAG Retrieval (768-dim Cosine Similarity + Lexical Term Match Boost)
    against the live Google Cloud Firestore collection `weil_memory_bank`.
    """
    db = firestore.Client(project=PROJECT_ID)
    embed_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

    emb_resp = embed_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[query],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    query_vec = list(emb_resp.embeddings[0].values)
    query_terms = [t.lower() for t in query.split() if len(t) > 2]

    collection_ref = db.collection(MEMORY_COLLECTION)
    if category_filter:
        docs_stream = collection_ref.where("category", "==", category_filter).stream()
    else:
        docs_stream = collection_ref.stream()

    scored_results: List[Dict[str, Any]] = []
    for snap in docs_stream:
        data = snap.to_dict()
        doc_vec = data.get("embedding", [])
        vec_score = cosine_similarity(query_vec, doc_vec) if doc_vec else 0.0

        haystack = f"{data.get('title', '')} {data.get('content', '')}".lower()
        term_hits = sum(1 for t in query_terms if t in haystack)
        lexical_boost = min(0.15, 0.03 * term_hits)

        hybrid_score = vec_score + lexical_boost
        scored_results.append({
            "doc_id": data.get("doc_id", snap.id),
            "title": data.get("title", ""),
            "category": data.get("category", ""),
            "source_type": data.get("source_type", ""),
            "conversation_id": data.get("conversation_id", ""),
            "file_path": data.get("file_path", ""),
            "hybrid_score": round(hybrid_score, 4),
            "vector_score": round(vec_score, 4),
            "content": data.get("content", ""),
        })

    scored_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return scored_results[:top_k]


def search_weil_memory_bank(query: str, top_k: int = 5) -> str:
    """
    Google ADK Function Tool: Searches the centralized Google Cloud Firestore MemoryBank
    (`vtxdemos.weil_memory_bank`) for all historical conversations, stakeholder details,
    architecture decisions, code implementations, and demo runbooks for Weil, Gotshal & Manges LLP.

    Args:
        query: The natural language question or topic to retrieve from the Weil MemoryBank.
        top_k: Maximum number of top matching documents to return (default 5).

    Returns:
        Formatted string containing the top retrieved documents with citations and metadata.
    """
    results = retrieve_from_firestore(query=query, top_k=top_k)
    if not results:
        return "No matching documents found in the Weil Firestore MemoryBank."

    formatted = []
    for idx, r in enumerate(results, 1):
        meta = f"Category: {r['category']} | Source: {r['source_type']}"
        if r.get("conversation_id"):
            meta += f" | Conversation: {r['conversation_id']}"
        if r.get("file_path"):
            meta += f" | File: {r['file_path']}"
        formatted.append(
            f"[{idx}] DOC_ID: {r['doc_id']} (Score: {r['hybrid_score']})\n"
            f"    Title: {r['title']}\n"
            f"    {meta}\n"
            f"    Content:\n{r['content']}\n"
        )
    return "\n" + ("-" * 80 + "\n").join(formatted)


def synthesize_answer_with_gemini(query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """Synthesizes a comprehensive, citation-backed answer using `gemini-3.8-flash`."""
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    context_blocks = "\n\n".join(
        f"=== [{d['doc_id']}] {d['title']} (Category: {d['category']}) ===\n{d['content']}"
        for d in retrieved_docs
    )
    prompt = (
        f"You are the Weil, Gotshal & Manges LLP Institutional MemoryBank Engine.\n"
        f"Answer the user's question with exhaustive precision ('details over the details') "
        f"using ONLY the retrieved Firestore MemoryBank documents below. Always cite document IDs "
        f"like `[doc_id]` in your answer.\n\n"
        f"RETRIEVED FIRESTORE MEMORYBANK CONTEXT:\n{context_blocks}\n\n"
        f"USER QUESTION:\n{query}\n"
    )
    response = client.models.generate_content(
        model=SYNTHESIS_MODEL,
        contents=prompt,
    )
    return response.text or ""


def print_memory_bank_stats() -> None:
    db = firestore.Client(project=PROJECT_ID)
    mem_docs = list(db.collection(MEMORY_COLLECTION).stream())
    sess_docs = list(db.collection(SESSIONS_COLLECTION).stream())

    by_cat: Dict[str, int] = {}
    for d in mem_docs:
        cat = d.to_dict().get("category", "uncategorized")
        by_cat[cat] = by_cat.get(cat, 0) + 1

    print("=" * 88)
    print(f"🏛️  WEIL FIRESTORE MEMORYBANK STATUS (GCP Project: `{PROJECT_ID}`)")
    print("=" * 88)
    print(f"• Firestore Collection `{MEMORY_COLLECTION}`   : {len(mem_docs)} embedded RAG documents")
    print(f"• Firestore Collection `{SESSIONS_COLLECTION}` : {len(sess_docs)} indexed Jetski conversations")
    print("\n📊 Documents by Category:")
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"   - {cat:<38} : {count} docs")
    print("\n🗂️  Indexed Jetski Conversations:")
    for s in sess_docs:
        sd = s.to_dict()
        print(
            f"   - {sd.get('conversation_id')} | Turns: {sd.get('total_user_turns', 0):<3} | "
            f"Steps: {sd.get('total_steps', 0):<4} | Last Active: {sd.get('last_timestamp', '')}"
        )
    print("=" * 88)


def main():
    parser = argparse.ArgumentParser(description="Weil, Gotshal & Manges LLP Firestore RAG MemoryBank CLI")
    parser.add_argument("--query", "-q", type=str, help="Natural language query for the Weil MemoryBank")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of top documents to retrieve")
    parser.add_argument("--category", "-c", type=str, default=None, help="Optional category filter")
    parser.add_argument("--synthesize", "-s", action="store_true", help="Synthesize answer with gemini-3.8-flash")
    parser.add_argument("--stats", action="store_true", help="Display Firestore MemoryBank collection statistics")
    args = parser.parse_args()

    if args.stats or not args.query:
        print_memory_bank_stats()
        if not args.query:
            return

    print(f"\n🔎 Querying Firestore MemoryBank for: \"{args.query}\" (top_k={args.top_k})...\n")
    top_docs = retrieve_from_firestore(query=args.query, top_k=args.top_k, category_filter=args.category)

    for idx, doc in enumerate(top_docs, 1):
        print(f"[{idx}] {doc['doc_id']} | Score: {doc['hybrid_score']} (Vec: {doc['vector_score']}) | {doc['category']}")
        print(f"    Title: {doc['title']}")

    if args.synthesize:
        print(f"\n🤖 Synthesizing Grounded Answer via `{SYNTHESIS_MODEL}`...\n")
        print("-" * 88)
        answer = synthesize_answer_with_gemini(args.query, top_docs)
        print(answer)
        print("-" * 88)


if __name__ == "__main__":
    main()
