"""
Hierarchical RAG Nexus - FastAPI Backend

Parent-Child RAG with Cloud SQL pgvector:
- Upload PDFs -> Extract sections -> Parent-child chunking -> Embed children
- Query -> Search children -> Return parent context + expand related agents

Uses Google ADK for agent orchestration with proper session management.
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Optional

import vertexai
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from init_db import init_database
from pipeline import (
    delete_document,
    embed_query,
    get_all_documents,
    get_all_relationships,
    get_all_agents_with_docs,
    get_document_data,
    run_full_pipeline,
    search_children_get_parents,
    search_simple_chunks,
)

load_dotenv(dotenv_path="../.env")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

# Initialize Vertex AI and ADK environment
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# GenAI client for warmup
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

APP_NAME = "hierarchical_rag_nexus"
MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """You are a helpful assistant that answers questions using retrieved context from a document database.

IMPORTANT RULES:
1. ALWAYS cite your sources using [1], [2], etc. corresponding to the source numbers
2. Use the PARENT CONTEXT which provides full context, not just the matched child chunk
3. If related agents are provided, incorporate that cross-component context
4. Be specific and detailed in your answers
5. If the context doesn't contain the answer, say so clearly
6. Keep conversation history in mind for follow-up questions
7. Provide direct answers without showing internal reasoning."""

# ADK Components - initialized once, reused across requests
session_service = InMemorySessionService()

rag_agent = LlmAgent(
    name="rag_assistant",
    model=MODEL,
    instruction=SYSTEM_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2048,
    ),
)

runner = Runner(
    agent=rag_agent,
    session_service=session_service,
    app_name=APP_NAME,
    auto_create_session=True,
)

app = FastAPI(
    title="Hierarchical RAG Nexus",
    description="Parent-Child RAG with Cloud SQL pgvector",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database and warm up ADK agent on startup."""
    try:
        await init_database()
        print("[Startup] Database initialized")
    except Exception as e:
        print(f"[Startup] Database init warning: {e}")

    # Warm up ADK agent with a simple request
    try:
        warmup_start = time.time()
        warmup_session_id = f"warmup_{uuid.uuid4()}"

        async for event in runner.run_async(
            user_id="system",
            session_id=warmup_session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello")],
            ),
        ):
            pass  # Just warm up, don't need the response

        warmup_time = time.time() - warmup_start
        print(f"[Startup] ADK agent warmed up in {warmup_time:.2f}s")
    except Exception as e:
        print(f"[Startup] Warmup warning: {e}")


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "vector_store": "pgvector", "pattern": "parent-child"}


@app.post("/api/session")
async def create_session():
    """
    Create a new session using ADK SessionService.
    Sessions are automatically created on first message, but this allows
    the frontend to get a session_id before sending any messages.
    """
    session_id = str(uuid.uuid4())
    user_id = "default_user"

    # Create session in ADK's session service
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    return {
        "session_id": session_id,
        "user_id": user_id,
        "status": "created",
        "message": "ADK session ready for chat"
    }


