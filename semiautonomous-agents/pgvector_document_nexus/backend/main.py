"""
FastAPI server for PGVector Document Nexus.
Provides endpoints for document upload, chat, and management.
"""

import os
import uuid
import json
from typing import Optional, List
from contextlib import asynccontextmanager

import vertexai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path="../.env")

os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("PROJECT_ID", "")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

vertexai.init(project=os.environ.get("PROJECT_ID"), location=os.environ.get("LOCATION", "us-central1"))

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.genai import types

from google import genai as genai_client

from pipeline import (
    process_document_pipeline,
    search_embeddings_pgvector,
    get_indexed_documents,
    get_document_chunks,
    delete_document,
    insert_chunks_to_pgvector,
    init_db_schema,
    get_genai_client,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema on startup
    await init_db_schema()

    # Warm up the singleton genai client to avoid cold start on first request
    print("Warming up genai client...")
    from google.genai.types import EmbedContentConfig

    # Get the singleton client (same one used by all requests)
    client = get_genai_client()

    # Warm up embedding model
    try:
        await client.aio.models.embed_content(
            model="text-embedding-004",
            contents="warmup",
            config=EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=768)
        )
        print("  - Embedding model warmed up")
    except Exception as e:
        print(f"  - Embedding warmup failed: {e}")

    # Warm up LLM model
    try:
        await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="hi"
        )
        print("  - LLM model warmed up")
    except Exception as e:
        print(f"  - LLM warmup failed: {e}")

    print("Server ready!")
    yield

