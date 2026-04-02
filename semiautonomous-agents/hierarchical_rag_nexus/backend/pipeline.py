"""
Parent-Child RAG Pipeline with Cloud SQL pgvector.

Implements Strategy 2 (Structure-Aware) + Strategy 4 (Agent-Native) from the research:
- Parent segments: Large context blocks with heading/agent metadata
- Child chunks: Small precise chunks for embedding search
- Relationship expansion: Pull related peer agents at retrieval time
"""

import asyncio
import asyncpg
import base64
import io
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import fitz  # PyMuPDF
import vertexai
from dotenv import load_dotenv
from google import genai
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import EmbedContentConfig, Part
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

load_dotenv(dotenv_path="../.env")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hierarchical_rag")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Initialize Vertex AI
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# GenAI client for embeddings
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Database connection pool
_db_pool: Optional[asyncpg.Pool] = None


# ============================================================================
# Pydantic Models
# ============================================================================


class ExtractedSection(BaseModel):
    """A logical section extracted from a document page."""
    heading: Optional[str] = None
    agent_name: Optional[str] = None  # Logical component/agent this belongs to
    content: str
    entity_type: str = "TEXT"  # TEXT, TABLE, CHART
    box_2d: list[int] = []  # [ymin, xmin, ymax, xmax] normalized 0-1000
    related_agents: list[str] = []  # Other agents this section references


class DocumentPageResult(BaseModel):
    """Extraction result for a single page."""
    page_number: int
    sections: list[ExtractedSection]


class ParentSegment(BaseModel):
    """A parent segment with full context."""
    parent_id: str
    document_name: str
    page_number: int
    heading: Optional[str]
    agent_name: Optional[str]
    content: str
    parent_agent: Optional[str]
    children: list["ChildChunk"] = []


class ChildChunk(BaseModel):
    """A child chunk for embedding and retrieval."""
    chunk_id: str
    parent_id: str
    document_name: str
    page_number: int
    chunk_index: int
    content: str
    embedding: list[float] = []
    entity_type: str = "TEXT"
    box_2d: list[int] = []


class ADKTrace(BaseModel):
    """Trace info for frontend display."""
    agent_name: str
    page_number: int
    start_time: str
    end_time: str
    duration_seconds: float
    sections_extracted: int


class RetrievalResult(BaseModel):
    """Result from parent-child retrieval."""
    parent_id: str
    parent_content: str
    agent_name: Optional[str]
    heading: Optional[str]
    matched_child: str
    matched_child_id: str
    similarity_score: float
    page_number: int
    document_name: str
    related_agents: list[str] = []
    expanded_context: list[dict] = []


# ============================================================================
# Database Operations
# ============================================================================


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool."""
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=2,
            max_size=10,
        )
        # Ensure pgvector extension
        async with _db_pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    return _db_pool


async def insert_parent_segment(segment: ParentSegment) -> None:
    """Insert a parent segment into the database."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO parent_segments (parent_id, document_name, page_number, heading, agent_name, content, parent_agent)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (parent_id) DO UPDATE SET
                content = EXCLUDED.content,
                heading = EXCLUDED.heading,
                agent_name = EXCLUDED.agent_name
            """,
            segment.parent_id,
            segment.document_name,
            segment.page_number,
            segment.heading,
            segment.agent_name,
            segment.content,
            segment.parent_agent,
        )


async def insert_child_chunks(chunks: list[ChildChunk]) -> None:
    """Bulk insert child chunks with embeddings."""
    if not chunks:
        return

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Prepare data for bulk insert
        records = []
        for chunk in chunks:
            embedding_str = f"[{','.join(str(v) for v in chunk.embedding)}]" if chunk.embedding else None
            records.append((
                chunk.chunk_id,
                chunk.parent_id,
                chunk.document_name,
                chunk.page_number,
                chunk.chunk_index,
                chunk.content,
                embedding_str,
                chunk.box_2d if chunk.box_2d else None,
                chunk.entity_type,
            ))

        await conn.executemany(
            """
            INSERT INTO child_chunks (chunk_id, parent_id, document_name, page_number, chunk_index, content, embedding, box_2d, entity_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7::vector, $8, $9)
            ON CONFLICT (chunk_id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            """,
            records,
        )


async def insert_agent_relationships(relationships: list[tuple[str, str, str]]) -> None:
    """Insert agent peer relationships."""
    if not relationships:
        return

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO segment_relationships (source_agent, target_agent, relationship_type)
            VALUES ($1, $2, $3)
            ON CONFLICT (source_agent, target_agent, relationship_type) DO NOTHING
            """,
            relationships,
        )


