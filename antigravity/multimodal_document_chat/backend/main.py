import os
import uuid
import base64
from typing import Optional, List
import vertexai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Session Service
session_service = InMemorySessionService()

# Define models
MODEL_NAME = "gemini-2.5-pro" # Excellent for multimodal tasks

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
        try:
            await session_service.get_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")
        except Exception:
             await session_service.create_session(user_id="default_user", session_id=session_id, app_name="multimodal_doc_chat")

    try:
        if not files and not message:
             raise HTTPException(status_code=400, detail="Message or file is required.")
             
        # Process files through the pipeline first if present
        pipeline_output = []
        for file in files:
            if file.size > 0:
                file_bytes = await file.read()
                # Run complete extraction + embedding pipeline
                extracted_rows = await process_document_pipeline(file_bytes, file.filename, session_service)
                pipeline_output.extend(extracted_rows)
                
        # Now run the conversational agent using this extracted context
        parts = []
        if message:
            parts.append(types.Part.from_text(text=message))
            
        if pipeline_output:
            # We add a summary of the extracted data as context to the assistant
            context_str = f"EXTRACTED PIPELINE DATA ({len(pipeline_output)} entities indexed with Embeddings):\n"
            for row in pipeline_output[:10]: # Limit context for the LLM to avoid token overflow
                 context_str += f"- [Page {row['page_number']}] {row['entity_type']}: {row['content'][:500]}...\n"
                 
            parts.append(types.Part.from_text(text=context_str))

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
            "pipeline_data": pipeline_output # Send embeddings and chunks back
        }
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
