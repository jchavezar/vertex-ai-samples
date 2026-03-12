import os
import uuid
import base64
from typing import Optional, List
import vertexai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from google.cloud import storage
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# Force ADK/GenAI SDK to use specific location for Vertex API
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_LOCATION"] = os.environ.get("LOCATION", "us-central1")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("PROJECT_ID", "")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# Initialize Vertex AI for other parts of the system
vertexai.init(project=os.environ.get("PROJECT_ID"), location=os.environ.get("LOCATION", "us-central1"))


from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.genai import types

# Force Google ADK/GenAI SDK to use 'global' location if needed for preview models
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

# Initialize Vertex AI
# vertexai.init(location="global") # Assume ADC is set up

app = FastAPI(title="Multimodal Document Chat")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Session Service
session_service = InMemorySessionService()

# Define models
MODEL_NAME = "gemini-2.5-flash" # Faster model for responsive chat

# Create agent
agent = LlmAgent(
    name="doc_analyzer",
    model=MODEL_NAME,
    instruction="You are an expert at analyzing documents that contain text, charts, and images. Provide detailed, helpful answers based on the provided documents. Format your responses in Markdown.",
)

# Initialize Runner
runner = Runner(
    agent=agent,
    session_service=session_service,
    app_name="multimodal_doc_chat"
)

from pipeline import process_document_pipeline
from pipeline import get_indexed_documents_bq, delete_document_from_bq
from pipeline import sync_feature_store_from_bq

