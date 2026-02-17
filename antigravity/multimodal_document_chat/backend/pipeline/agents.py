import os
import json
import uuid
import logging
from typing import List
from zipfile import ZipFile

from google.adk.agents import LlmAgent, ParallelAgent, Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types

from .schemas import DocumentPageResult
from .utils import split_pdf_logically
from .embeddings import generate_embeddings_for_entities

logger = logging.getLogger(__name__)

# --- Model definitions from user request & ADK rules ---
MODEL_EXTRACTOR = "gemini-2.5-pro" # For deep reasoning charts / tables
MODEL_NORMALIZER = "gemini-2.5-flash" # Fast cleanup

# We define a function to create an agent for a specific page chunk
def _create_page_extractor(page_chunk: dict, page_num: int) -> LlmAgent:
    """Creates a Gemini Extractor ADK Agent for a specific page."""
    
    # We use a custom callback to inject the PDF part.
    def inject_pdf(callback_context: CallbackContext, llm_request: LlmRequest, **kwargs):
        try:
             pdf_part = types.Part.from_bytes(
                 data=page_chunk["pdf_bytes"], 
                 mime_type="application/pdf"
             )
             # Prepend or append to contents
             llm_request.contents[-1].parts.append(pdf_part)
        except Exception as e:
             logger.error(f"Failed to inject PDF bytes for page {page_num}: {e}")

    return LlmAgent(
        name=f"extractor_page_{page_num}",
        model=MODEL_EXTRACTOR,
        instruction=f"""
        Analyze the specific PDF page provided.
        1. Identify any text blocks, charts, diagrams, or standalone tables.
        2. Create an entity for each.
        3. For text: Extract exactly.
        4. For charts/tables: Describe them precisely and extract tabular data structurally.
        5. Return the result strictly as a JSON object matching the requested schema.
        """,
        output_schema=DocumentPageResult,
        before_model_callback=inject_pdf
    )

async def run_parallel_extraction(pdf_path: str, runner_factory, session_service, app_name: str, session_id: str) -> List[DocumentPageResult]:
    """Splits PDF and runs ADK ParallelAgent over pages."""
    chunks = split_pdf_logically(pdf_path, max_pages_per_chunk=1)
    if not chunks:
        return []

    sub_agents = []
    for chunk in chunks:
        page_num = chunk["start_page"]
        agent = _create_page_extractor(chunk, page_num)
        sub_agents.append(agent)

    # Use ParallelAgent to execute all sub-extractors concurrently
    parallel_extractor = ParallelAgent(
        name="document_parallel_extractor",
        sub_agents=sub_agents
    )
    
    # Needs its own runner scope normally, but we pass factory/session hooks
    # For simplicity, we create a temporary runner for this isolated task
    from google.adk.runners import Runner
    temp_runner = Runner(agent=parallel_extractor, session_service=session_service, app_name=app_name)
    content = types.Content(role='user', parts=[types.Part(text="Extract entities from the provided pages.")])
    
    results = []
    try:
        async for event in temp_runner.run_async(user_id="system", session_id=session_id, new_message=content):
            # ParallelAgent aggregates the JSON strings internally 
            if event.is_final_response() and event.content and event.content.parts:
                resp_text = event.content.parts[0].text
                try:
                    # In ADK ParallelAgent, responses are usually a list of strings / dicts
                    parsed_results = json.loads(resp_text)
                    if isinstance(parsed_results, list):
                        for item in parsed_results:
                             # Some agents return standard strings, others return the exact dict
                             if isinstance(item, str):
                                 try:
                                     data = json.loads(item)
                                     results.append(DocumentPageResult(**data))
                                 except: pass
                             elif isinstance(item, dict):
                                 results.append(DocumentPageResult(**item))
                    elif isinstance(parsed_results, dict):
                         # If there was only 1 page
                         results.append(DocumentPageResult(**parsed_results))
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode parallel extraction result: {resp_text}")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        
    return results

async def process_document_pipeline(file_bytes: bytes, filename: str, session_service) -> List[dict]:
    """Main function called by FastAPI endpoint."""
    import tempfile
    
    app_name = "doc_pipeline"
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=app_name, user_id="system", session_id=session_id, state={})
    
    # Save bytes to temp file to reuse utility logic
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
         tmp.write(file_bytes)
         tmp_path = tmp.name
         
    try:
         # 1. Extraction (ADK)
         logger.info(f"Extracting entities from {filename}...")
         extracted_pages = await run_parallel_extraction(tmp_path, None, session_service, app_name, session_id)
         
         # Flatten entities
         all_entities = []
         for page_res in extracted_pages:
             for entity in page_res.entities:
                  all_entities.append(entity)

         if not all_entities:
             return []

         # 2. Embeddings (Vertex AI) - Python logic
         logger.info(f"Generating embeddings for {len(all_entities)} entities...")
         embedded_entities = generate_embeddings_for_entities(all_entities)
         
         # 3. Format for BigQuery / Output
         output_rows = []
         for i, entity in enumerate(embedded_entities):
              chunk_id = f"chunk_{filename}_{entity.page_number}_{i}"
              
              row = {
                  "chunk_id": chunk_id,
                  "document_name": filename,
                  "page_number": entity.page_number,
                  "entity_type": entity.entity_type,
                  "content": entity.content_description[:5000], # Keep reasonably sized for BQ string logs
                  "embedding": entity.embedding # The 3072 dimension vector
                  # Plus any schema details stringified
              }
              output_rows.append(row)
              
         return output_rows
    finally:
         if os.path.exists(tmp_path):
             os.remove(tmp_path)
