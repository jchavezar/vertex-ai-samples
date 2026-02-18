import os
import json
import uuid
import logging
from typing import List, Tuple, Optional
from zipfile import ZipFile

from google.adk.agents import LlmAgent, ParallelAgent, Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types

from .schemas import DocumentPageResult, ADKTrace
from .utils import split_pdf_logically
from .embeddings import generate_embeddings_for_entities

logger = logging.getLogger(__name__)

# --- Model definitions from user request & ADK rules ---
MODEL_EXTRACTOR = "gemini-2.5-flash" # Changed to flash for high throughput
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
        5. For every entity, provide `box_2d`: a 2D integer array [ymin, xmin, ymax, xmax] representing the normalized bounding box coordinates (0-1000).
        6. Return the result strictly as a JSON object matching the requested schema.
        """,
        output_schema=DocumentPageResult,
        before_model_callback=inject_pdf
    )

import asyncio
from google.adk.runners import Runner

async def _process_single_page(page_agent, session_service, app_name: str, session_id: str, semaphore: asyncio.Semaphore) -> Tuple[List[DocumentPageResult], Optional[ADKTrace]]:
    """Runs a single ADK page extractor within a semaphore boundary."""
    from datetime import datetime, timezone
    import time
    
    start_t = time.time()
    start_dt = datetime.now(timezone.utc).isoformat()
    
    async with semaphore:
        # Create the sub-session for this specific page execution to satisfy ADK runner
        await session_service.create_session(user_id="system", session_id=session_id, app_name=app_name, state={})
        
        # We need to use the agent's specific runner
        temp_runner = Runner(agent=page_agent, session_service=session_service, app_name=app_name)
        content = types.Content(role="user", parts=[types.Part.from_text(text="Extract entities from this page.")])
        
        try:
            async for event in temp_runner.run_async(user_id="system", session_id=session_id, new_message=content):
                if event.is_final_response() and event.content and event.content.parts:
                    resp_text = event.content.parts[0].text
                    try:
                        import json
                        parsed = json.loads(resp_text)
                        
                        page_num = 1
                        entities_data = []
                        if isinstance(parsed, dict):
                            page_num = parsed.get("page_number", 1)
                            if "entities" in parsed:
                                entities_data = parsed["entities"]
                            else:
                                entities_data = [parsed] # Failsafe
                        elif isinstance(parsed, list):
                            entities_data = parsed
                            
                        processed_entities = []
                        for item in entities_data:
                            if not item.get("structured_data"):
                                item["structured_data"] = None
                            if not item.get("embedding"):
                                item["embedding"] = None
                            processed_entities.append(item)
                            
                        end_t = time.time()
                        end_dt = datetime.now(timezone.utc).isoformat()
                        trace = ADKTrace(
                            agent_name=page_agent.name,
                            page_number=page_num,
                            start_time=start_dt,
                            end_time=end_dt,
                            duration_seconds=round(end_t - start_t, 2),
                            entities_extracted=len(processed_entities)
                        )
                        return [DocumentPageResult(page_number=page_num, entities=processed_entities)], trace

                    except Exception as e:
                        print(f"Failed fallback JSON decode in event loop: {e}")

        except Exception as e:
            print(f"Single page extraction failed for {page_agent.name}: {e}")
            import traceback
            traceback.print_exc()

        try:
            # ADK stores Pydantic objects directly in the session state
            session = await session_service.get_session(user_id="system", session_id=session_id, app_name=app_name)
            if session and hasattr(session, 'state'):
                output_key = getattr(page_agent, 'output_key', 'output')
                result = session.state.get(output_key)
                
                if result:
                    if hasattr(result, "entities"):
                        end_t = time.time()
                        trace = ADKTrace(
                            agent_name=page_agent.name,
                            page_number=int(page_agent.name.split("_page_")[1]) if "_page_" in page_agent.name else 0,
                            start_time=start_dt,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            duration_seconds=round(end_t - start_t, 2),
                            entities_extracted=len(result.entities)
                        )
                        return [result], trace
                    elif isinstance(result, list):
                        end_t = time.time()
                        trace = ADKTrace(
                            agent_name=page_agent.name,
                            page_number=int(page_agent.name.split("_page_")[1]) if "_page_" in page_agent.name else 0,
                            start_time=start_dt,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            duration_seconds=round(end_t - start_t, 2),
                            entities_extracted=len(result)
                        )
                        return result, trace
                    elif isinstance(result, DocumentPageResult):
                        end_t = time.time()
                        trace = ADKTrace(
                            agent_name=page_agent.name,
                            page_number=result.page_number,
                            start_time=start_dt,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            duration_seconds=round(end_t - start_t, 2),
                            entities_extracted=len(result.entities)
                        )
                        return [result], trace

        except Exception as e:
             print(f"Error reading ADK session state: {e}")

        return [], None   

async def run_parallel_extraction(pdf_bytes: bytes, runner_factory, session_service, app_name: str, session_id: str) -> Tuple[List[DocumentPageResult], List[ADKTrace]]:
    """Splits PDF and runs ADK Extractors concurrently using asyncio.gather."""
    from .schemas import ADKTrace
    chunks = split_pdf_logically(pdf_bytes, max_pages_per_chunk=1)
    if not chunks:
        return [], []

    # Limit to 100 concurrent requests as per Gemini 2.5 Flash optimizations
    semaphore = asyncio.Semaphore(100)
    tasks = []
    
    for chunk in chunks:
        page_num = chunk["start_page"]
        agent = _create_page_extractor(chunk, page_num)
        # Create a unique session ID for each parallel task so they don't clobber history
        sub_session_id = f"{session_id}_page_{page_num}"
        tasks.append(_process_single_page(agent, session_service, app_name, sub_session_id, semaphore))

    all_page_results = await asyncio.gather(*tasks)
    
    # Flatten the results
    final_results = []
    traces = []
    for res_tuple in all_page_results:
        page_res_list, trace = res_tuple
        logger.info(f"Page returned {len(page_res_list)} results.")
        final_results.extend(page_res_list)
        if trace:
            traces.append(trace)
        
    logger.info(f"Total entities extracted across all pages before flattening: {len(final_results)}")
    return final_results, traces

async def process_document_pipeline(file_bytes: bytes, filename: str, session_service) -> dict:
    """Main function called by FastAPI endpoint."""
    app_name = "doc_pipeline"
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=app_name, user_id="system", session_id=session_id, state={})
         
    # 1. Extraction (ADK) concurrent across all pages
    logger.info(f"Extracting entities from {filename} in parallel...")
    extracted_pages, traces = await run_parallel_extraction(file_bytes, None, session_service, app_name, session_id)
    
    # Flatten entities
    all_entities = []
    for page_res in extracted_pages:
        for entity in page_res.entities:
             all_entities.append(entity)

    logger.info(f"Total pure entities after extraction: {len(all_entities)}")
    if not all_entities:
        logger.warning("Pipeline terminating early: 0 entities were yielded by extraction.")
        return []

    # 2. Embeddings (Vertex AI) - Python logic
    logger.info(f"Generating embeddings for {len(all_entities)} entities...")
    embedded_entities = await generate_embeddings_for_entities(all_entities)
    
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
         }
         output_rows.append(row)
         
    # 4. Draw annotated images for the frontend
    from .utils import pdf_page_to_image, draw_bounding_boxes
    import base64
    
    annotated_images = []
    # Group entities by page
    pages_to_draw = {}
    for entity in embedded_entities:
        if entity.page_number not in pages_to_draw:
            pages_to_draw[entity.page_number] = []
        pages_to_draw[entity.page_number].append(entity)
        
    for page_num_1_indexed, entities in pages_to_draw.items():
        try:
            # 0-indexed for fitz
            raw_img_bytes = pdf_page_to_image(file_bytes, page_num_1_indexed - 1)
            annotated_bytes = draw_bounding_boxes(raw_img_bytes, entities, page_num_1_indexed)
            
            if annotated_bytes:
                b64_img = base64.b64encode(annotated_bytes).decode('utf-8')
                annotated_images.append(f"data:image/jpeg;base64,{b64_img}")
        except Exception as e:
            logger.error(f"Failed to draw annotations for page {page_num_1_indexed}: {e}")
         
    # 5. Insert into BigQuery
    from .bigquery import insert_embeddings_to_bq
    insert_embeddings_to_bq(output_rows)
         
    return {
        "output_rows": output_rows,
        "annotated_images": annotated_images,
        "traces": [t.model_dump() for t in traces]
    }