app = FastAPI(title="PGVector Document Nexus", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

MODEL_NAME = "gemini-2.5-flash"

agent = LlmAgent(
    name="doc_analyzer",
    model=MODEL_NAME,
    instruction="You are an expert at analyzing documents. Provide detailed answers grounded in the provided context. Format responses in Markdown.",
)

runner = Runner(
    agent=agent,
    session_service=session_service,
    app_name="pgvector_doc_chat"
)

@app.post("/api/chat")
async def chat_endpoint(
    background_tasks: BackgroundTasks,
    message: str = Form(""),
    session_id: str = Form(""),
    selected_model: str = Form("gemini-2.5-flash"),
    files: List[UploadFile] = File([]),
):
    if not session_id:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            user_id="default_user",
            session_id=session_id,
            app_name="pgvector_doc_chat"
        )
    else:
        session = await session_service.get_session(
            user_id="default_user",
            session_id=session_id,
            app_name="pgvector_doc_chat"
        )
        if not session:
            await session_service.create_session(
                user_id="default_user",
                session_id=session_id,
                app_name="pgvector_doc_chat"
            )

    try:
        if not files and not message:
            raise HTTPException(status_code=400, detail="Message or file required")

        pipeline_output = []
        annotated_images = []
        traces = []

        # Process uploaded files
        for file in files:
            if file.size > 0:
                file_bytes = await file.read()
                result = await process_document_pipeline(file_bytes, file.filename, session_service)
                if result:
                    pipeline_output.extend(result.get("output_rows", []))
                    annotated_images.extend(result.get("annotated_images", []))
                    traces.extend(result.get("traces", []))
                    # Background insert to pgvector
                    background_tasks.add_task(insert_chunks_to_pgvector, result.get("output_rows", []))

        parts = []
        search_results = []
        instruction_text = ""
        context_str = ""

        if message:
            parts.append(types.Part.from_text(text=message))

        if pipeline_output:
            # Fresh upload - use extracted data as context
            instruction_text = """
You are an expert analyzing documents. Ground your answers using the EXTRACTED DATA below.
MUST cite sources using [1], [2], etc. Do NOT use backticks around citations.
"""
            runner.agent.instruction = instruction_text

            context_str = "EXTRACTED DATA:\n"
            for idx, row in enumerate(pipeline_output[:20]):
                frontend_id = str(idx + 1)
                row['frontend_id'] = frontend_id
                context_str += f"Source [{frontend_id}]: (Doc: {row.get('document_name')}, Page: {row.get('page_number')}) {row.get('entity_type')}: {row.get('content')}...\n"

            parts.append(types.Part.from_text(text=context_str))

        elif message:
            # RAG search from pgvector
            search_results = await search_embeddings_pgvector(message, top_k=5)

            if search_results:
                instruction_text = """
You are an expert analyzing documents. Ground your answers using the RETRIEVED CONTEXT below.
MUST cite sources using [1], [2], etc. Do NOT use backticks around citations.
"""
                runner.agent.instruction = instruction_text

                context_str = "RETRIEVED CONTEXT FROM PGVECTOR:\n"
                for idx, res in enumerate(search_results):
                    frontend_id = str(idx + 1)
                    res['frontend_id'] = frontend_id
                    context_str += f"Source [{frontend_id}]: (Doc: {res['document_name']}, Page: {res['page_number']}) Content: {res['content']}\n"
                    traces.append({
                        "step": "pgvector Search",
                        "description": f"Retrieved from {res['document_name']}, Page {res['page_number']}",
                        "similarity": res.get('similarity', 0),
                    })

                parts.append(types.Part.from_text(text=context_str))
                pipeline_output = search_results

        if not parts:
            parts.append(types.Part.from_text(text="Document processed successfully."))

        # Use direct genai call for faster response (bypasses ADK overhead)
        async def run_main_agent():
            if not message:
                return "Document processed and indexed in pgvector. You can now search or chat."

            client = get_genai_client()

            # Build the prompt
            system_instruction = instruction_text if instruction_text else "You are a helpful assistant that analyzes documents. Be concise."
            user_prompt = message
            if context_str:
                user_prompt = f"{context_str}\n\nUSER QUESTION: {message}"

            response = await client.aio.models.generate_content(
                model=selected_model,
                contents=user_prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                }
            )

            return response.text if response.text else "No response generated."

        # Run main agent only (removed evaluator to reduce latency)
        main_resp = await run_main_agent()
        eval_resp = ""

        return {
            "response": main_resp,
            "session_id": session_id,
            "pipeline_data": pipeline_output,
            "annotated_images": annotated_images,
            "traces": traces,
            "evaluator_logs": eval_resp,
            "llm_prompt": f"INSTRUCTION:\n{instruction_text}\n\nCONTEXT:\n{context_str}" if instruction_text else "",
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    docs = await get_indexed_documents()
    return {"documents": docs}

@app.get("/api/documents/{document_name}/data")
async def get_document_data(document_name: str):
    chunks = await get_document_chunks(document_name)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found")

    session_id = str(uuid.uuid4())
    await session_service.create_session(
        user_id="default_user",
        session_id=session_id,
        app_name="pgvector_doc_chat"
    )

    # Load local metadata
    metadata_path = os.path.join(os.path.dirname(__file__), "local_data", f"{document_name}.json")
    annotated_images = []
    traces = [{"timestamp": "Now", "event": f"Loaded {len(chunks)} chunks from pgvector"}]

    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            annotated_images = metadata.get("annotated_images", [])
            traces = metadata.get("traces", traces)
            boxes = metadata.get("boxes", {})
            for chunk in chunks:
                if chunk["chunk_id"] in boxes:
                    chunk["box_2d"] = boxes[chunk["chunk_id"]]

    return {
        "session_id": session_id,
        "pipeline_data": chunks,
        "annotated_images": annotated_images,
        "traces": traces,
    }

@app.delete("/api/documents/{document_name}")
async def delete_document_endpoint(document_name: str):
    success = await delete_document(document_name)
    if success:
        return {"status": "success", "message": f"Deleted {document_name}"}
    raise HTTPException(status_code=500, detail="Delete failed")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "vector_store": "pgvector"}

@app.post("/api/sql")
async def execute_sql(query: str = Form(...)):
    """Execute a read-only SQL query against the pgvector database."""
    from pipeline import get_db_pool

    # Security: Only allow SELECT queries
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed for security reasons"
        )

    # Block dangerous keywords even in SELECT
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE", "GRANT", "REVOKE"]
    for keyword in dangerous:
        if keyword in query_upper:
            raise HTTPException(
                status_code=400,
                detail=f"Query contains forbidden keyword: {keyword}"
            )

    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Set statement timeout to prevent long-running queries
            await conn.execute("SET statement_timeout = '10s'")

            rows = await conn.fetch(query)

            # Convert to list of dicts
            results = []
            columns = []
            for row in rows:
                if not columns:
                    columns = list(row.keys())
                # Handle special types
                row_dict = {}
                for key, value in row.items():
                    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                        # Convert arrays/vectors to lists, truncate long vectors
                        try:
                            val_list = list(value)
                            if len(val_list) > 10:
                                row_dict[key] = f"[{val_list[0]:.4f}, {val_list[1]:.4f}, ... ({len(val_list)} dims)]"
                            else:
                                row_dict[key] = val_list
                        except:
                            row_dict[key] = str(value)
                    else:
                        row_dict[key] = value
                results.append(row_dict)

            return {
                "success": True,
                "columns": columns,
                "rows": results,
                "row_count": len(results)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "columns": [],
            "rows": [],
            "row_count": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