@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Check if a session exists and get its info."""
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id="default_user",
            session_id=session_id,
        )
        if session:
            return {
                "session_id": session_id,
                "exists": True,
                "event_count": len(session.events) if session.events else 0,
            }
    except Exception:
        pass
    return {"session_id": session_id, "exists": False}


@app.post("/api/chat")
async def chat(
    files: list[UploadFile] = File(default=[]),
    message: str = Form(default=""),
    session_id: str = Form(default=""),
):
    """
    Main chat endpoint:
    - If files provided: Process documents with parent-child pipeline
    - If message provided: Search children, return parent context, generate response
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    response_data = {
        "response": "",
        "session_id": session_id,
        "pipeline_data": None,
        "annotated_images": [],
        "traces": [],
        "retrieval_results": [],
    }

    # Handle file uploads
    if files and files[0].filename:
        for file in files:
            pdf_bytes = await file.read()
            pipeline_result = await run_full_pipeline(pdf_bytes, file.filename)

            response_data["pipeline_data"] = pipeline_result
            response_data["annotated_images"] = pipeline_result["annotated_images"]
            response_data["traces"] = pipeline_result["traces"]
            response_data["response"] = (
                f"Processed **{file.filename}**:\n\n"
                f"- **{len(pipeline_result['parents'])}** parent segments\n"
                f"- **{len(pipeline_result['children'])}** child chunks\n"
                f"- **{len(pipeline_result['relationships'])}** agent relationships\n\n"
                f"The document has been indexed with parent-child structure. "
                f"Ask questions to see how child retrieval returns parent context!"
            )

        return response_data

    # Handle chat queries
    if message:
        query_traces = []

        # Step 1: Embed query
        t0 = time.time()
        query_embedding = await embed_query(message)
        t1 = time.time()
        query_traces.append({
            "step": "1. Embed Query",
            "description": f"Convert query to 768-dim vector using text-embedding-004",
            "duration_ms": round((t1 - t0) * 1000),
            "details": f"Query: \"{message[:50]}{'...' if len(message) > 50 else ''}\"",
        })

        # Step 2: Run BOTH approaches in parallel for comparison
        t2 = time.time()
        hierarchical_task = search_children_get_parents(query_embedding, top_k=5, expand_related=True)
        simple_task = search_simple_chunks(query_embedding, top_k=5)

        retrieval_results, simple_results = await asyncio.gather(hierarchical_task, simple_task)
        t3 = time.time()

        if not retrieval_results:
            response_data["response"] = (
                "No relevant documents found. Please upload some PDFs first."
            )
            return response_data

        # Add retrieval trace details
        unique_parents = len(set(r.parent_id for r in retrieval_results))
        expanded_count = len(retrieval_results[0].expanded_context) if retrieval_results and retrieval_results[0].expanded_context else 0

        # Calculate context sizes for comparison
        hierarchical_context_chars = sum(len(r.parent_content) for r in retrieval_results)
        hierarchical_context_chars += sum(
            len(exp.get("content", "")) for r in retrieval_results for exp in (r.expanded_context or [])
        )
        simple_context_chars = sum(len(r.content) for r in simple_results) if simple_results else 0

        query_traces.append({
            "step": "2a. Hierarchical RAG",
            "description": f"Search children → get parents → expand related agents",
            "duration_ms": round((t3 - t2) * 1000),
            "details": f"{len(retrieval_results)} children → {unique_parents} parents + {expanded_count} expanded = ~{hierarchical_context_chars} chars",
        })

        query_traces.append({
            "step": "2b. Simple RAG (Comparison)",
            "description": f"Direct vector search on flat chunks (no hierarchy)",
            "duration_ms": 0,  # Same search, different table
            "details": f"{len(simple_results)} chunks = ~{simple_context_chars} chars (no parent context)",
        })

        # Step 3: Build context from parent segments
        context_parts = []
        for idx, result in enumerate(retrieval_results):
            source_num = idx + 1
            context_parts.append(
                f"**Source [{source_num}]** (Doc: {result.document_name}, "
                f"Page: {result.page_number}, Agent: {result.agent_name or 'N/A'})\n"
                f"Heading: {result.heading or 'None'}\n"
                f"**Parent Context:**\n{result.parent_content}\n\n"
                f"*Matched on child chunk:* {result.matched_child[:200]}..."
            )

            # Include expanded context from related agents
            if result.expanded_context:
                context_parts.append(
                    f"\n**Related Agents ({', '.join(result.related_agents)}):**"
                )
                for exp in result.expanded_context:
                    context_parts.append(
                        f"- {exp['agent_name']}: {exp['content'][:300]}..."
                    )

        context_str = "\n\n---\n\n".join(context_parts)

        # Step 4: Generate response with ADK Runner (maintains conversation history automatically)
        t4 = time.time()

        # Build prompt with retrieved context
        current_prompt = f"""RETRIEVED CONTEXT (Parent-Child Structure):
{context_str}

USER QUESTION: {message}

Answer the question comprehensively, citing sources [1], [2], etc."""

        # Run ADK agent - session history is managed automatically by ADK
        response_text = ""
        async for event in runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=current_prompt)],
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        if not response_text:
            response_text = "No response generated."

        t5 = time.time()

        # Get session info for trace
        try:
            session = await session_service.get_session(
                app_name=APP_NAME,
                user_id="default_user",
                session_id=session_id,
            )
            event_count = len(session.events) if session and session.events else 0
        except Exception:
            event_count = 0

        query_traces.append({
            "step": "4. ADK Agent",
            "description": f"Generate response using {MODEL} with ADK session management",
            "duration_ms": round((t5 - t4) * 1000),
            "details": f"Session: {session_id[:8]}..., Events: {event_count}",
        })

        # Summary trace
        total_ms = round((t5 - t0) * 1000)
        query_traces.append({
            "step": "Total",
            "description": f"End-to-end query processing",
            "duration_ms": total_ms,
            "details": f"Latency breakdown: Embed {query_traces[0]['duration_ms']}ms, Search {query_traces[1]['duration_ms']}ms, LLM {query_traces[-2]['duration_ms']}ms",
        })

        response_data["response"] = response_text
        response_data["query_traces"] = query_traces
        response_data["retrieval_results"] = [
            {
                "source_num": idx + 1,
                "parent_id": r.parent_id,
                "parent_content": r.parent_content,
                "matched_child": r.matched_child,
                "agent_name": r.agent_name,
                "heading": r.heading,
                "similarity": round(r.similarity_score, 4),
                "document_name": r.document_name,
                "page_number": r.page_number,
                "related_agents": r.related_agents,
            }
            for idx, r in enumerate(retrieval_results)
        ]
        # Simple RAG results for comparison
        response_data["simple_results"] = [
            {
                "source_num": idx + 1,
                "chunk_id": r.chunk_id,
                "content": r.content,
                "document_name": r.document_name,
                "page_number": r.page_number,
                "similarity": round(r.similarity_score, 4),
            }
            for idx, r in enumerate(simple_results)
        ] if simple_results else []

        return response_data

    response_data["response"] = "Please provide a message or upload a document."
    return response_data


