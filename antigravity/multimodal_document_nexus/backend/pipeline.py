
# ========================================
# Content from schemas.py
# ========================================
from pydantic import BaseModel, Field
from typing import List, Any, Optional

class ExtractedEntity(BaseModel):
    page_number: int = Field(description="The page number in the original document.")
    entity_type: str = Field(description="'TEXT', 'TABLE', or 'CHART'")
    content_description: str = Field(description="The actual text content. For tables and charts, provide a detailed description and the FULL TABLE DATA IN MARKDOWN FORMAT.")
    structured_data: Optional[dict] = Field(description="Optional parsed JSON dictionary for tabular data (headers, rows).", default=None)
    box_2d: Optional[List[int]] = Field(description="Normalized bounding box [ymin, xmin, ymax, xmax] from 0-1000.", default=None)
    embedding: Optional[List[float]] = Field(description="3072-dimensional embedding vector assigned post-extraction.", default=None)
    
class DocumentPageResult(BaseModel):
    page_number: int = Field(description="Page number analyzed")
    entities: List[ExtractedEntity] = Field(description="List of entities (text chunks, tables, charts) identified on this page.")
    
class BQFeatureStoreRow(BaseModel):
    """Schema for final structured insertion into BigQuery for Vertex AI Feature Store."""
    chunk_id: str = Field(description="Unique ID for this chunk (e.g., page_num_entity_idx)")
    document_name: str = Field(description="Source document name")
    page_number: int = Field(description="The page number where this chunk was found")
    entity_type: str = Field(description="Type of entity: TEXT, TABLE, CHART")
    content: str = Field(description="The text content or description used to generate the embedding")
    embedding: List[float] = Field(description="3072-dimensional embedding vector")

class ADKTrace(BaseModel):
    """Schema for returning ADK execution traces back to the frontend dashboard."""
    agent_name: str = Field(description="Name of the agent executing the extraction")
    page_number: int = Field(description="The page number this agent processed")
    start_time: str = Field(description="ISO timestamp of when the agent started")
    end_time: str = Field(description="ISO timestamp of when the agent finished")
    duration_seconds: float = Field(description="Total execution time in seconds")
    entities_extracted: int = Field(description="Number of entities found on the page")


# ========================================
# Content from utils.py
# ========================================
import os
import io
import base64
import fitz
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
from pypdf import PdfReader, PdfWriter

def split_pdf_logically(pdf_bytes: bytes, max_pages_per_chunk: int = 1) -> List[Dict[str, Any]]:
    """
    Splits a PDF locally into separate single-page chunks to be parsed independently.
    Uses in-memory bytes streams to optimize latency instead of disk writes.
    Returns a list of dicts containing the bytes and metadata.
    """
    chunks = []
    
    # Read the PDF from memory
    pdf_stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    num_pages = len(reader.pages)

    for i in range(0, num_pages, max_pages_per_chunk):
        writer = PdfWriter()
        end_idx = min(i + max_pages_per_chunk, num_pages)
        for j in range(i, end_idx):
             writer.add_page(reader.pages[j])
        
        # Write the split page(s) to a memory buffer
        out_stream = io.BytesIO()
        writer.write(out_stream)
        chunk_bytes = out_stream.getvalue()
        out_stream.close()
        
        chunks.append({
             "start_page": i + 1,
             "end_page": end_idx,
             "pdf_bytes": chunk_bytes,
             "mime_type": "application/pdf"
        })

    pdf_stream.close()
    return chunks

