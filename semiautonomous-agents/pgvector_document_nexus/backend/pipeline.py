"""
Document processing pipeline with pgvector storage.
Extracts entities from PDFs, generates embeddings, and stores in Cloud SQL.
"""

import os
import io
import json
import uuid
import asyncio
import logging
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

import asyncpg
import fitz
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pydantic import BaseModel, Field

from google import genai
from google.genai import types
from google.genai.types import EmbedContentConfig
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.runners import Runner

logger = logging.getLogger(__name__)

# ========================================
# Singleton GenAI Client (avoids cold start on each request)
# ========================================
_genai_client = None

def get_genai_client():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
    return _genai_client

# ========================================
# Pydantic Schemas
# ========================================

class ExtractedEntity(BaseModel):
    page_number: int = Field(description="The page number in the original document.")
    entity_type: str = Field(description="'TEXT', 'TABLE', or 'CHART'")
    content_description: str = Field(description="The actual text content. For tables and charts, include full data in markdown.")
    structured_data: Optional[dict] = Field(default=None)
    box_2d: Optional[List[int]] = Field(default=None, description="Bounding box [ymin, xmin, ymax, xmax] normalized 0-1000")
    embedding: Optional[List[float]] = Field(default=None)

class DocumentPageResult(BaseModel):
    page_number: int
    entities: List[ExtractedEntity]

class ADKTrace(BaseModel):
    agent_name: str
    page_number: int
    start_time: str
    end_time: str
    duration_seconds: float
    entities_extracted: int

# ========================================
# Database Pool (pgvector)
# ========================================

_db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            database=os.environ.get("DB_NAME", "document_nexus"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", ""),
            min_size=2,
            max_size=10,
        )
        # Register vector type
        async with _db_pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    return _db_pool

async def init_db_schema():
    """Initialize database schema if not exists."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                chunk_id TEXT UNIQUE NOT NULL,
                document_name TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                entity_type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding vector(768),
                box_2d INTEGER[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create HNSW index if not exists
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
            ON document_chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """)

# ========================================
# PDF Utilities
# ========================================

def split_pdf_logically(pdf_bytes: bytes, max_pages_per_chunk: int = 1) -> List[Dict[str, Any]]:
    """Split PDF into single-page chunks."""
    chunks = []
    pdf_stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)

    for i in range(0, len(reader.pages), max_pages_per_chunk):
        writer = PdfWriter()
        end_idx = min(i + max_pages_per_chunk, len(reader.pages))
        for j in range(i, end_idx):
            writer.add_page(reader.pages[j])

        out_stream = io.BytesIO()
        writer.write(out_stream)
        chunks.append({
            "start_page": i + 1,
            "end_page": end_idx,
            "pdf_bytes": out_stream.getvalue(),
            "mime_type": "application/pdf"
        })
        out_stream.close()

    pdf_stream.close()
    return chunks