# ============================================================================
# Simple RAG (for comparison with hierarchical approach)
# ============================================================================


async def insert_simple_chunks(chunks: list[ChildChunk], document_name: str) -> None:
    """Insert simple flat chunks (same content as children, no hierarchy)."""
    if not chunks:
        return

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        records = []
        for chunk in chunks:
            # Use 'simple_' prefix to differentiate from hierarchical chunks
            simple_id = f"simple_{chunk.chunk_id}"
            embedding_str = f"[{','.join(str(v) for v in chunk.embedding)}]" if chunk.embedding else None
            records.append((
                simple_id,
                document_name,
                chunk.page_number,
                chunk.content,
                embedding_str,
            ))

        await conn.executemany(
            """
            INSERT INTO simple_chunks (chunk_id, document_name, page_number, content, embedding)
            VALUES ($1, $2, $3, $4, $5::vector)
            ON CONFLICT (chunk_id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            """,
            records,
        )


@dataclass
class SimpleRetrievalResult:
    """Result from simple RAG (no parent context)."""
    chunk_id: str
    content: str
    document_name: str
    page_number: int
    similarity_score: float


async def search_simple_chunks(
    query_embedding: list[float],
    top_k: int = 5,
) -> list[SimpleRetrievalResult]:
    """
    Simple RAG retrieval - just vector search on flat chunks.
    No parent context, no expansion. Returns exactly what was matched.
    """
    pool = await get_db_pool()
    embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                chunk_id,
                content,
                document_name,
                page_number,
                1 - (embedding <=> $1::vector) AS similarity
            FROM simple_chunks
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            embedding_str,
            top_k,
        )

        return [
            SimpleRetrievalResult(
                chunk_id=row["chunk_id"],
                content=row["content"],
                document_name=row["document_name"],
                page_number=row["page_number"],
                similarity_score=float(row["similarity"]),
            )
            for row in rows
        ]


async def search_children_get_parents(
    query_embedding: list[float],
    top_k: int = 5,
    expand_related: bool = True,
) -> list[RetrievalResult]:
    """
    Core parent-child retrieval:
    1. Vector search on child chunks
    2. Resolve child -> parent
    3. Expand via related agent relationships
    """
    pool = await get_db_pool()
    embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"

    async with pool.acquire() as conn:
        # Step 1 & 2: Search children, join to parents
        rows = await conn.fetch(
            """
            SELECT
                c.chunk_id,
                c.parent_id,
                c.content AS child_content,
                c.page_number,
                c.document_name,
                1 - (c.embedding <=> $1::vector) AS similarity,
                p.content AS parent_content,
                p.heading,
                p.agent_name,
                p.parent_agent
            FROM child_chunks c
            JOIN parent_segments p ON c.parent_id = p.parent_id
            ORDER BY c.embedding <=> $1::vector
            LIMIT $2
            """,
            embedding_str,
            top_k,
        )

        results = []
        seen_parents = set()
        agents_to_expand = set()

        for row in rows:
            parent_id = row["parent_id"]
            agent_name = row["agent_name"]

            # Deduplicate parents
            if parent_id in seen_parents:
                continue
            seen_parents.add(parent_id)

            if agent_name:
                agents_to_expand.add(agent_name)

            results.append(
                RetrievalResult(
                    parent_id=parent_id,
                    parent_content=row["parent_content"],
                    agent_name=agent_name,
                    heading=row["heading"],
                    matched_child=row["child_content"],
                    matched_child_id=row["chunk_id"],
                    similarity_score=float(row["similarity"]),
                    page_number=row["page_number"],
                    document_name=row["document_name"],
                )
            )

        # Step 3: Expand related agents (query-relevant expansion)
        if expand_related and agents_to_expand:
            related = await conn.fetch(
                """
                SELECT DISTINCT target_agent
                FROM segment_relationships
                WHERE source_agent = ANY($1::text[])
                """,
                list(agents_to_expand),
            )

            related_agents = [r["target_agent"] for r in related]

            # Filter out agents we already have in results
            existing_agents = {r.agent_name for r in results if r.agent_name}
            related_agents = [a for a in related_agents if a not in existing_agents]

            if related_agents:
                # For each related agent, find the segment MOST SIMILAR to the query
                # Using vector search on child chunks, then getting their parents
                expanded = await conn.fetch(
                    """
                    WITH ranked_children AS (
                        SELECT
                            c.parent_id,
                            p.content,
                            p.heading,
                            p.agent_name,
                            p.page_number,
                            p.document_name,
                            1 - (c.embedding <=> $1::vector) AS similarity,
                            ROW_NUMBER() OVER (PARTITION BY p.agent_name ORDER BY c.embedding <=> $1::vector) as rn
                        FROM child_chunks c
                        JOIN parent_segments p ON c.parent_id = p.parent_id
                        WHERE p.agent_name = ANY($2::text[])
                    )
                    SELECT parent_id, content, heading, agent_name, page_number, document_name, similarity
                    FROM ranked_children
                    WHERE rn = 1
                    ORDER BY similarity DESC
                    LIMIT 3
                    """,
                    embedding_str,
                    related_agents,
                )

                for exp in expanded:
                    # Add as expanded context to first result
                    if results:
                        results[0].expanded_context.append({
                            "parent_id": exp["parent_id"],
                            "content": exp["content"],
                            "heading": exp["heading"],
                            "agent_name": exp["agent_name"],
                            "similarity": float(exp["similarity"]),
                        })
                        results[0].related_agents.append(exp["agent_name"])

        return results


