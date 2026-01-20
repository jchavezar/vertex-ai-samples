import os
import asyncio
from contextlib import asynccontextmanager

# --- Configuration: Restore Vertex AI (Global) ---
# Mimic the User's working GCE VM setup exactly
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

print(f"--- STARTUP ENV CHECK ---")
print(f"GOOGLE_GENAI_USE_VERTEXAI: {os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
print(f"GOOGLE_CLOUD_LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
print(f"-------------------------")

import uuid
import json
import base64
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from utils import pdf_to_images, draw_legend_sidebar, upload_to_gcs, insert_to_bq
from agent_logic import create_page_extractor_agent, create_evaluator_agent, PdfExtractionResult
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import debug script
# import debug_vertex

app = FastAPI(title="PDF Chart Extractor API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

session_service = InMemorySessionService()

class ExtractionResponse(BaseModel):
    session_id: str
    results: Any
    annotated_images: List[str] # List of static URLs
    gcs_urls: List[str] # List of GCS URLs
    bq_status: str
    bq_link: str

import asyncio

@app.post("/extract", response_model=ExtractionResponse)
async def extract_pdf(
    file: UploadFile = File(...),
    extractor_model: str = Form("projects/vtxdemos/locations/global/publishers/google/models/gemini-3-flash-preview"),
    supporting_model: str = Form("projects/vtxdemos/locations/global/publishers/google/models/gemini-3-flash-preview")
):
    session_id = str(uuid.uuid4())
    pdf_bytes = await file.read()
    
    # 1. Convert PDF to Images (Splitting into pages)
    images = pdf_to_images(pdf_bytes)
    
    async def process_page(i, img_bytes):
        page_num = i + 1
        # Create agent for this specific page and model
        agent = create_page_extractor_agent(page_num, model_id=extractor_model)
        runner = Runner(agent=agent, app_name="PdfExtractor", session_service=session_service)
        await session_service.create_session(app_name="PdfExtractor", user_id="web_user", session_id=f"{session_id}_{page_num}")

        content = types.Content(
            role='user',
            parts=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                types.Part(text=f"Extract charts and tables from page {page_num}")
            ]
        )
        
        print(f"Processing Page {page_num} in PARALLEL with model {extractor_model}...")
        result_text = ""
        try:
            async for event in runner.run_async(user_id="web_user", session_id=f"{session_id}_{page_num}", new_message=content):
                if event.is_final_response() and event.content:
                    result_text = event.content.parts[0].text
            
            data = json.loads(result_text)
            page_charts = data.get("charts", [])
            page_tables = data.get("tables", [])
            
            # Combine all for visualization
            boxes = []
            for item in page_charts + page_tables:
                bbox = item.get("chart_bounding_box") or item.get("table_bounding_box")
                desc = item.get("description", "Object")
                if bbox:
                    boxes.append({
                        "box_2d": [bbox["ymin"], bbox["xmin"], bbox["ymax"], bbox["xmax"]],
                        "label": desc[:30] + "..."
                    })
            
            annotated_url = None
            gcs_url = None
            if boxes:
                annotated_img = draw_legend_sidebar(img_bytes, boxes)
                filename = f"{session_id}_page_{page_num}.jpg"
                filepath = os.path.join(STATIC_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(annotated_img)
                annotated_url = f"/static/{filename}"
                
                # Upload to GCS
                try:
                    gcs_url = upload_to_gcs(annotated_img, "vtxdemos-staging", filename)
                except Exception as e:
                    print(f"GCS Upload Error: {e}")
                    gcs_url = f"gs://vtxdemos-staging/{filename}"
            
            return page_charts, page_tables, annotated_url, gcs_url
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            return [], [], None, None

    # Run all pages in parallel with concurrency limit
    print(f"Starting parallel processing for {len(images)} pages...")
    
    # Dynamic Semaphore Limit based on Model
    # Gemini 3 Pro Preview might have strict quotas.
    # Gemini 3 Flash and others are production-ready with higher limits.
    limit = 200
    if "gemini-3-pro" in extractor_model.lower():
        limit = 8
        
    print(f"Applying concurrency limit: {limit} (Model: {extractor_model})")
    sem = asyncio.Semaphore(limit) 

    async def process_page_with_limit(i, img):
        async with sem:
            return await process_page(i, img)

    tasks = [process_page_with_limit(i, img) for i, img in enumerate(images)]
    results = await asyncio.gather(*tasks)

    # Aggregate results
    all_charts = []
    all_tables = []
    annotated_urls = []
    gcs_urls = []
    
    for page_charts, page_tables, annotated_url, gcs_url in results:
        all_charts.extend(page_charts)
        all_tables.extend(page_tables)
        if annotated_url:
            annotated_urls.append(annotated_url)
        if gcs_url:
            gcs_urls.append(gcs_url)

    # Final BQ storage
    bq_status = "Skipped"
    bq_link = "https://console.cloud.google.com/bigquery?project=vtxdemos&p=vtxdemos&d=esg_demo_data&t=pdf_extractions&page=table"
    
    if all_charts or all_tables:
        try:
            rows = []
            
            def flatten_item(item, item_type, idx):
                page = item.get('page_number')
                desc = item.get('description')
                conf = item.get('confidence')
                ext_data = item.get('extracted_data') or {}
                
                headers = ext_data.get('headers', [])
                data_rows = ext_data.get('rows', [])
                element_id = f"{item_type}_{page}_{idx}_{uuid.uuid4().hex[:4]}"
                
                # If no data rows, still insert a metadata row? 
                # Or just skip if the table is empty.
                if not data_rows:
                    rows.append({
                        "page": page,
                        "type": item_type,
                        "element_id": element_id,
                        "description": desc,
                        "confidence": conf,
                        "row_index": 0,
                        "column_name": "Metadata",
                        "cell_value": "No tabular data extracted"
                    })
                    return

                for r_idx, row_vals in enumerate(data_rows):
                    for c_idx, cell_val in enumerate(row_vals):
                        col_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx}"
                        rows.append({
                            "page": page,
                            "type": item_type,
                            "element_id": element_id,
                            "description": desc,
                            "confidence": conf,
                            "row_index": r_idx,
                            "column_name": str(col_name),
                            "cell_value": str(cell_val)
                        })

            for i, chart in enumerate(all_charts):
                flatten_item(chart, "CHART", i)
            for i, table in enumerate(all_tables):
                flatten_item(table, "TABLE", i)

            if rows:
                insert_to_bq(rows, "esg_demo_data", "pdf_extractions")
                bq_status = f"Success: {len(rows)} flattened rows inserted"
        except Exception as e:
            print(f"BQ Insert Error (Schema mismatch?): {e}")
            bq_status = f"Error: {e}"

    return ExtractionResponse(
        session_id=session_id,
        results={"charts": all_charts, "tables": all_tables},
        annotated_images=annotated_urls,
        gcs_urls=gcs_urls,
        bq_status=bq_status,
        bq_link=bq_link
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
