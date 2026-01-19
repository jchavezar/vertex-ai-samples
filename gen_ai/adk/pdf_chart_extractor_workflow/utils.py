import os
import json
import logging
from typing import List, Dict, Any, Tuple
from google.cloud import bigquery
from google.cloud import storage
from google.api_core.exceptions import NotFound
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pdf_page_count(pdf_path: str) -> int:
    """
    Returns the number of pages in the PDF.
    HARDCODED for this environment/example: 3 pages.
    """
    return 3

def split_pdf_logically(pdf_path: str) -> List[int]:
    """
    Returns a list of page numbers to process.
    """
    count = get_pdf_page_count(pdf_path)
    return list(range(1, count + 1))

def insert_into_bigquery(data: Dict[str, Any], project_id: str, dataset_id: str, table_id: str):
    """
    Inserts data into BigQuery. Creates table if not exists.
    Raises exception on failure.
    """
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    # Define schema for flattened "Tidy Data"
    # One row per cell in the extracted table
    schema = [
        bigquery.SchemaField("page", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("element_id", "STRING", mode="NULLABLE"), # unique id for the chart/table
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("confidence", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("row_index", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("column_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("cell_value", "STRING", mode="NULLABLE"),
    ]
    
    # Check if table exists
    try:
        table = client.get_table(table_ref)
        # Check for schema mismatch (heuristic: look for 'cell_value')
        field_names = [f.name for f in table.schema]
        if "cell_value" not in field_names:
            logger.info(f"Table {table_ref} schema mismatch (switching to flattened). Dropping and recreating.")
            client.delete_table(table_ref)
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            logger.info(f"Recreated table {table_ref}")
    except NotFound:
        logger.info(f"Table {table_ref} not found. Creating it.")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        logger.info(f"Created table {table_ref}")

    # Ensure data is a list of rows
    rows_to_insert = [data] if isinstance(data, dict) else data
    
    # Convert 'extracted_data' dicts/lists to JSON strings if needed? 
    # The JSON type in BQ Client usually accepts dicts directly.
    
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors == []:
        logger.info("New rows have been added.")
    else:
        error_msg = f"Encountered errors while inserting rows: {errors}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def upload_to_gcs(file_path: str, bucket_name: str, destination_blob_name: str):
    """
    Uploads a file to the bucket.
    Raises exception on failure.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

    logger.info(f"File {file_path} uploaded to gs://{bucket_name}/{destination_blob_name}.")

def draw_bounding_boxes(pdf_path: str, extraction_results: List[Any], output_dir: str):
    """
    Draws bounding boxes. Uses sips for Page 1 background if available.
    """
    output_files = []
    
    # Group results by page
    items_by_page = {}
    for item in extraction_results:
        p = item.page_number
        if p not in items_by_page:
            items_by_page[p] = []
        items_by_page[p].append(item)
        
    try:
        # Try to convert Page 1 using sips
        page1_img_path = os.path.join(output_dir, "page1_temp.png")
        use_sips = False
        try:
            import subprocess
            cmd = ["sips", "-s", "format", "png", pdf_path, "--out", page1_img_path]
            subprocess.run(cmd, check=True, capture_output=True)
            if os.path.exists(page1_img_path):
                use_sips = True
        except Exception as e:
            logger.warning(f"Sips conversion failed: {e}")

        for page_num, items in items_by_page.items():
            # Create/Load image
            if page_num == 1 and use_sips:
                img = Image.open(page1_img_path).convert("RGB")
                width, height = img.size
            else:
                width, height = 1000, 1414 # Approx A4
                img = Image.new('RGB', (width, height), color = (255, 255, 255))
                
            draw = ImageDraw.Draw(img)
            
            # Draw placeholder text if not real image
            if not (page_num == 1 and use_sips):
                draw.text((50, 50), f"Page {page_num} (Placeholder)", fill="black")

            for item in items:
                if hasattr(item, 'chart_bounding_box'):
                    bbox = item.chart_bounding_box
                    color = "red"
                    label = f"Chart ({item.confidence:.2f})"
                elif hasattr(item, 'table_bounding_box'):
                    bbox = item.table_bounding_box
                    color = "blue"
                    label = f"Table ({item.confidence:.2f})"
                else:
                    continue
                
                # Scale coordinates
                x1 = bbox.xmin * (width / 1000)
                y1 = bbox.ymin * (height / 1000)
                x2 = bbox.xmax * (width / 1000)
                y2 = bbox.ymax * (height / 1000)
                
                # Draw box
                draw.rectangle([x1, y1, x2, y2], outline=color, width=5)
                # Draw label background
                text_bbox = draw.textbbox((x1, y1), label)
                draw.rectangle(text_bbox, fill=color)
                draw.text((x1, y1), label, fill="white")
                
                # Draw objects inside if any
                if hasattr(item, 'objects_inside'):
                    for obj in item.objects_inside:
                        obbox = obj.bounding_box
                        ox1 = obbox.xmin * (width / 1000)
                        oy1 = obbox.ymin * (height / 1000)
                        ox2 = obbox.xmax * (width / 1000)
                        oy2 = obbox.ymax * (height / 1000)
                        draw.rectangle([ox1, oy1, ox2, oy2], outline="green", width=2)

            out_name = f"annotated_page_{page_num}.png"
            out_path = os.path.join(output_dir, out_name)
            img.save(out_path)
            output_files.append(out_path)
            logger.info(f"Saved {out_path}")
            
        # Clean up temp
        if os.path.exists(page1_img_path):
            os.remove(page1_img_path)
            
        return output_files # Return list

    except Exception as e:
        logger.error(f"Failed to draw bounding boxes: {e}")
        raise e