def pdf_page_to_image(pdf_bytes: bytes, page_num: int) -> bytes:
    """Convert PDF page to JPEG image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page_num >= len(doc):
        return b""
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return pix.tobytes("jpeg")

def draw_bounding_boxes(image_bytes: bytes, entities_with_boxes: List[Any], page_num: int) -> bytes:
    """Draw bounding boxes on page image."""
    if not image_bytes or not entities_with_boxes:
        return image_bytes

    visual_entities = []
    for idx, item in enumerate(entities_with_boxes):
        if isinstance(item, tuple):
            entity, global_idx = item
        else:
            entity, global_idx = item, idx
        if hasattr(entity, 'entity_type') and entity.entity_type.lower() in ['chart', 'image', 'table']:
            visual_entities.append((entity, global_idx))

    if not visual_entities:
        return image_bytes

    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = im.size
    draw = ImageDraw.Draw(im)

    COLORS = ["#00D9FF", "#FF6B9D", "#A855F7", "#10B981", "#F59E0B", "#EF4444"]

    try:
        label_font = ImageFont.truetype("Arial.ttf", size=max(20, int(min(width, height) / 35)))
    except OSError:
        label_font = ImageFont.load_default()

    for idx, (entity, global_idx) in enumerate(visual_entities):
        if not hasattr(entity, 'box_2d') or not entity.box_2d or len(entity.box_2d) != 4:
            continue

        bb = entity.box_2d
        y_min, x_min, y_max, x_max = [int(v / 1000 * (height if j % 2 == 0 else width)) for j, v in enumerate(bb)]
        color = COLORS[idx % len(COLORS)]

        draw.rectangle(((x_min, y_min), (x_max, y_max)), outline=color, width=3)
        tag_text = f" {global_idx} "
        try:
            tw, th = label_font.getbbox(tag_text)[2:]
        except:
            tw, th = 30, 30

        pill_rect = [x_min, max(0, y_min - th - 8), x_min + tw + 8, y_min]
        draw.rectangle(pill_rect, fill=color)
        draw.text((pill_rect[0] + 4, pill_rect[1] + 4), tag_text, fill="white", font=label_font)

    output = io.BytesIO()
    im.save(output, format="JPEG", quality=85)
    return output.getvalue()

# ========================================
# Embeddings
# ========================================

async def generate_embeddings(entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
    """Generate embeddings for entities using Vertex AI."""
    if not entities:
        return []

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    )

    contents = [e.content_description for e in entities]
    batch_size = 50
    all_embeddings = []

    for i in range(0, len(contents), batch_size):
        batch = contents[i:i + batch_size]
        try:
            response = await client.aio.models.embed_content(
                model="text-embedding-004",
                contents=batch,
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )
            if response.embeddings:
                all_embeddings.extend(response.embeddings)
        except Exception as e:
            logger.error(f"Embedding batch {i // batch_size} failed: {e}")
            all_embeddings.extend([None] * len(batch))

    for i, entity in enumerate(entities):
        if i < len(all_embeddings) and all_embeddings[i]:
            entity.embedding = all_embeddings[i].values
        else:
            entity.embedding = []

    return entities

# ========================================
# pgvector Operations
# ========================================

async def insert_chunks_to_pgvector(rows: List[Dict[str, Any]]):
    """Insert document chunks with embeddings into Cloud SQL pgvector."""
    if not rows:
        return

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for row in rows:
            embedding = row.get("embedding", [])
            if not embedding:
                continue

            embedding_str = f"[{','.join(map(str, embedding))}]"
            box_2d = row.get("box_2d")

            await conn.execute("""
                INSERT INTO document_chunks (chunk_id, document_name, page_number, entity_type, content, embedding, box_2d)
                VALUES ($1, $2, $3, $4, $5, $6::vector, $7)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    box_2d = EXCLUDED.box_2d
            """, row["chunk_id"], row["document_name"], row["page_number"],
                row["entity_type"], row["content"], embedding_str, box_2d)

    logger.info(f"Inserted {len(rows)} chunks into pgvector")

async def search_embeddings_pgvector(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using pgvector cosine similarity."""
    client = get_genai_client()

    try:
        response = await client.aio.models.embed_content(
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
        logger.error(f"Query embedding failed: {e}")
        return []

    embedding_str = f"[{','.join(map(str, query_vector))}]"

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT chunk_id, document_name, page_number, entity_type, content, box_2d,
                   1 - (embedding <=> $1::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """, embedding_str, top_k)

    return [
        {
            "chunk_id": row["chunk_id"],
            "document_name": row["document_name"],
            "page_number": row["page_number"],
            "entity_type": row["entity_type"],
            "content": row["content"],
            "box_2d": list(row["box_2d"]) if row["box_2d"] else None,
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]

async def get_indexed_documents() -> List[Dict[str, Any]]:
    """Get list of indexed documents with chunk counts."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT document_name, COUNT(*) as chunk_count
            FROM document_chunks
            GROUP BY document_name
            ORDER BY document_name
        """)
    return [{"document_name": r["document_name"], "chunk_count": r["chunk_count"]} for r in rows]

async def get_document_chunks(document_name: str) -> List[Dict[str, Any]]:
    """Get all chunks for a specific document."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT chunk_id, document_name, page_number, entity_type, content, box_2d
            FROM document_chunks
            WHERE document_name = $1
            ORDER BY page_number, chunk_id
        """, document_name)
    return [
        {
            "chunk_id": r["chunk_id"],
            "document_name": r["document_name"],
            "page_number": r["page_number"],
            "entity_type": r["entity_type"],
            "content": r["content"],
            "box_2d": list(r["box_2d"]) if r["box_2d"] else None,
        }
        for r in rows
    ]

async def delete_document(document_name: str) -> bool:
    """Delete a document and all its chunks."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM document_chunks WHERE document_name = $1",
            document_name
        )
    return "DELETE" in result

# ========================================
# ADK Extraction Agents
# ========================================

MODEL_EXTRACTOR = "gemini-2.5-flash"

def _create_page_extractor(page_chunk: dict, page_num: int) -> LlmAgent:
    """Create an ADK agent for extracting entities from a page."""

    def inject_image(callback_context: CallbackContext, llm_request: LlmRequest, **kwargs):
        try:
            image_part = types.Part.from_bytes(
                data=page_chunk["image_bytes"],
                mime_type="image/jpeg"
            )
            llm_request.contents[-1].parts.append(image_part)
        except Exception as e:
            logger.error(f"Image injection failed for page {page_num}: {e}")

    return LlmAgent(
        name=f"extractor_page_{page_num}",
        model=MODEL_EXTRACTOR,
        instruction=f"""
        Analyze the PAGE IMAGE provided.
        1. Identify logical sections: titles, paragraphs, lists, charts, diagrams, tables.
        2. For text: extract exact content into content_description.
        3. For tables/charts: describe and include FULL DATA IN MARKDOWN.
        4. Provide box_2d [ymin, xmin, ymax, xmax] (0-1000 normalized) for ALL elements.
        5. Return strictly as JSON matching the schema.
        """,
        output_schema=DocumentPageResult,
        before_model_callback=inject_image
    )

async def _process_single_page(page_agent, session_service, app_name: str, session_id: str, semaphore: asyncio.Semaphore) -> Tuple[List[DocumentPageResult], Optional[ADKTrace]]:
    """Run extraction for a single page."""
    async with semaphore:
        start_t = asyncio.get_event_loop().time()
        start_dt = datetime.now(timezone.utc).isoformat()

        await session_service.create_session(user_id="system", session_id=session_id, app_name=app_name, state={})

        temp_runner = Runner(agent=page_agent, session_service=session_service, app_name=app_name)
        content = types.Content(role="user", parts=[types.Part.from_text(text="Extract entities from this page.")])

        try:
            async for event in temp_runner.run_async(user_id="system", session_id=session_id, new_message=content):
                if event.is_final_response() and event.content and event.content.parts:
                    resp_text = event.content.parts[0].text
                    try:
                        parsed = json.loads(resp_text)
                        page_num = parsed.get("page_number", 1) if isinstance(parsed, dict) else 1
                        entities_data = parsed.get("entities", [parsed]) if isinstance(parsed, dict) else parsed

                        processed = []
                        for item in entities_data:
                            item.setdefault("structured_data", None)
                            item.setdefault("embedding", None)
                            processed.append(item)

                        end_t = asyncio.get_event_loop().time()
                        trace = ADKTrace(
                            agent_name=page_agent.name,
                            page_number=page_num,
                            start_time=start_dt,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            duration_seconds=round(end_t - start_t, 2),
                            entities_extracted=len(processed)
                        )
                        return [DocumentPageResult(page_number=page_num, entities=processed)], trace
                    except Exception as e:
                        logger.error(f"JSON parse failed: {e}")
        except Exception as e:
            logger.error(f"Page extraction failed: {e}")

        return [], None

async def run_parallel_extraction(pdf_bytes: bytes, session_service, app_name: str, session_id: str) -> Tuple[List[DocumentPageResult], List[ADKTrace]]:
    """Extract entities from all pages in parallel."""
    chunks = split_pdf_logically(pdf_bytes)
    if not chunks:
        return [], []

    semaphore = asyncio.Semaphore(5)
    tasks = []

    for chunk in chunks:
        page_num = chunk["start_page"]
        try:
            chunk["image_bytes"] = pdf_page_to_image(chunk["pdf_bytes"], 0)
        except Exception as e:
            logger.error(f"Page {page_num} rasterization failed: {e}")
            continue

        agent = _create_page_extractor(chunk, page_num)
        sub_session_id = f"{session_id}_page_{page_num}"
        tasks.append(_process_single_page(agent, session_service, app_name, sub_session_id, semaphore))

    results = await asyncio.gather(*tasks)

    final_results = []
    traces = []
    for page_results, trace in results:
        final_results.extend(page_results)
        if trace:
            traces.append(trace)

    return final_results, traces

# ========================================
# Main Pipeline
# ========================================

async def process_document_pipeline(file_bytes: bytes, filename: str, session_service) -> dict:
    """Main document processing pipeline."""
    app_name = "pgvector_pipeline"
    session_id = str(uuid.uuid4())

    await session_service.create_session(app_name=app_name, user_id="system", session_id=session_id, state={})

    # 1. Parallel extraction
    logger.info(f"Extracting from {filename}...")
    extracted_pages, traces = await run_parallel_extraction(file_bytes, session_service, app_name, session_id)

    all_entities = []
    for page in extracted_pages:
        all_entities.extend(page.entities)

    if not all_entities:
        logger.warning("No entities extracted")
        return {"output_rows": [], "annotated_images": [], "traces": []}

    # 2. Generate embeddings
    logger.info(f"Generating embeddings for {len(all_entities)} entities...")
    embedded_entities = await generate_embeddings(all_entities)

    # 3. Format output rows
    output_rows = []
    for i, entity in enumerate(embedded_entities):
        chunk_id = f"chunk_{filename}_{entity.page_number}_{i}"
        output_rows.append({
            "chunk_id": chunk_id,
            "document_name": filename,
            "page_number": entity.page_number,
            "entity_type": entity.entity_type,
            "content": entity.content_description,
            "embedding": entity.embedding,
            "box_2d": entity.box_2d,
        })

    # 4. Draw annotated images
    annotated_images = []
    pages_to_draw = {}
    for i, entity in enumerate(embedded_entities):
        if entity.page_number not in pages_to_draw:
            pages_to_draw[entity.page_number] = []
        pages_to_draw[entity.page_number].append((entity, i))

    for page_num, entities in pages_to_draw.items():
        try:
            raw_img = pdf_page_to_image(file_bytes, page_num - 1)
            annotated = draw_bounding_boxes(raw_img, entities, page_num)
            if annotated:
                b64 = base64.b64encode(annotated).decode('utf-8')
                annotated_images.append(f"data:image/jpeg;base64,{b64}")
        except Exception as e:
            logger.error(f"Annotation failed for page {page_num}: {e}")

    # 5. Save local metadata
    local_dir = os.path.join(os.path.dirname(__file__), "local_data")
    os.makedirs(local_dir, exist_ok=True)
    metadata = {
        "annotated_images": annotated_images,
        "traces": [t.model_dump() for t in traces],
        "boxes": {f"chunk_{filename}_{e.page_number}_{i}": e.box_2d for i, e in enumerate(embedded_entities) if e.box_2d}
    }
    with open(os.path.join(local_dir, f"{filename}.json"), "w") as f:
        json.dump(metadata, f)

    return {
        "output_rows": output_rows,
        "annotated_images": annotated_images,
        "traces": [t.model_dump() for t in traces]
    }