async def get_all_documents() -> list[dict]:
    """Get all indexed documents with chunk counts."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                document_name,
                COUNT(DISTINCT parent_id) as parent_count,
                COUNT(*) as child_count
            FROM child_chunks
            GROUP BY document_name
            ORDER BY document_name
            """
        )
        return [dict(r) for r in rows]


async def get_document_data(document_name: str) -> dict:
    """Get all data for a specific document."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        parents = await conn.fetch(
            """
            SELECT parent_id, document_name, page_number, heading, agent_name, content, parent_agent
            FROM parent_segments
            WHERE document_name = $1
            ORDER BY page_number
            """,
            document_name,
        )

        children = await conn.fetch(
            """
            SELECT chunk_id, parent_id, document_name, page_number, chunk_index, content, entity_type, box_2d
            FROM child_chunks
            WHERE document_name = $1
            ORDER BY page_number, chunk_index
            """,
            document_name,
        )

        # Get relationships for agents in this document
        agent_names = list(set(p["agent_name"] for p in parents if p["agent_name"]))
        relationships = []
        if agent_names:
            rels = await conn.fetch(
                """
                SELECT source_agent, target_agent, relationship_type
                FROM segment_relationships
                WHERE source_agent = ANY($1::text[]) OR target_agent = ANY($1::text[])
                """,
                agent_names,
            )
            relationships = [(r["source_agent"], r["target_agent"], r["relationship_type"]) for r in rels]

        return {
            "parents": [dict(p) for p in parents],
            "children": [dict(c) for c in children],
            "relationships": relationships,
        }


async def get_all_relationships() -> list:
    """Get all agent relationships for graph visualization."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rels = await conn.fetch(
            """
            SELECT source_agent, target_agent, relationship_type
            FROM segment_relationships
            """
        )
        return [(r["source_agent"], r["target_agent"], r["relationship_type"]) for r in rels]


async def get_all_agents_with_docs() -> list:
    """Get all agents and which documents they appear in."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT agent_name, document_name
            FROM parent_segments
            WHERE agent_name IS NOT NULL
            ORDER BY agent_name
            """
        )
        return [dict(r) for r in rows]


async def delete_document(document_name: str) -> int:
    """Delete a document and all its segments/chunks."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Delete children first (FK constraint)
        await conn.execute(
            "DELETE FROM child_chunks WHERE document_name = $1", document_name
        )
        result = await conn.execute(
            "DELETE FROM parent_segments WHERE document_name = $1", document_name
        )
        # Extract row count from result
        return int(result.split()[-1])


# ============================================================================
# PDF Processing
# ============================================================================


def pdf_page_to_image(pdf_bytes: bytes, page_num: int) -> bytes:
    """Convert a PDF page to JPEG image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for quality
    img_data = pix.tobytes("jpeg")
    doc.close()
    return img_data


def split_text_into_children(
    text: str, parent_id: str, document_name: str, page_number: int, max_tokens: int = 200
) -> list[ChildChunk]:
    """Split parent text into smaller child chunks (~200 tokens each)."""
    # Rough approximation: 1 token ~ 4 characters
    max_chars = max_tokens * 4
    sentences = re.split(r'(?<=[.!?])\s+', text)

    children = []
    current_chunk = ""
    chunk_index = 0

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chars and current_chunk:
            children.append(
                ChildChunk(
                    chunk_id=f"{parent_id}_c{chunk_index}",
                    parent_id=parent_id,
                    document_name=document_name,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    content=current_chunk.strip(),
                )
            )
            chunk_index += 1
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    # Don't forget the last chunk
    if current_chunk.strip():
        children.append(
            ChildChunk(
                chunk_id=f"{parent_id}_c{chunk_index}",
                parent_id=parent_id,
                document_name=document_name,
                page_number=page_number,
                chunk_index=chunk_index,
                content=current_chunk.strip(),
            )
        )

    return children


