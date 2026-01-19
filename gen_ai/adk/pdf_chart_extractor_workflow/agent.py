import asyncio
import os
import sys
import json
import logging
from typing import List, Any
from copy import deepcopy

# Add project root to path
sys.path.append(os.getcwd())

from pydantic import BaseModel, Field
from google.adk.agents import Agent, ParallelAgent
from google.adk.models import LlmRequest
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool

# Import utils
from pdf_chart_extractor_workflow.utils import (
    split_pdf_logically, 
    insert_into_bigquery, 
    upload_to_gcs, 
    draw_bounding_boxes
)

# Environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Workflow")

# --- Schemas ---

class BoundingBox(BaseModel):
    ymin: float = Field(description="Normalized Y coordinate (0-1000) for top")
    xmin: float = Field(description="Normalized X coordinate (0-1000) for left")
    ymax: float = Field(description="Normalized Y coordinate (0-1000) for bottom")
    xmax: float = Field(description="Normalized X coordinate (0-1000) for right")

class ChartObject(BaseModel):
    label: str = Field(description="Label or name of the object identified inside the chart")
    text_confidence: float = Field(description="Confidence score for the text/label extracted (0.0 to 1.0)")
    bounding_box: BoundingBox = Field(description="Bounding box of this specific object within the chart")

class ChartData(BaseModel):
    headers: List[str] = Field(description="Column headers of the extracted table")
    rows: List[List[Any]] = Field(description="Data rows corresponding to the headers")

class ChartExtraction(BaseModel):
    page_number: int = Field(description="Page number where the chart was found")
    chart_bounding_box: BoundingBox = Field(description="Bounding box of the entire chart/diagram on the PDF page")
    description: str = Field(description="A very detailed, precise, and lengthy description of the chart/diagram.")
    confidence: float = Field(description="Confidence level of the overall chart extraction (0.0 to 1.0)")
    objects_inside: List[ChartObject] = Field(description="List of distinct objects found inside the chart with their bounding boxes and label confidence")
    extracted_data: ChartData = Field(description="Structured tabular data extracted from the chart")

class TableExtraction(BaseModel):
    page_number: int = Field(description="Page number where the table was found")
    table_bounding_box: BoundingBox = Field(description="Bounding box of the table on the PDF page")
    description: str = Field(description="A detailed description of the table's purpose and content.")
    confidence: float = Field(description="Confidence level of the extraction (0.0 to 1.0)")
    extracted_data: ChartData = Field(description="Structured tabular data")

class PdfExtractionResult(BaseModel):
    charts: List[ChartExtraction] = Field(description="List of all charts/diagrams found in the PDF")
    tables: List[TableExtraction] = Field(description="List of all standalone tables found in the PDF")

# --- Globals ---
CURRENT_PDF_PATH = "example_pdf.pdf"
AGGREGATED_DATA = {"charts": [], "tables": []}

# --- Callbacks ---

def pdf_injection_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """Injects the PDF file into the prompt."""
    try:
        if os.path.exists(CURRENT_PDF_PATH):
            with open(CURRENT_PDF_PATH, "rb") as f:
                pdf_bytes = f.read()
            pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
            llm_request.contents[-1].parts.append(pdf_part)
    except Exception as e:
        logger.error(f"Error injecting PDF: {e}")

# --- Tool Definitions ---

def store_in_bq_tool():
    """Stores the aggregated data from the workflow into BigQuery in a flattened format."""
    try:
        data = AGGREGATED_DATA
        rows_to_insert = []
        
        def flatten_item(item, item_type, idx):
            item_dict = item if isinstance(item, dict) else item.dict()
            page = item_dict.get('page_number')
            desc = item_dict.get('description')
            conf = item_dict.get('confidence')
            
            # Get data
            ext_data = item_dict.get('extracted_data', {})
            # Handle if it's a dict or object
            if hasattr(ext_data, 'dict'): ext_data = ext_data.dict()
            
            headers = ext_data.get('headers', [])
            data_rows = ext_data.get('rows', [])
            
            element_id = f"{item_type}_{page}_{idx}"
            
            for r_idx, row_vals in enumerate(data_rows):
                for c_idx, cell_val in enumerate(row_vals):
                    # Safety check for column bounds
                    col_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx}"
                    
                    bq_row = {
                        "page": page,
                        "type": item_type,
                        "element_id": element_id,
                        "description": desc,
                        "confidence": conf,
                        "row_index": r_idx,
                        "column_name": str(col_name),
                        "cell_value": str(cell_val)
                    }
                    rows_to_insert.append(bq_row)

        for i, chart in enumerate(data.get('charts', [])):
            flatten_item(chart, "CHART", i)
            
        for i, table in enumerate(data.get('tables', [])):
            flatten_item(table, "TABLE", i)
            
        if not rows_to_insert:
            return "No data found in global state to store."
            
        insert_into_bigquery(rows_to_insert, "vtxdemos", "esg_demo_data", "pdf_extractions")
        return f"Successfully stored {len(rows_to_insert)} flattened cells in BigQuery."
    except Exception as e:
        logger.exception("BQ Store Failed")
        return f"Failed to store data: {e}"

