#!/usr/bin/env python3
"""
Custom Google ADK Agent with Intelligent Sub-Query Fan-Out & Multi-Store Retrieval
Implements query decomposition, parallel DataStore search, RRF deduplication,
exponential backoff retry, and Gemini 2.5 grounded synthesis.
"""

import os
import json
import time
import requests
import google.auth
import google.auth.transport.requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import ClientError

DEFAULT_PROJECT_NUMBER = "545964020693"
DEFAULT_CONNECTOR_ID = "sharepoint-data-def-connector"
MODEL_NAME = "gemini-2.5-flash"  # Allowed model per Google ADK rules
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

class SubQuerySpec(BaseModel):
    query: str = Field(description="Specific sub-query or entity keyword optimized for search")
    target_entities: List[str] = Field(
        default=["file"],
        description="List of entity stores to target: file, page, comment, event, attachment"
    )
    reasoning: str = Field(description="Why this sub-query or keyword is necessary")

class QueryDecomposition(BaseModel):
    sub_queries: List[SubQuerySpec] = Field(description="List of 2 to 5 targeted sub-queries/keywords")

class SearchResultDoc(BaseModel):
    id: str
    title: str
    entity_type: str
    url: str
    author: str
    snippet: str
    content: str
    score: float = 0.0

class ADKFanOutAgent:
    def __init__(self, project_number: str = DEFAULT_PROJECT_NUMBER, connector_id: str = DEFAULT_CONNECTOR_ID):
        self.project_number = project_number
        self.connector_id = connector_id
        self.creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.client = genai.Client(vertexai=True, project=project_number, location="us-central1")

    def _get_token(self) -> str:
        if not self.creds.valid:
            self.creds.refresh(google.auth.transport.requests.Request())
        return self.creds.token

    def _generate_with_retry(self, **kwargs) -> Any:
        """Executes model generation with exponential backoff on 429 quota exhaustion."""
        for attempt in range(5):
            try:
                return self.client.models.generate_content(**kwargs)
            except ClientError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    sleep_time = (2 ** attempt) * 3 + 2
                    time.sleep(sleep_time)
                else:
                    raise
        raise RuntimeError("Max retries exceeded for Gemini API call.")

    def _decompose_query(self, user_query: str) -> List[SubQuerySpec]:
        """Uses Gemini 2.5 to analyze the query and fan out into targeted sub-queries & key entity names."""
        system_instruction = (
            "You are a Search Query Decomposition Engine for enterprise SharePoint search.\n"
            "Analyze the user's question and decompose it into 2 to 5 discrete sub-queries.\n"
            "CRITICAL RULES:\n"
            "1. Extract exact proper nouns and acronyms (e.g. 'CFE', 'Smart Pipes', 'Apex Financial', 'NovaTech', 'Jennifer Walsh').\n"
            "2. For comparative questions, create separate sub-queries for each entity.\n"
            "3. Keep sub-queries concise (1-4 words) for best semantic matching."
        )
        prompt = f"Decompose this search query into targeted keyword and entity sub-queries:\n\"{user_query}\""
        try:
            response = self._generate_with_retry(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=QueryDecomposition,
                    temperature=0.0,
                )
            )
            parsed = json.loads(response.text)
            sub_queries = [SubQuerySpec(**sq) for sq in parsed.get("sub_queries", [])]
            sub_queries.append(SubQuerySpec(query=user_query, target_entities=["file", "page"], reasoning="Original query anchor"))
            return sub_queries
        except Exception:
            return [SubQuerySpec(query=user_query, target_entities=["file", "page"], reasoning="Fallback anchor")]

    def _search_single_datastore(self, datastore_id: str, query: str, page_size: int = 5) -> List[SearchResultDoc]:
        """Executes direct search against a Discovery Engine DataStore serving config."""
        token = self._get_token()
        url = (
            f"https://discoveryengine.googleapis.com/v1alpha/projects/{self.project_number}/"
            f"locations/global/collections/default_collection/dataStores/{datastore_id}/"
            f"servingConfigs/default_search:search"
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number,
        }
        payload = {"query": query, "pageSize": page_size}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if not resp.ok:
                return []
            results = resp.json().get("results", [])
            docs = []
            for r in results:
                d = r.get("document", {})
                s = d.get("structData", {})
                docs.append(SearchResultDoc(
                    id=d.get("id", ""),
                    title=s.get("title", "Untitled"),
                    entity_type=s.get("entity_type", "file"),
                    url=s.get("url", ""),
                    author=s.get("author", "Unknown"),
                    snippet=s.get("description", ""),
                    content=s.get("content", "") or s.get("description", ""),
                    score=r.get("rankSignals", {}).get("customSignals", [{}])[0].get("value", 1.0)
                ))
            return docs
        except Exception:
            return []

    def execute_fan_out_retrieval(self, sub_queries: List[SubQuerySpec]) -> List[SearchResultDoc]:
        """Executes parallel searches across sub-queries and entity stores with RRF merging."""
        all_docs: Dict[str, SearchResultDoc] = {}
        doc_ranks: Dict[str, float] = {}

        for sq in sub_queries:
            for entity in sq.target_entities:
                ds_id = f"{self.connector_id}_{entity}"
                results = self._search_single_datastore(ds_id, sq.query, page_size=4)
                for rank, doc in enumerate(results, 1):
                    doc_key = doc.id or doc.url
                    # Reciprocal Rank Fusion (RRF) with k=60
                    rrf_score = 1.0 / (60 + rank)
                    doc_ranks[doc_key] = doc_ranks.get(doc_key, 0.0) + rrf_score
                    if doc_key not in all_docs:
                        all_docs[doc_key] = doc

        # Sort docs by aggregate RRF score
        ranked_docs = sorted(all_docs.values(), key=lambda d: doc_ranks.get(d.id or d.url, 0.0), reverse=True)
        return ranked_docs[:8]

    def answer_query(self, user_query: str) -> Dict[str, Any]:
        """End-to-end pipeline: decompose -> fan-out search -> RRF merge -> Gemini synthesis."""
        start_time = time.time()
        
        # 1. Sub-query decomposition
        sub_queries = self._decompose_query(user_query)
        
        # 2. Parallel fan-out retrieval
        retrieved_docs = self.execute_fan_out_retrieval(sub_queries)
        
        # 3. Build context for synthesis
        context_blocks = []
        for idx, doc in enumerate(retrieved_docs, 1):
            context_blocks.append(
                f"--- SOURCE [{idx}]: {doc.title} ({doc.url}) ---\n"
                f"Author: {doc.author} | Entity: {doc.entity_type}\n"
                f"Content:\n{doc.content[:8000]}\n"
            )
        
        context_str = "\n".join(context_blocks) if context_blocks else "No relevant documents found."
        
        # 4. Grounded Synthesis with Gemini 2.5
        system_prompt = (
            "You are an expert Enterprise Knowledge Assistant. Answer the user's question accurately "
            "based strictly on the provided SharePoint context.\n"
            "- Cite sources using [Title](url) where available.\n"
            "- If the context contains specific numbers, dates, or tables, extract them precisely.\n"
            "- If the question asks for visual layout, color hex codes, or vector coordinates that are not present "
            "in the text/OCR, explicitly explain that raw visual diagram layouts are unextractable via text indexing.\n"
            "- Do not invent facts."
        )
        
        user_prompt = (
            f"User Question: {user_query}\n\n"
            f"Retrieved SharePoint Context:\n{context_str}\n\n"
            f"Provide a comprehensive, highly accurate answer with citations."
        )
        
        response = self._generate_with_retry(
            model=MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            )
        )
        
        elapsed_ms = round((time.time() - start_time) * 1000)
        
        return {
            "answer": response.text,
            "sub_queries": [sq.model_dump() for sq in sub_queries],
            "sources": [{"title": d.title, "url": d.url, "author": d.author} for d in retrieved_docs],
            "latency_ms": elapsed_ms,
            "docs_retrieved": len(retrieved_docs)
        }