def pdf_page_to_image(pdf_bytes: bytes, page_num: int) -> bytes:
    """Converts a specific PDF page (0-indexed) to a JPEG image bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page_num >= len(doc):
        return b""
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher resolution
    img_data = pix.tobytes("jpeg")
    return img_data

def draw_bounding_boxes(image_bytes: bytes, entities_with_boxes: List[Any], original_page_num: int) -> bytes:
    """
    Draws bounding boxes over the image and adds a sidebar legend.
    entities_with_boxes should be a list of ExtractedEntity objects with bounding_box mapped.
    """
    if not image_bytes or not entities_with_boxes:
        return image_bytes
        
    # Filter entities to only draw boxes for non-text items
    visual_entities = []
    for idx_or_i, item in enumerate(entities_with_boxes):
        if isinstance(item, tuple) and len(item) == 2:
            entity, global_idx = item
        else:
            entity, global_idx = item, idx_or_i
            
        if hasattr(entity, 'entity_type') and entity.entity_type.lower() in ['chart', 'image', 'table']:
            visual_entities.append((entity, global_idx))

    if not visual_entities:
        return image_bytes

    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = im.size
    draw = ImageDraw.Draw(im)
    
    # Modern high-contrast vibrant palette
    VIBRANT_COLORS = [
        "#FF3D00", "#00E676", "#2979FF", "#FFEA00", "#D500F9", 
        "#00E5FF", "#FF9100", "#1DE9B6", "#C6FF00", "#FF1744"
    ]
    
    title_size = max(28, int(height / 30))
    body_size = max(22, int(height / 40))

    try:
        base_size = max(20, int(min(width, height) / 35))
        label_font = ImageFont.truetype("Arial.ttf", size=base_size)
    except OSError:
        label_font = ImageFont.load_default()

    # Draw boxes
    for visual_idx, (entity, global_idx) in enumerate(visual_entities):
        if not hasattr(entity, 'box_2d') or not entity.box_2d or len(entity.box_2d) != 4:
            continue
            
        bb = entity.box_2d
        y_min, x_min, y_max, x_max = [int(v / 1000 * (height if j%2==0 else width)) 
                                      for j, v in enumerate(bb)]
        
        color = VIBRANT_COLORS[visual_idx % len(VIBRANT_COLORS)]
        
        # Bounding box
        draw.rectangle(((x_min, y_min), (x_max, y_max)), outline=color, width=4)
        draw.rectangle(((x_min-1, y_min-1), (x_max+1, y_max+1)), outline="white", width=1)
        
        # Pill Tag
        tag_text = f" {global_idx} "
        try:
            tw, th = label_font.getbbox(tag_text)[2:]
        except:
            tw, th = 30, 30

        pill_padding = 6
        pill_rect = [x_min, y_min - th - (pill_padding * 2), x_min + tw + (pill_padding * 2), y_min]
        if pill_rect[1] < 0:
            pill_rect[1] = y_min
            pill_rect[3] = y_min + th + (pill_padding * 2)

        draw.rectangle(pill_rect, fill=color)
        draw.text((pill_rect[0] + pill_padding, pill_rect[1] + pill_padding), tag_text, fill="white", font=label_font)

    # 3. Create Sidebar
    sidebar_width = 500
    new_width = width + sidebar_width
    badge_h = 45
    required_height = 60 + title_size * 2 + len(visual_entities) * int(badge_h * 1.6)
    final_height = max(height, required_height)

    combined = Image.new("RGB", (new_width, final_height), (15, 15, 20)) # Deep navy-black
    combined.paste(im, (0, 0))
    
    s_draw = ImageDraw.Draw(combined)
    
    try:
        title_font = ImageFont.truetype("Arial.ttf", size=title_size)
        body_font = ImageFont.truetype("Arial.ttf", size=body_size)
    except OSError:
        title_font = body_font = ImageFont.load_default()

    s_draw.text((width + 30, 30), f"PAGE {original_page_num} ENTITIES", fill="#64B5F6", font=title_font)
    s_draw.line((width + 30, 30 + title_size + 10, width + 470, 30 + title_size + 10), fill="#2C2C3E", width=2)

    current_y = 60 + title_size * 2
    for visual_idx, (entity, global_idx) in enumerate(visual_entities):
        if not hasattr(entity, 'box_2d') or not entity.box_2d or len(entity.box_2d) != 4:
            continue
            
        color = VIBRANT_COLORS[visual_idx % len(VIBRANT_COLORS)]
        content_preview = ""
        if hasattr(entity, 'content_description') and entity.content_description:
            content_preview = entity.content_description
        elif hasattr(entity, 'content') and entity.content:
            content_preview = entity.content
        label_text = f"[{entity.entity_type}] {content_preview[:30].replace(chr(10), ' ')}..."
        
        # Badge
        badge_w = 45
        s_draw.rounded_rectangle([width + 30, current_y, width + 30 + badge_w, current_y + badge_h], radius=8, fill=color)
        s_draw.text((width + 42, current_y + 8), str(global_idx), fill="white", font=body_font)
        
        # Text
        s_draw.text((width + 90, current_y + 8), label_text, fill="#E0E0E0", font=body_font)
        
        current_y += int(badge_h * 1.6)

    output = io.BytesIO()
    combined.save(output, format="JPEG", quality=85)
    return output.getvalue()

# ========================================
# Content from embeddings.py
# ========================================
import logging
import os
from typing import List
from google import genai
from google.genai.types import EmbedContentConfig


logger = logging.getLogger(__name__)

async def generate_embeddings_for_entities(entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
    """
    Takes a list of normalized ExtractedEntities, generates embeddings asynchronously for their content,
    and returns the updated list.
    """
    if not entities:
        return []

    client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location=os.environ.get("GOOGLE_CLOUD_LOCATION"))
    
    # We will embed the 'content_description' text
    contents_to_embed = []
    for entity in entities:
        text = entity.content_description
        if entity.structured_data:
            text += f"\nStructured Data Context: {str(entity.structured_data)}"
        contents_to_embed.append(text)
        
    try:
        # Vertex AI embeddings limit is 250 instances per prediction call,
        # but also max 20,000 total tokens per call.
        batch_size = 50
        all_embeddings = []
        
        for i in range(0, len(contents_to_embed), batch_size):
            batch = contents_to_embed[i:i + batch_size]
            try:
                response = await client.aio.models.embed_content(
                    model="text-embedding-004", # Standard Vertex AI text embedding model
                    contents=batch,
                    config=EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=768,
                    ),
                )
                if response.embeddings:
                    all_embeddings.extend(response.embeddings)
            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i//batch_size}: {e}")
                # Append empty embeddings for this failed batch to keep alignment
                all_embeddings.extend([None] * len(batch))
        
        if len(all_embeddings) != len(entities):
            logger.error(f"Mismatch in embedding count returned. Expected {len(entities)}, got {len(all_embeddings)}.")
            # We can't safely align them, so we just set all to empty
            for entity in entities:
                entity.embedding = []
            return entities
            
        for i, entity in enumerate(entities):
            # If the embedding failed for a batch, it will be None here, so we replace with []
            val = all_embeddings[i]
            entity.embedding = val.values if val and hasattr(val, 'values') else []
            
    except Exception as e:
        logger.error(f"Failed to generate async embeddings entirely: {e}")
        for entity in entities:
            entity.embedding = []
        
    return entities

# ========================================
# Content from bigquery.py
# ========================================
import logging
import os
from typing import List, Dict, Any
from google.cloud import bigquery

logger = logging.getLogger(__name__)

def insert_embeddings_to_bq(rows: List[Dict[str, Any]], dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs"):
    """
    Inserts a list of dictionaries (rows) into the specified BigQuery table.
    Expects rows to match the schema of the target table.
    """
    if not rows:
        return
        
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT not set, skipping BQ insertion.")
        return
        
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    try:
        # Check if dataset exists, create if not
        dataset_ref = client.dataset(dataset_id)
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            logger.info(f"Dataset {dataset_id} not found, attempting to create it...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US" # Standard multi-region
            client.create_dataset(dataset)
            
        # Check if table exists
        try:
             client.get_table(table_ref)
        except Exception as e:
             logger.warning(f"Failed to get table {table_ref}, will attempt to create it. {e}")
             schema = [
                 bigquery.SchemaField("chunk_id", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("document_name", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("page_number", "INTEGER", mode="REQUIRED"),
                 bigquery.SchemaField("entity_type", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                 # For Feature Store, embeddings are often standard FLOAT arrays
                 bigquery.SchemaField("embedding", "FLOAT", mode="REPEATED")
             ]
             table = bigquery.Table(table_ref, schema=schema)
             client.create_table(table)
             logger.info(f"Created table {table_ref}")
             
             import time
             time.sleep(2) # Give BQ a moment to register the new table
        
        # Filter rows to only include expected schema fields
        valid_fields = {"chunk_id", "document_name", "page_number", "entity_type", "content", "embedding"}
        cleaned_rows = []
        for row in rows:
            cleaned_row = {k: v for k, v in row.items() if k in valid_fields}
            cleaned_rows.append(cleaned_row)
            
        # Use a load job instead of streaming inserts so records are immediately searchable by VECTOR_SEARCH
        # and so they can be DELETEd if necessary without hitting streaming buffer limitations.
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition="WRITE_APPEND",
            schema=[
                bigquery.SchemaField("chunk_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("document_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("page_number", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("entity_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("embedding", "FLOAT", mode="REPEATED")
            ]
        )
        
        load_job = client.load_table_from_json(cleaned_rows, table_ref, job_config=job_config)
        load_job.result()  # Waits for the job to complete.
        
        if load_job.errors:
            logger.error(f"Failed to load rows into BigQuery: {load_job.errors}")
        else:
            logger.info(f"Successfully loaded {len(cleaned_rows)} rows into {table_ref}.")
            
    except Exception as e:
        logger.error(f"Error during BigQuery operation: {e}")

def get_indexed_documents_bq(dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> List[Dict[str, Any]]:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id: return []
    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    query = f"SELECT document_name, COUNT(*) as chunk_count FROM {table_ref} GROUP BY document_name ORDER BY document_name"
    try:
        query_job = client.query(query)
        rows = query_job.result()
        return [{"document_name": row.document_name, "chunk_count": row.chunk_count} for row in rows]
    except Exception as e:
        logger.error(f"Error fetching documents from BQ: {e}")
        return []

def delete_document_from_bq(document_name: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> bool:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id: return False
    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    query = f"DELETE FROM {table_ref} WHERE document_name = @document_name"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("document_name", "STRING", document_name),
        ]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return True
    except Exception as e:
        logger.error(f"Error deleting document from BQ: {e}")
        return False

async def search_embeddings_in_bq(query_text: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs", top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embeds the query text and uses BigQuery VECTOR_SEARCH to find the most relevant chunks.
    """
    from google import genai
    from google.genai.types import EmbedContentConfig
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not project_id:
        return []

    client_genai = genai.Client(vertexai=True, project=project_id, location=location)
        
    # 1. Embed the query
    try:
        response = await client_genai.aio.models.embed_content(
            model="text-embedding-004",
            contents=query_text,
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768,
            )
        )
        if not response.embeddings:
            return []
        query_vector = response.embeddings[0].values
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []



    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    
    # 2. Run VECTOR_SEARCH
    # BQ VECTOR_SEARCH requires the input to be a table, so we use a CTE
    query = f"""
    WITH query_table AS (
      SELECT {query_vector} AS embedding 
    )
    SELECT base.document_name, base.chunk_id, base.page_number, base.entity_type, base.content, distance
    FROM VECTOR_SEARCH(
      TABLE {table_ref},
      'embedding',
      (SELECT * FROM query_table),
      top_k => @top_k,
      distance_type => 'COSINE'
    )
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
        ]
    )
    
    results = []
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        for row in rows:
            results.append({
                "document_name": row.document_name,
                "chunk_id": row.chunk_id,
                "page_number": row.page_number,
                "entity_type": row.entity_type,
                "content": row.content,
                "distance": row.distance
            })
    except Exception as e:
        logger.error(f"VECTOR_SEARCH failed: {e}")
        
    return results

def get_document_chunks_from_bq(document_name: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> List[Dict[str, Any]]:
    """Retrieves all chunks for a specific document to load the dashboard."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return []
    
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    query = f"""
    SELECT document_name, chunk_id, page_number, entity_type, content
    FROM `{table_ref}`
    WHERE document_name = @doc_name
    ORDER BY page_number, chunk_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("doc_name", "STRING", document_name),
        ]
    )
    
    results = []
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        for row in rows:
            results.append({
                "document_name": row.document_name,
                "chunk_id": row.chunk_id,
                "page_number": int(row.page_number) if row.page_number else 0,
                "entity_type": row.entity_type,
                "content": row.content,
                "distance": 0.0 # Add default distance for frontend compatibility
            })
    except Exception as e:
        logger.error(f"Failed to fetch document chunks: {e}")
        
    return results

def get_all_indexed_chunks_from_bq(dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs", limit: int = 1000) -> List[Dict[str, Any]]:
    """Retrieves chunks from all indexed documents to load the global dashboard."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return []
    
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    query = f"""
    SELECT document_name, chunk_id, page_number, entity_type, content
    FROM `{table_ref}`
    ORDER BY document_name, page_number, chunk_id
    LIMIT @limit
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    
    results = []
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        for row in rows:
            results.append({
                "document_name": row.document_name,
                "chunk_id": row.chunk_id,
                "page_number": int(row.page_number) if row.page_number else 0,
                "entity_type": row.entity_type,
                "content": row.content,
                "distance": 0.0 # Add default distance for frontend compatibility
            })
    except Exception as e:
        logger.error(f"Failed to fetch global document chunks: {e}")
        
    return results

# ========================================
# Content from feature_store.py
# ========================================
import os
import logging
from google.cloud import aiplatform

logger = logging.getLogger(__name__)

def sync_feature_store_from_bq(
    dataset_id: str = "esg_demo_data", 
    table_id: str = "document_embeddings_fs",
    feature_store_name: str = "esg_feature_store",
    feature_view_name: str = "document_embeddings_view"
):
    """
    Creates/updates a Vertex AI Feature View based on the BigQuery table and triggers a sync.
    For this to work, the BigQuery table should ideally have a feature_timestamp column 
    and an entity_id column for standard Feature Store setups.
    
    In a simple document retrieval scenario, we treat 'chunk_id' as the entity_id.
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    
    if not project_id or not location:
        logger.warning("GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION not set, skipping Feature Store sync.")
        return

    aiplatform.init(project=project_id, location=location)
    
    bq_source_uri = f"bq://{project_id}.{dataset_id}.{table_id}"
    logger.info(f"Preparing to sync Feature Store '{feature_store_name}' from {bq_source_uri}")

    try:
        # Step 1: Get or Create Online Store (Often provisioned externally, but we can try)
        # Note: Provisioning an online store can take time. In a real app, this is done once manually.
        # We will assume it exists or fail gracefully for demo purposes.
        try:
             online_store = aiplatform.FeatureOnlineStore(feature_store_name)
             logger.info(f"Found existing FeatureOnlineStore: {feature_store_name}")
        except Exception as e:
             logger.error(f"FeatureOnlineStore {feature_store_name} not found. Please create it manually in GCP Console or via Terraform. {e}")
             return

        # Step 2: Get or Create Feature View
        try:
            feature_view = online_store.get_feature_view(feature_view_name)
            logger.info(f"Found existing FeatureView: {feature_view_name}")
        except Exception:
            logger.info(f"Creating FeatureView {feature_view_name}...")
            # We configure it for Vector Search
            from google.cloud.aiplatform.featurestore_v1.types import feature_view as feature_view_pb2
            
            # The BQ table MUST have 'embedding' column for standard Vector Search configuration
            feature_view = online_store.create_feature_view(
                name=feature_view_name,
                source=aiplatform.featurestore.BigQuerySource(
                    uri=bq_source_uri,
                    entity_id_columns=["chunk_id"] # Treat chunk ID as the unique entity
                ),
                sync_config={"cron": "TZ=America/Los_Angeles 00 00 * * *"}, # Daily sync
            )
            logger.info(f"Created FeatureView: {feature_view.name}")
            
        # Step 3: Trigger online sync
        logger.info(f"Triggering sync for FeatureView {feature_view_name}...")
        sync_response = feature_view.sync()
        logger.info(f"Sync initiated: {sync_response}")
        
    except Exception as e:
        logger.error(f"Error during Feature Store operations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Allow manual triggering
    logging.basicConfig(level=logging.INFO)
    sync_feature_store_from_bq()

# ========================================
# Content from agents.py
# ========================================
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


logger = logging.getLogger(__name__)

# --- Model definitions from user request & ADK rules ---
MODEL_EXTRACTOR = "gemini-3-flash-preview" # Better for spatial bounding boxes
MODEL_NORMALIZER = "gemini-2.5-flash" # Fast cleanup

# We define a function to create an agent for a specific page chunk
def _create_page_extractor(page_chunk: dict, page_num: int) -> LlmAgent:
    """Creates a Gemini Extractor ADK Agent for a specific page."""
    
    def inject_image(callback_context: CallbackContext, llm_request: LlmRequest, **kwargs):
        try:
             image_part = types.Part.from_bytes(
                 data=page_chunk["image_bytes"], 
                 mime_type="image/jpeg"
             )
             # Prepend or append to contents
             llm_request.contents[-1].parts.append(image_part)
        except Exception as e:
             logger.error(f"Failed to inject image bytes for page {page_num}: {e}")

    return LlmAgent(
        name=f"extractor_page_{page_num}",
        model=MODEL_EXTRACTOR,
        instruction=f"""
        Analyze the specific PAGE IMAGE provided.
        1. Identify the meaningful logical sections on the page such as titles, paragraphs, lists, charts, diagrams, or standalone tables. Create an entity for each.
        2. For text blocks: Extract the text exactly into `content_description`.
        3. For charts/images/tables (non-raw text): Describe them precisely. IF IT IS A TABLE, YOU MUST INCLUDE THE FULL TABLE DATA IN MARKDOWN FORMAT INSIDE `content_description`.
        4. Provide `box_2d` for ALL elements (text and non-text). `box_2d` must be a 2D integer array [ymin, xmin, ymax, xmax] representing the normalized bounding box coordinates (0-1000) for the visual region of the entity.
        5. Return the result strictly as a JSON object matching the requested schema.
        """,
        output_schema=DocumentPageResult,
        before_model_callback=inject_image
    )

import asyncio
from google.adk.runners import Runner

async def _process_single_page(page_agent, session_service, app_name: str, session_id: str, semaphore: asyncio.Semaphore) -> Tuple[List[DocumentPageResult], Optional[ADKTrace]]:
    """Runs a single ADK page extractor within a semaphore boundary."""
    from datetime import datetime, timezone
    import time
    
    async with semaphore:
        start_t = time.time()
        start_dt = datetime.now(timezone.utc).isoformat()
        
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

    print("DEBUG PIPELINE: Calling split_pdf_logically...", flush=True)
    chunks = split_pdf_logically(pdf_bytes, max_pages_per_chunk=1)
    print(f"DEBUG PIPELINE: split_pdf_logically returned {len(chunks)} chunks.", flush=True)
    if not chunks:
        return [], []

    # Limit concurrent requests to prevent Vertex API 503 Overloaded errors
    semaphore = asyncio.Semaphore(5)
    tasks = []
    

    for chunk in chunks:
        page_num = chunk["start_page"]
        
        # Convert the chunked PDF to a JPEG image so Gemini sees the exact same image pixels we draw on
        try:
            image_bytes = pdf_page_to_image(chunk["pdf_bytes"], 0)
            chunk["image_bytes"] = image_bytes
        except Exception as e:
            logger.error(f"Failed to rasterize chunk {page_num} for Gemini: {e}")
            continue

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
    print(f"DEBUG PIPELINE: Creating session {session_id}...", flush=True)
    await session_service.create_session(app_name=app_name, user_id="system", session_id=session_id, state={})
         
    # 1. Extraction (ADK) concurrent across all pages
    print(f"DEBUG PIPELINE: Extracting entities from {filename} in parallel...", flush=True)
    logger.info(f"Extracting entities from {filename} in parallel...")
    extracted_pages, traces = await run_parallel_extraction(file_bytes, None, session_service, app_name, session_id)
    print(f"DEBUG PIPELINE: Extraction complete!", flush=True)
    
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
             "content": entity.content_description, # Keep full content for LLM context
             "embedding": entity.embedding, # The 3072 dimension vector
             "box_2d": entity.box_2d if hasattr(entity, 'box_2d') else None
         }
         output_rows.append(row)
         
    # 4. Draw annotated images for the frontend

    import base64
    
    annotated_images = []
    # Group entities by page
    pages_to_draw = {}
    for i, entity in enumerate(embedded_entities):
        if entity.page_number not in pages_to_draw:
            pages_to_draw[entity.page_number] = []
        pages_to_draw[entity.page_number].append((entity, i))
        
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
    # DEFERRED: Let the caller route this to a BackgroundTask to avoid blocking the UI.
    # insert_embeddings_to_bq(output_rows)
    # insert_embeddings_to_bq(output_rows)
         
    # 6. Save metadata locally (bounding boxes, annotated images, traces)
    metadata = {
        "annotated_images": annotated_images,
        "traces": [t.model_dump() for t in traces],
        "boxes": {}
    }
    for i, entity in enumerate(embedded_entities):
         chunk_id = f"chunk_{filename}_{entity.page_number}_{i}"
         if hasattr(entity, 'box_2d') and entity.box_2d:
             metadata["boxes"][chunk_id] = entity.box_2d

    local_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_data")
    os.makedirs(local_data_dir, exist_ok=True)
    metadata_path = os.path.join(local_data_dir, f"{filename}.json")
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
    except Exception as e:
        logger.error(f"Failed to save local metadata for {filename}: {e}")

    return {
        "output_rows": output_rows,
        "annotated_images": annotated_images,
        "traces": [t.model_dump() for t in traces]
    }
