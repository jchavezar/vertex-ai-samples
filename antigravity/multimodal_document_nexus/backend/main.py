import os
import uuid
import base64
from typing import Optional, List
import vertexai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
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

from pipeline.agents import process_document_pipeline
from pipeline.bigquery import get_indexed_documents_bq, delete_document_from_bq
from pipeline.feature_store import sync_feature_store_from_bq

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(""),
    session_id: str = Form(""),
    files: List[UploadFile] = File([]) # Optional files
):
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
        if not files and not message:
             raise HTTPException(status_code=400, detail="Message or file is required.")
             
        # Process files through the pipeline first if present
        pipeline_output = []
        annotated_images = []
        traces = []
        for file in files:
            if file.size > 0:
                file_bytes = await file.read()
                # Run complete extraction + embedding pipeline
                result_dict = await process_document_pipeline(file_bytes, file.filename, session_service)
                pipeline_output.extend(result_dict["output_rows"])
                annotated_images.extend(result_dict["annotated_images"])
                traces.extend(result_dict.get("traces", []))
                
        # Now run the conversational agent using this extracted context
        parts = []
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
                 context_str += f"Source [{frontend_id}]: (Doc: {file.filename}, Page: {row.get('page_number', 'unknown')}) {row.get('entity_type', 'TEXT')}: {row.get('content', '')}...\n"
                 
            parts.append(types.Part.from_text(text=context_str))
        elif message:
            # RAG Search if we didn't just upload a document
            from pipeline.bigquery import search_embeddings_in_bq
            search_results = await search_embeddings_in_bq(message)
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
                parts.append(types.Part.from_text(text=context_str))
                
                # Expose these chunks back to the frontend for citation tooltips
                pipeline_output.extend(search_results)

        if not parts:
            parts.append(types.Part.from_text(text="I have processed the document pipeline successfully."))
            
        content = types.Content(role="user", parts=parts)
        
        response_text = ""
        # Runner run_async yields events
        async for event in runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                     if part.text:
                         response_text += part.text

        # If we didn't get streaming text easily
        session = await session_service.get_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")
        if not response_text and session.history:
              last_msg = session.history[-1]
              if last_msg.role == "model":
                   response_text = "".join([p.text for p in last_msg.parts if p.text])

        # Return both the conversational response and the structured pipeline data for the UI
        return {
            "response": response_text, 
            "session_id": session_id,
            "pipeline_data": pipeline_output, # Send embeddings and chunks back
            "annotated_images": annotated_images,
            "traces": traces
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        import traceback
        traceback.print_exc()
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

@app.get("/api/documents/{document_name}/data")
async def get_document_data(document_name: str):
    from pipeline.bigquery import get_document_chunks_from_bq
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