@app.post("/api/chat")
async def chat_endpoint(
    background_tasks: BackgroundTasks,
    message: str = Form(""),
    session_id: str = Form(""),
    selected_model: str = Form("gemini-2.5-flash"),
    files: List[UploadFile] = File([]), # Optional files
    gcs_uri: Optional[str] = Form(None) # Optional GCS URI
):
    print("----- CHAT ENDPOINT HIT -----", flush=True)
    if not session_id:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            user_id="default_user",
            session_id=session_id,
            app_name="multimodal_doc_chat"
        )
    else:
        session = await session_service.get_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")
        if not session:
            await session_service.create_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")

    try:
        print(f"DEBUG: files={len(files) if files else 0}, message={message}, gcs_uri={gcs_uri}", flush=True)
        if not files and not message and not gcs_uri:
             raise HTTPException(status_code=400, detail="Message, file, or GCS URI is required.")
             
        # Process files through the pipeline first if present
        pipeline_output = []
        annotated_images = []
        traces = []
        for file in files:
            if file.size > 0:
                file_bytes = await file.read()
                # Run complete extraction + embedding pipeline
                result_dict = await process_document_pipeline(file_bytes, file.filename, session_service)
                if result_dict:
                    pipeline_output.extend(result_dict.get("output_rows", []))
                    annotated_images.extend(result_dict.get("annotated_images", []))
                    traces.extend(result_dict.get("traces", []))
                    # Background the slow BigQuery document insertion
                    from pipeline import insert_embeddings_to_bq
                    background_tasks.add_task(insert_embeddings_to_bq, result_dict.get("output_rows", []))
                
        # Handle GCS URI if provided
        if gcs_uri:
            print(f"Processing GCS URI: {gcs_uri}")
            try:
                if not gcs_uri.startswith("gs://"):
                    raise HTTPException(status_code=400, detail="Invalid GCS URI. Must start with gs://")
                
                bucket_name = gcs_uri.split("/")[2]
                blob_name = "/".join(gcs_uri.split("/")[3:])
                
                storage_client = storage.Client()
                print("DEBUG: Getting bucket...", flush=True)
                bucket = storage_client.bucket(bucket_name)
                print("DEBUG: Getting blob...", flush=True)
                blob = bucket.blob(blob_name)
                
                print("DEBUG: Downloading blob as bytes...", flush=True)
                file_bytes = blob.download_as_bytes()
                print("DEBUG: Download complete! File size:", len(file_bytes), flush=True)
                filename = os.path.basename(blob_name) or "gcs_file.pdf"
                
                print("DEBUG: Starting process_document_pipeline...", flush=True)
                result_dict = await process_document_pipeline(file_bytes, filename, session_service)
                print("DEBUG: process_document_pipeline complete!", flush=True)
                if result_dict:
                    pipeline_output.extend(result_dict.get("output_rows", []))
                    annotated_images.extend(result_dict.get("annotated_images", []))
                    traces.extend(result_dict.get("traces", []))
                    # Background the slow BigQuery document insertion
                    import copy
                    bq_rows = copy.deepcopy(result_dict.get("output_rows", []))
                    for r in bq_rows:
                        if "frontend_id" in r:
                            r.pop("frontend_id")
                    
                    from pipeline import insert_embeddings_to_bq
                    background_tasks.add_task(insert_embeddings_to_bq, bq_rows)
            except Exception as e:
                print(f"Error downloading from GCS: {e}")
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=500, detail=f"Failed to process GCS file: {str(e)}")
                
        # Now run the conversational agent using this extracted context
        parts = []
        search_results = []
        instruction_text = ""
        context_str = ""
        
        if message:
            parts.append(types.Part.from_text(text=message))
            
        if pipeline_output:
            # Add strict instructions for grounding formatting
            instruction_text = """
You are an expert analyzing documents. ALWAYS ground your answers using the provided EXTRACTED PIPELINE DATA.
Crucially, you MUST cite your sources using EXACTLY this format for every claim: [1], [2], etc., corresponding to the Source ID.
DO NOT wrap the citation in backticks (`). DO NOT place periods, commas, or other punctuation immediately BEFORE or AFTER the citation bracket itself, incorporate the citation cleanly without extra symbols.
"""
            runner.agent.instruction = instruction_text
            
            # We add a summary of the extracted data as context to the assistant
            context_str = f"EXTRACTED PIPELINE DATA:\n"
            for idx, row in enumerate(pipeline_output[:20]): # Provide more context chunks
                 frontend_id = str(idx + 1)
                 row['frontend_id'] = frontend_id
                 doc_name = row.get('document_name', 'Document')
                 context_str += f"Source [{frontend_id}]: (Doc: {doc_name}, Page: {row.get('page_number', 'unknown')}) {row.get('entity_type', 'TEXT')}: {row.get('content', '')}...\n"
                 
            parts.append(types.Part.from_text(text=context_str))
        elif message:
            # RAG Search if we didn't just upload a document
            from pipeline import search_embeddings_in_bq
            search_results = await search_embeddings_in_bq(message)
            
            print("\n" + "="*50)
            print(f"VECTOR SEARCH RESULTS FOR QUERY: '{message}'")
            print("="*50)
            if search_results:
                for idx, res in enumerate(search_results):
                    print(f"Result {idx + 1}:")
                    print(f"  Doc: {res.get('document_name')}, Page: {res.get('page_number')}")
                    # Print full text being sent to LLM
                    print(f"  Content: {res.get('content')}")
                    print("-" * 50)
            else:
                print("No results found.")
            print("="*50 + "\n")

            if search_results:
                instruction_text = """
You are an expert analyzing documents. ALWAYS ground your answers using the provided RETRIEVED CONTEXT.
Crucially, you MUST cite your sources using EXACTLY this format for every claim: [1], [2], etc., corresponding to the Source ID.
DO NOT wrap the citation in backticks (`). DO NOT place periods, commas, or other punctuation immediately BEFORE or AFTER the citation bracket itself, incorporate the citation cleanly without extra symbols.
"""
                runner.agent.instruction = instruction_text
                
                context_str = f"RETRIEVED CONTEXT FROM BIGQUERY:\n"
                for idx, res in enumerate(search_results):
                     frontend_id = str(idx + 1)
                     res['frontend_id'] = frontend_id
                     context_str += f"Source [{frontend_id}]: (Doc: {res['document_name']}, Page: {res['page_number']}) Content: {res['content']}\n"
                     traces.append({
                         "step": "BigQuery Vector Search",
                         "description": f"Retrieved chunk from document: {res['document_name']}, Page {res['page_number']}",
                         "details": res['content']
                     })
                parts.append(types.Part.from_text(text=context_str))
                
                # Expose these chunks back to the frontend for citation tooltips
                pipeline_output = search_results

        if not parts:
            parts.append(types.Part.from_text(text="I have processed the document pipeline successfully."))

            
        content = types.Content(role="user", parts=parts)
        
        # Override the agent model with the user's selection
        runner.agent.model = selected_model
        
        async def run_main_agent():
            if not message:
                return "Document processed and inserted into the Vector Search index successfully. You can now search or chat with it."
                
            response_text = ""
            async for event in runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                         if part.text:
                             response_text += part.text
            return response_text

        async def run_evaluator_agent():
            if not message or not search_results:
                return "No evaluation performed because this was an initial document upload without a specific query, or no documents matched."
                
            eval_agent = LlmAgent(
                name="grounding_evaluator",
                model="gemini-2.5-flash",
                instruction="""You are an impartial asynchronous evaluator. Your job is to read the user's QUERY and the retrieved CONTEXT documents.
Evaluate if the documents contain relevant information to answer the query. Briefly summarize what relevant info was found and highlight which Document IDs are the most valuable.
If the documents are not relevant, state that clearly. Be concise. Format everything in Markdown."""
            )
            eval_runner = Runner(agent=eval_agent, session_service=session_service, app_name="eval_chat")
            eval_content = types.Content(role="user", parts=[
                types.Part.from_text(text=f"USER QUERY:\n{message}\n\n{context_str}")
            ])
            eval_text = ""
            eval_session_id = f"eval_{session_id}"
            eval_session_obj = await session_service.get_session(user_id="system", session_id=eval_session_id, app_name="eval_chat")
            if not eval_session_obj:
                 await session_service.create_session(user_id="system", session_id=eval_session_id, app_name="eval_chat")
            
            async for event in eval_runner.run_async(user_id="system", session_id=eval_session_id, new_message=eval_content):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            eval_text += part.text
            return eval_text

        import asyncio
        # Run both the conversational agent and the evaluator simultaneously
        main_resp, eval_resp = await asyncio.gather(run_main_agent(), run_evaluator_agent())

        # If we didn't get streaming text easily
        session = await session_service.get_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")
        if not main_resp and session.history:
              last_msg = session.history[-1]
              if last_msg.role == "model":
                   main_resp = "".join([p.text for p in last_msg.parts if p.text])

        # Return both the conversational response and the structured pipeline data for the UI
        return {
            "response": main_resp, 
            "session_id": session_id,
            "pipeline_data": pipeline_output, # Send embeddings and chunks back
            "annotated_images": annotated_images,
            "traces": traces,
            "evaluator_logs": eval_resp,
            "llm_prompt": f"SYSTEM INSTRUCTION:\n{instruction_text}\n\nCONTEXT:\n{context_str}" if (instruction_text or context_str) else "",
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        import traceback
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    docs = get_indexed_documents_bq()
    return {"documents": docs}

@app.delete("/api/documents/{document_name}")
async def delete_document(document_name: str, background_tasks: BackgroundTasks):
    success = delete_document_from_bq(document_name)
    if success:
        # Trigger feature store sync in background so the online view reflects the deletion
        background_tasks.add_task(sync_feature_store_from_bq)
        return {"status": "success", "message": f"Deleted {document_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.get("/api/documents/all/data")
async def get_all_documents_data():
    from pipeline import get_all_indexed_chunks_from_bq
    chunks = get_all_indexed_chunks_from_bq(limit=2000) # get a reasonable number of chunks for the global view
    
    if not chunks:
        return {
            "session_id": None,
            "pipeline_data": [],
            "annotated_images": [],
            "traces": [{"timestamp": "Now", "event": "No indexed documents found in BigQuery."}],
        }
    
    return {
        "session_id": None,
        "pipeline_data": chunks,
        "annotated_images": [], # No single set of images for global view
        "traces": [{"timestamp": "Now", "event": f"Loaded {len(chunks)} chunks across multiple documents from BigQuery."}],
    }

@app.get("/api/documents/{document_name}/data")
async def get_document_data(document_name: str):
    from pipeline import get_document_chunks_from_bq
    import json
    chunks = get_document_chunks_from_bq(document_name)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document data not found")
        
    # We create a new session ID for the user to chat with this document
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        user_id="default_user",
        session_id=session_id,
        app_name="multimodal_doc_chat"
    )
    
    # Load metadata (annotated images, traces, bounding boxes)
    metadata_path = os.path.join(os.path.dirname(__file__), "local_data", f"{document_name}.json")
    annotated_images = []
    traces = [{"timestamp": "Now", "event": f"Loaded {len(chunks)} cached chunks from BigQuery Index."}]
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                annotated_images = metadata.get("annotated_images", [])
                traces = metadata.get("traces", traces)
                boxes = metadata.get("boxes", {})
                # Inject bounding boxes back into chunks
                for chunk in chunks:
                    chunk_id = chunk.get("chunk_id")
                    if chunk_id in boxes:
                        chunk["box_2d"] = boxes[chunk_id]
        except Exception as e:
            print(f"Error loading metadata for {document_name}: {e}")
    
    return {
        "session_id": session_id,
        "pipeline_data": chunks,
        "annotated_images": annotated_images,
        "traces": traces,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