# ============================================================================
# ADK Extraction
# ============================================================================


def create_page_extractor(page_image: bytes, page_num: int) -> LlmAgent:
    """Create an ADK agent for extracting structured sections from a page."""

    def inject_image(callback_context: CallbackContext, llm_request: LlmRequest, **kwargs):
        """Inject page image into the LLM request."""
        try:
            image_part = types.Part.from_bytes(data=page_image, mime_type="image/jpeg")
            llm_request.contents[-1].parts.append(image_part)
        except Exception as e:
            print(f"Image injection failed for page {page_num}: {e}")

    instruction = """You are an expert document analyst specializing in extracting structured information.

Analyze this document page and extract ALL logical sections. For each section identify:

1. **heading**: The section title/header if visible (null if none)
2. **agent_name**: A logical component/agent name this section belongs to. Use consistent naming like:
   - "orchestrator" for main/overview sections
   - "auth_agent" for authentication-related content
   - "billing_agent" for billing/payment content
   - "data_pipeline" for data processing content
   - "monitoring_agent" for logging/monitoring content
   - Use descriptive names based on the content domain
3. **content**: The FULL text content of this section (preserve all details)
4. **entity_type**: TEXT, TABLE, or CHART
5. **box_2d**: Bounding box [ymin, xmin, ymax, xmax] normalized to 0-1000 scale
6. **related_agents**: List of other agent names this section references or depends on

Be thorough - extract every distinct section. For tables, include the FULL table data in markdown format.
If a section references other components/systems, list them in related_agents.

Return valid JSON matching the DocumentPageResult schema exactly."""

    return LlmAgent(
        name=f"extractor_page_{page_num}",
        model="gemini-2.5-flash",
        instruction=instruction,
        output_schema=DocumentPageResult,
        before_model_callback=inject_image,
    )


async def extract_page(
    page_image: bytes,
    page_num: int,
    session_service: InMemorySessionService,
    app_name: str,
    semaphore: asyncio.Semaphore,
) -> tuple[DocumentPageResult, ADKTrace]:
    """Extract sections from a single page using ADK."""
    async with semaphore:
        agent = create_page_extractor(page_image, page_num)
        runner = Runner(
            agent=agent,
            session_service=session_service,
            app_name=app_name,
        )

        session_id = f"extract_page_{page_num}_{datetime.now().timestamp()}"
        session = await session_service.create_session(
            app_name=app_name, user_id="system", session_id=session_id
        )

        start_time = datetime.now()

        result = None
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text="Extract all sections from this page.")]
        )
        async for event in runner.run_async(
            user_id="system", session_id=session_id, new_message=content
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        try:
                            data = json.loads(part.text)
                            result = DocumentPageResult(**data)
                        except (json.JSONDecodeError, ValueError):
                            pass

        end_time = datetime.now()

        if result is None:
            result = DocumentPageResult(page_number=page_num, sections=[])

        trace = ADKTrace(
            agent_name=f"extractor_page_{page_num}",
            page_number=page_num,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=(end_time - start_time).total_seconds(),
            sections_extracted=len(result.sections),
        )

        return result, trace


async def process_document(
    pdf_bytes: bytes, filename: str
) -> tuple[list[ParentSegment], list[ChildChunk], list[ADKTrace], list[tuple[str, str, str]]]:
    """
    Process a PDF document with parent-child chunking.

    Returns:
        - parents: List of parent segments
        - children: List of child chunks (without embeddings yet)
        - traces: ADK execution traces
        - relationships: Agent relationship tuples
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = len(doc)
    doc.close()

    session_service = InMemorySessionService()
    app_name = "hierarchical_extractor"
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent extractions

    # Extract all pages in parallel
    tasks = []
    for page_num in range(num_pages):
        page_image = pdf_page_to_image(pdf_bytes, page_num)
        tasks.append(
            extract_page(page_image, page_num + 1, session_service, app_name, semaphore)
        )

    results = await asyncio.gather(*tasks)

    # Process results into parent-child structure
    parents = []
    children = []
    relationships = []
    doc_prefix = filename.replace(".pdf", "").replace(" ", "_").lower()

    for page_result, trace in results:
        for idx, section in enumerate(page_result.sections):
            parent_id = f"{doc_prefix}_p{page_result.page_number}_s{idx}"

            # Create parent segment
            parent = ParentSegment(
                parent_id=parent_id,
                document_name=filename,
                page_number=page_result.page_number,
                heading=section.heading,
                agent_name=section.agent_name,
                content=section.content,
                parent_agent=None,  # Could be inferred from hierarchy
            )
            parents.append(parent)

            # Split into children
            section_children = split_text_into_children(
                section.content,
                parent_id,
                filename,
                page_result.page_number,
            )

            # Transfer metadata to children
            for child in section_children:
                child.entity_type = section.entity_type
                child.box_2d = section.box_2d

            children.extend(section_children)

            # Extract relationships
            if section.agent_name and section.related_agents:
                for related in section.related_agents:
                    relationships.append((section.agent_name, related, "related"))

    traces = [trace for _, trace in results]
    return parents, children, traces, relationships


# ============================================================================
# Embedding Generation
# ============================================================================


async def generate_embeddings(chunks: list[ChildChunk], batch_size: int = 50) -> list[ChildChunk]:
    """Generate embeddings for child chunks using text-embedding-004."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.content for c in batch]

        try:
            response = await genai_client.aio.models.embed_content(
                model="text-embedding-004",
                contents=texts,
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )

            for j, embedding in enumerate(response.embeddings):
                batch[j].embedding = list(embedding.values)

        except Exception as e:
            print(f"Embedding error for batch {i}: {e}")

    return chunks


async def embed_query(query: str) -> list[float]:
    """Generate embedding for a search query."""
    response = await genai_client.aio.models.embed_content(
        model="text-embedding-004",
        contents=[query],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        ),
    )
    return list(response.embeddings[0].values)


