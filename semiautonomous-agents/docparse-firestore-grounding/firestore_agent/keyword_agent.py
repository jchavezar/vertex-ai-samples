"""ADK Agent with keyword-based Firestore retrieval (fallback from vector search)."""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool


def keyword_retrieve(query: str) -> str:
    """
    Retrieve from Firestore using keyword matching.

    Returns JSON with chunks and grounding metadata for citations.
    """
    import re
    import json
    from google.cloud import firestore

    project = os.environ.get("FIRESTORE_PROJECT", "sharepoint-wif")
    collection_name = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")

    try:
        db = firestore.Client(project=project)
        collection = db.collection(collection_name)
        docs = list(collection.stream())

        # Remove stopwords and punctuation
        stopwords = {'a', 'an', 'the', 'for', 'of', 'in', 'on', 'at', 'to', 'from', 'by', 'with', 'about',
                     'bring', 'me', 'all', 'what', 'are', 'is', 'was', 'be', 'been', 'do', 'does', 'did'}
        query_lower = query.lower()
        words = [re.sub(r'[^\w]', '', w) for w in query_lower.split()]
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        # Handle typos
        typo_map = {'milenial': 'millennial', 'millenial': 'millennial', 'gen': 'generation'}
        keywords = [typo_map.get(w, w) for w in keywords]

        if not keywords:
            keywords = [w for w in words if len(w) > 2]

        # Score docs by keyword matches
        scored_docs = []
        for doc in docs:
            data = doc.to_dict()
            text = data.get("text", "").lower()
            score = sum(1 for word in keywords if word in text)
            if score > 0:
                scored_docs.append((score, doc.id, data))

        scored_docs.sort(reverse=True, key=lambda x: x[0])

        # Build response with grounding metadata
        chunks = []
        grounding = []
        for score, doc_id, data in scored_docs[:5]:
            text = data.get("text", "")
            chunks.append(text)

            # Parse doc ID for grounding
            parts = doc_id.rsplit("_p", 1)
            doc_name = parts[0].replace("_", " ")
            page_num = parts[1] if len(parts) > 1 else "001"

            grounding.append({
                "title": f"{doc_name} - Page {page_num}",
                "uri": data.get("pdf_uri", f"gs://sharepoint-wif-docparse/{doc_id}.pdf"),
                "text": text[:200]
            })

        if not chunks:
            return json.dumps({
                "status": "no_results",
                "chunks": [],
                "grounding": []
            })

        return json.dumps({
            "status": "success",
            "chunks": chunks,
            "grounding": grounding
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"{type(e).__name__}: {str(e)[:300]}",
            "chunks": [],
            "grounding": []
        })


MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    model=MODEL,
    name="firestore_keyword_agent",
    description="Firestore-backed agent with keyword retrieval and grounding",
    instruction="""You answer questions about PDF reports extracted by docparse.

MANDATORY WORKFLOW:
1. ALWAYS call keyword_retrieve with the user's question
2. The tool returns JSON with "chunks" (text content) and "grounding" (source metadata)
3. Parse the JSON response
4. Use the chunks to answer EXHAUSTIVELY
5. Quote statistics and numbers VERBATIM
6. At the end of your answer, cite sources using the grounding data like: "Sources: [Document Name - Page X]"

If status is "no_results", say you don't have that information.

NEVER say you lack access - you have the keyword_retrieve tool.""",
    tools=[FunctionTool(keyword_retrieve)],
)
