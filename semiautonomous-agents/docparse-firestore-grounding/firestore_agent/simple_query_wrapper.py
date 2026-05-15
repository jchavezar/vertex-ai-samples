"""Simple query() wrapper for Firestore agent with keyword retrieval."""
import os
import json
import re


PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "sharepoint-wif")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


class FirestoreQueryAgent:
    """
    Agent with query() and stream_query() methods for GE compatibility.
    1. Calls Firestore keyword retrieval
    2. Calls Gemini with context
    3. Returns answer
    """

    def _retrieve_and_answer(self, query: str) -> str:
        """Core retrieval and answering logic."""
        from google.cloud import firestore
        from google import genai

        # STEP 1: Keyword retrieval from Firestore
        try:
            firestore_project = os.environ.get("FIRESTORE_PROJECT", PROJECT_ID)
            collection_name = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")

            db = firestore.Client(project=firestore_project)
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
                    scored_docs.append((score, data.get("text", "")))

            scored_docs.sort(reverse=True, key=lambda x: x[0])
            chunks = [text for score, text in scored_docs[:5]]

            if not chunks:
                return "I don't have information about that in my knowledge base."

        except Exception as e:
            return f"Error retrieving from Firestore: {type(e).__name__}: {str(e)[:200]}"

        # STEP 2: Build sources list from scored docs
        sources = []
        for score, text in scored_docs[:5]:
            # Extract page info from text (starts with "# DocName — Page N")
            lines = text.split('\n')
            if lines and lines[0].startswith('#'):
                header = lines[0].replace('#', '').strip()
                sources.append(header)

        # STEP 3: Call Gemini with context
        context = "\n\n---\n\n".join(chunks)

        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

        sources_text = "\n".join([f"- {s}" for s in sources]) if sources else "No sources"

        prompt = f"""You are answering a question using retrieved PDF document chunks.

User question: {query}

Retrieved document chunks:
{context}

Sources (document pages where this information was found):
{sources_text}

Instructions:
- Answer EXHAUSTIVELY using all relevant data from the chunks
- Quote statistics and numbers VERBATIM
- If the chunks contain the answer, provide it in detail
- At the END of your answer, include a "Sources:" section listing which PDF pages you used
- Format source citations as clickable links: [Document Name - Page X](gs://sharepoint-wif-docparse-in/filename.pdf)
- Do NOT say you don't have access - the chunks above are your data source

Answer:"""

        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text

    def query(self, query: str) -> str:
        """Non-streaming query method."""
        return self._retrieve_and_answer(query)

    def stream_query(self, query: str):
        """Streaming query method."""
        answer = self._retrieve_and_answer(query)
        yield answer

    def streaming_agent_run_with_events(self, query: str):
        """GE-specific streaming method with grounding metadata."""
        from google.cloud import firestore
        import logging

        logger = logging.getLogger(__name__)

        # Get retrieval results for grounding
        firestore_project = os.environ.get("FIRESTORE_PROJECT", PROJECT_ID)
        collection_name = os.environ.get("FIRESTORE_COLLECTION", "docparse_chunks")

        try:
            db = firestore.Client(project=firestore_project)
            collection = db.collection(collection_name)
            docs = list(collection.stream())

            # Keyword matching (same as _retrieve_and_answer)
            stopwords = {'a', 'an', 'the', 'for', 'of', 'in', 'on', 'at', 'to', 'from', 'by', 'with', 'about',
                         'bring', 'me', 'all', 'what', 'are', 'is', 'was', 'be', 'been', 'do', 'does', 'did'}
            query_lower = query.lower()
            words = [re.sub(r'[^\w]', '', w) for w in query_lower.split()]
            keywords = [w for w in words if w not in stopwords and len(w) > 2]

            typo_map = {'milenial': 'millennial', 'millenial': 'millennial', 'gen': 'generation'}
            keywords = [typo_map.get(w, w) for w in keywords]

            if not keywords:
                keywords = [w for w in words if len(w) > 2]

            # Score and collect docs with metadata
            scored_docs = []
            for doc in docs:
                data = doc.to_dict()
                text = data.get("text", "").lower()
                score = sum(1 for word in keywords if word in text)
                if score > 0:
                    scored_docs.append((score, doc.id, data))

            scored_docs.sort(reverse=True, key=lambda x: x[0])

            # Build grounding references
            grounding_chunks = []
            for score, doc_id, data in scored_docs[:5]:
                parts = doc_id.rsplit("_p", 1)
                doc_name = parts[0].replace("_", " ")
                page_num = parts[1] if len(parts) > 1 else "001"

                grounding_chunks.append({
                    "web": {
                        "uri": data.get("pdf_uri", f"gs://sharepoint-wif-docparse/{doc_id}.pdf"),
                        "title": f"{doc_name} - Page {page_num}"
                    }
                })

            logger.info(f"Built {len(grounding_chunks)} grounding chunks for query: {query}")

        except Exception as e:
            logger.error(f"Error building grounding: {e}")
            grounding_chunks = []

        # Get answer
        answer = self._retrieve_and_answer(query)

        # Build response with grounding
        response = {
            "content": answer,
            "grounding_metadata": {
                "grounding_chunks": grounding_chunks,
                "grounding_supports": []
            }
        }

        logger.info(f"Yielding response with {len(grounding_chunks)} grounding chunks")

        # Yield event with both content and grounding metadata
        yield response


# Singleton
root_agent = FirestoreQueryAgent()