# ============================================================================
# Visualization
# ============================================================================


def draw_bounding_boxes(pdf_bytes: bytes, children: list[ChildChunk]) -> list[str]:
    """Draw bounding boxes on PDF pages and return as base64 images."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    annotated_images = []

    COLORS = [
        (0, 229, 255),    # Cyan
        (255, 61, 0),     # Red
        (0, 230, 118),    # Green
        (255, 234, 0),    # Yellow
        (213, 0, 249),    # Purple
        (255, 145, 0),    # Orange
    ]

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        draw = ImageDraw.Draw(img)

        # Get children for this page
        page_children = [c for c in children if c.page_number == page_num + 1 and c.box_2d]

        for idx, child in enumerate(page_children):
            if len(child.box_2d) == 4:
                ymin, xmin, ymax, xmax = child.box_2d
                # Scale from 0-1000 to actual pixels
                x1 = int(xmin * pix.width / 1000)
                y1 = int(ymin * pix.height / 1000)
                x2 = int(xmax * pix.width / 1000)
                y2 = int(ymax * pix.height / 1000)

                color = COLORS[idx % len(COLORS)]
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

                # Draw index number
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                except:
                    font = ImageFont.load_default()
                draw.text((x1 + 5, y1 + 5), str(idx + 1), fill=color, font=font)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        b64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        annotated_images.append(f"data:image/jpeg;base64,{b64_img}")

    doc.close()
    return annotated_images


# ============================================================================
# Main Pipeline
# ============================================================================


async def run_full_pipeline(
    pdf_bytes: bytes, filename: str
) -> dict:
    """
    Run the complete parent-child RAG pipeline:
    1. Extract sections via ADK
    2. Split into parent-child structure
    3. Generate embeddings for children
    4. Store in Cloud SQL
    5. Return visualization data
    """
    print(f"[Pipeline] Starting for {filename}")

    # Step 1-2: Extract and structure
    parents, children, traces, relationships = await process_document(pdf_bytes, filename)
    print(f"[Pipeline] Extracted {len(parents)} parents, {len(children)} children")

    # Step 3: Generate embeddings
    children = await generate_embeddings(children)
    print(f"[Pipeline] Generated embeddings")

    # Step 4: Store in database (both hierarchical and simple)
    for parent in parents:
        await insert_parent_segment(parent)
    await insert_child_chunks(children)
    await insert_agent_relationships(relationships)
    # Also store as simple chunks for comparison
    await insert_simple_chunks(children, filename)
    print(f"[Pipeline] Stored in database (hierarchical + simple)")

    # Step 5: Generate visualizations
    annotated_images = draw_bounding_boxes(pdf_bytes, children)

    return {
        "parents": [p.model_dump() for p in parents],
        "children": [
            {
                "chunk_id": c.chunk_id,
                "parent_id": c.parent_id,
                "content": c.content,
                "page_number": c.page_number,
                "entity_type": c.entity_type,
            }
            for c in children
        ],
        "traces": [t.model_dump() for t in traces],
        "annotated_images": annotated_images,
        "relationships": relationships,
    }