@app.get("/api/documents")
async def list_documents():
    """List all indexed documents with parent/child counts."""
    docs = await get_all_documents()
    return {"documents": docs}


@app.get("/api/graph")
async def get_graph_data():
    """Get all agents and relationships for graph visualization."""
    agents = await get_all_agents_with_docs()
    relationships = await get_all_relationships()
    return {
        "agents": agents,
        "relationships": relationships,
    }


@app.get("/api/documents/{document_name}/data")
async def get_document(document_name: str):
    """Get all data for a specific document."""
    data = await get_document_data(document_name)
    return data


@app.delete("/api/documents/{document_name}")
async def remove_document(document_name: str):
    """Delete a document and all its segments/chunks."""
    count = await delete_document(document_name)
    return {"deleted": True, "document_name": document_name, "rows_affected": count}


@app.post("/api/evaluate")
async def evaluate_rag_approaches(query: str = Form(...)):
    """
    Deep evaluation comparing Hierarchical RAG vs Simple RAG.

    Returns detailed scores on 5 dimensions, grounding analysis with
    highlighted spans, and hallucination detection.
    """
    t_start = time.time()

    # Step 1: Get embeddings
    query_embedding = await embed_query(query)

    # Step 2: Run both retrievals in parallel
    hierarchical_task = search_children_get_parents(query_embedding, top_k=5, expand_related=True)
    simple_task = search_simple_chunks(query_embedding, top_k=5)
    hierarchical_results, simple_results = await asyncio.gather(hierarchical_task, simple_task)

    if not hierarchical_results or not simple_results:
        return {"error": "No documents found. Please upload PDFs first."}

    # Step 3: Build context for each approach
    hierarchical_context = ""
    hierarchical_context_list = []
    for idx, r in enumerate(hierarchical_results):
        hierarchical_context += f"[{idx+1}] {r.parent_content}\n"
        hierarchical_context_list.append({"id": idx+1, "content": r.parent_content})
        if r.expanded_context:
            for exp in r.expanded_context:
                hierarchical_context += f"  Related ({exp['agent_name']}): {exp['content'][:200]}...\n"

    simple_context = ""
    simple_context_list = []
    for idx, r in enumerate(simple_results):
        simple_context += f"[{idx+1}] {r.content}\n"
        simple_context_list.append({"id": idx+1, "content": r.content})

    # Step 4: Generate answers from both approaches
    async def generate_answer(context: str) -> tuple[str, float]:
        t0 = time.time()
        prompt = f"""Based on the following context, answer this question: {query}

CONTEXT:
{context}

Provide a comprehensive answer citing sources [1], [2], etc."""

        response = await genai_client.aio.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=512,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        return response.text or "", time.time() - t0

    hierarchical_answer, h_time = await generate_answer(hierarchical_context)
    simple_answer, s_time = await generate_answer(simple_context)

    # Step 5: Deep evaluation with grounding analysis
    async def deep_evaluate(answer: str, context: str, approach_name: str) -> dict:
        eval_prompt = f"""You are an expert RAG evaluation judge. Analyze this answer against its context.

QUESTION: {query}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{answer}

Evaluate on these 5 dimensions (score 0-5 each):

1. **Faithfulness**: Are ALL claims supported by context? (5=every claim supported, 0=multiple unsupported)
2. **Groundedness**: Do citations [1], [2] correctly point to sources? (5=all accurate, 0=wrong/missing)
3. **Completeness**: Did answer cover all relevant info from context? (5=comprehensive, 0=missed critical info)
4. **Answer Relevance**: Does answer directly address the query? (5=perfectly addresses, 0=off-topic)
5. **Context Precision**: What % of retrieved chunks were actually useful? (0.0-1.0)

Also perform GROUNDING ANALYSIS:
- For each sentence/claim in the answer, identify if it's GROUNDED (from context) or UNGROUNDED (potentially hallucinated)
- Calculate grounded_percentage and ungrounded_percentage

Return ONLY valid JSON:
{{
    "faithfulness": <0-5>,
    "groundedness": <0-5>,
    "completeness": <0-5>,
    "answer_relevance": <0-5>,
    "context_precision": <0.0-1.0>,
    "grounded_percentage": <0-100>,
    "ungrounded_percentage": <0-100>,
    "hallucination_count": <number>,
    "hallucination_examples": ["example claim 1", "example claim 2"],
    "grounded_spans": [
        {{"text": "exact text from answer", "is_grounded": true, "source_id": "1", "confidence": 0.95}},
        {{"text": "potentially hallucinated text", "is_grounded": false, "source_id": null, "confidence": 0.1}}
    ],
    "reasoning": "Brief explanation"
}}"""

        response = await genai_client.aio.models.generate_content(
            model=MODEL,
            contents=eval_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1500,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        eval_text = response.text or "{}"
        # Extract JSON
        if "```json" in eval_text:
            eval_text = eval_text.split("```json")[1].split("```")[0]
        elif "```" in eval_text:
            eval_text = eval_text.split("```")[1].split("```")[0]

        try:
            return json.loads(eval_text.strip())
        except json.JSONDecodeError:
            return {
                "faithfulness": 0, "groundedness": 0, "completeness": 0,
                "answer_relevance": 0, "context_precision": 0,
                "grounded_percentage": 0, "ungrounded_percentage": 100,
                "hallucination_count": 0, "hallucination_examples": [],
                "grounded_spans": [], "reasoning": f"Parse error: {eval_text[:100]}"
            }

    # Run deep evaluations in parallel
    h_eval, s_eval = await asyncio.gather(
        deep_evaluate(hierarchical_answer, hierarchical_context, "Hierarchical"),
        deep_evaluate(simple_answer, simple_context, "Simple")
    )

    # Calculate total scores (out of 30)
    def calc_total(ev):
        return (
            ev.get("faithfulness", 0) +
            ev.get("groundedness", 0) +
            ev.get("completeness", 0) +
            ev.get("answer_relevance", 0) +
            int(ev.get("context_precision", 0) * 10)  # Scale 0-1 to 0-10
        )

    h_total = calc_total(h_eval)
    s_total = calc_total(s_eval)

    # Determine winner
    if h_total > s_total:
        winner = "Hierarchical RAG"
        winner_reasoning = f"Hierarchical scored {h_total}/30 vs Simple's {s_total}/30. "
        winner_reasoning += f"Grounding: {h_eval.get('grounded_percentage', 0):.0f}% vs {s_eval.get('grounded_percentage', 0):.0f}%."
    elif s_total > h_total:
        winner = "Simple RAG"
        winner_reasoning = f"Simple scored {s_total}/30 vs Hierarchical's {h_total}/30."
    else:
        winner = "Tie"
        winner_reasoning = f"Both scored {h_total}/30."

    t_total = time.time() - t_start

    return {
        "query": query,
        "hierarchical": {
            "answer": hierarchical_answer,
            "context_chars": len(hierarchical_context),
            "sources": len(hierarchical_results),
            "latency_ms": round(h_time * 1000),
            "scores": {
                "faithfulness": h_eval.get("faithfulness", 0),
                "groundedness": h_eval.get("groundedness", 0),
                "completeness": h_eval.get("completeness", 0),
                "answer_relevance": h_eval.get("answer_relevance", 0),
                "context_precision": h_eval.get("context_precision", 0),
                "total": h_total,
            },
            "grounding": {
                "grounded_percentage": h_eval.get("grounded_percentage", 0),
                "ungrounded_percentage": h_eval.get("ungrounded_percentage", 0),
                "grounded_spans": h_eval.get("grounded_spans", []),
                "hallucination_count": h_eval.get("hallucination_count", 0),
                "hallucination_examples": h_eval.get("hallucination_examples", []),
            },
            "reasoning": h_eval.get("reasoning", ""),
        },
        "simple": {
            "answer": simple_answer,
            "context_chars": len(simple_context),
            "sources": len(simple_results),
            "latency_ms": round(s_time * 1000),
            "scores": {
                "faithfulness": s_eval.get("faithfulness", 0),
                "groundedness": s_eval.get("groundedness", 0),
                "completeness": s_eval.get("completeness", 0),
                "answer_relevance": s_eval.get("answer_relevance", 0),
                "context_precision": s_eval.get("context_precision", 0),
                "total": s_total,
            },
            "grounding": {
                "grounded_percentage": s_eval.get("grounded_percentage", 0),
                "ungrounded_percentage": s_eval.get("ungrounded_percentage", 0),
                "grounded_spans": s_eval.get("grounded_spans", []),
                "hallucination_count": s_eval.get("hallucination_count", 0),
                "hallucination_examples": s_eval.get("hallucination_examples", []),
            },
            "reasoning": s_eval.get("reasoning", ""),
        },
        "evaluation": {
            "a_score": h_total,
            "b_score": s_total,
            "winner": "A" if h_total > s_total else ("B" if s_total > h_total else "TIE"),
            "winner_label": winner,
            "reason": winner_reasoning,
        },
        "total_latency_ms": round(t_total * 1000),
    }


@app.post("/api/sql")
async def execute_sql(query: str = Form(...)):
    """Execute read-only SQL for exploration."""
    from pipeline import get_db_pool

    # Security: Only allow SELECT
    query_lower = query.strip().lower()
    blocked = ["drop", "delete", "insert", "update", "alter", "create", "truncate", "grant", "revoke"]
    if not query_lower.startswith("select") or any(b in query_lower for b in blocked):
        return {"error": "Only SELECT queries are allowed"}

    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)

            # Convert to list of dicts
            results = []
            for row in rows:
                row_dict = dict(row)
                # Truncate embeddings for display
                if "embedding" in row_dict and row_dict["embedding"]:
                    row_dict["embedding"] = f"[{len(row_dict['embedding'])} dims]"
                results.append(row_dict)

            return {
                "success": True,
                "columns": list(rows[0].keys()) if rows else [],
                "rows": results,
                "row_count": len(results),
            }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