def visualize_tool():
    """Visualizes the aggregated data by drawing bounding boxes and uploading to GCS."""
    try:
        data = AGGREGATED_DATA
        
        # Reconstruct objects for the util
        items = []
        for c in data.get('charts', []):
            items.append(ChartExtraction(**c))
        for t in data.get('tables', []):
            items.append(TableExtraction(**t))
            
        if not items:
            return "No items to visualize."

        output_files = draw_bounding_boxes(CURRENT_PDF_PATH, items, ".")
        
        results = []
        for fpath in output_files:
            fname = os.path.basename(fpath)
            # Add random suffix to avoid collision/caching issues
            blob_name = f"annotated_{os.urandom(4).hex()}_{fname}"
            upload_to_gcs(fpath, "vtxdemos-staging", blob_name)
            results.append(f"gs://vtxdemos-staging/{blob_name}")
            
        return f"Visualization created and uploaded: {', '.join(results)}"
    except Exception as e:
        logger.exception("Visualization Failed")
        return f"Visualization error: {e}"

# --- Agent Factories & Definitions ---

def create_page_extractor(page_num: int) -> Agent:
    return Agent(
        name=f"extractor_page_{page_num}",
        model="gemini-2.5-pro",
        description=f"Extracts charts and tables specifically from page {page_num}.",
        instruction=f"""
        Analyze the provided PDF file.
        FOCUS ONLY ON PAGE {page_num}. Do not extract content from other pages.
        1. Identify charts, diagrams, and standalone tables on Page {page_num}.
        2. Extract structured data, bounding boxes, and object details.
        3. Provide confidence scores for the chart/table and for individual text labels.
        4. Return the result strictly matching the provided schema.
        """,
        output_schema=PdfExtractionResult,
        before_model_callback=pdf_injection_callback
    )

evaluator_agent = Agent(
    name="evaluator_agent",
    model="gemini-2.5-flash",
    description="Evaluates the quality and confidence of extracted data.",
    instruction="""
    You are a Quality Assurance AI.
    Review the provided JSON extraction results.
    1. Check if confidence scores are acceptable (> 0.8).
    2. Verify that bounding boxes are normalized (0-1000).
    3. Summarize the quality of the extraction.
    Return a brief approval or list of warnings.
    """
)

storage_agent = Agent(
    name="storage_agent",
    model="gemini-2.5-flash",
    description="Stores extracted data into BigQuery.",
    instruction="""
    The extraction data is already prepared.
    Use the `store_in_bq_tool` to save it to BigQuery.
    Do not pass any arguments to the tool.
    """,
    tools=[store_in_bq_tool]
)

visualization_agent = Agent(
    name="visualization_agent",
    model="gemini-2.5-flash",
    description="Visualizes bounding boxes and uploads to GCS.",
    instruction="""
    The extraction data is already prepared.
    Use the `visualize_tool` to create and upload the annotated images.
    Do not pass any arguments to the tool.
    """,
    tools=[visualize_tool]
)

# --- Workflow ---

async def main():
    global AGGREGATED_DATA
    if not os.path.exists(CURRENT_PDF_PATH):
        print(f"File {CURRENT_PDF_PATH} not found.")
        sys.exit(1)

    print("--- 1. Splitting PDF Logically ---")
    pages = split_pdf_logically(CURRENT_PDF_PATH)
    print(f"Identified {len(pages)} pages to process.")

    print("\n--- 2. Parallel Extraction ---")
    sub_agents = [create_page_extractor(p) for p in pages]
    parallel_extractor = ParallelAgent(
        name="parallel_extractor",
        sub_agents=sub_agents
    )

    APP_NAME = "PdfWorkflow"
    USER_ID = "user"
    SESSION_ID = "workflow_session"
    
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state={})
    
    runner = Runner(agent=parallel_extractor, app_name=APP_NAME, session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text="Extract charts and tables from all pages.")])
    
    # Run Parallel Extraction
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                try:
                    data = json.loads(text)
                    if "charts" in data:
                        AGGREGATED_DATA["charts"].extend(data["charts"])
                    if "tables" in data:
                        AGGREGATED_DATA["tables"].extend(data["tables"])
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        logger.error(f"Error in parallel extraction: {e}")

    print(f"\nAggregated {len(AGGREGATED_DATA['charts'])} charts and {len(AGGREGATED_DATA['tables'])} tables.")
    
    if not AGGREGATED_DATA["charts"] and not AGGREGATED_DATA["tables"]:
        print("No data extracted. Aborting subsequent steps.")
        return

    json_str = json.dumps(AGGREGATED_DATA) # Still used for evaluator prompt
    
    print("\n--- 3. Evaluation ---")
    eval_runner = Runner(agent=evaluator_agent, app_name=APP_NAME, session_service=session_service)
    eval_content = types.Content(role='user', parts=[types.Part(text=f"Evaluate this extraction: {json_str}")])
    
    try:
        async for event in eval_runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=eval_content):
            if event.is_final_response() and event.content:
                 print("Evaluation Result:", event.content.parts[0].text)
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")

    print("\n--- 4. Storage ---")
    store_runner = Runner(agent=storage_agent, app_name=APP_NAME, session_service=session_service)
    store_content = types.Content(role='user', parts=[types.Part(text="Store the extracted data.")])
    
    try:
        async for event in store_runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=store_content):
            if event.is_final_response() and event.content:
                 print("Storage Result:", event.content.parts[0].text)
    except Exception as e:
        logger.error(f"Error in storage: {e}")

    print("\n--- 5. Visualization ---")
    vis_runner = Runner(agent=visualization_agent, app_name=APP_NAME, session_service=session_service)
    vis_content = types.Content(role='user', parts=[types.Part(text="Visualize the data.")])
    
    try:
        async for event in vis_runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=vis_content):
            if event.is_final_response() and event.content:
                 print("Visualization Result:", event.content.parts[0].text)
    except Exception as e:
        logger.error(f"Error in visualization: {e}")

if __name__ == "__main__":
    asyncio.run(main())