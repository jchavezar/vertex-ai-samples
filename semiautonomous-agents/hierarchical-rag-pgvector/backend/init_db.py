"""
Database initialization for Hierarchical RAG with Parent-Child chunking.

Schema Design:
- parent_segments: Large context blocks (500-2000 tokens), owns children
- child_chunks: Small precise chunks (100-300 tokens) with embeddings for retrieval
- segment_relationships: Lateral peer relationships between agents/segments
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hierarchical_rag")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


SCHEMA_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Parent segments table: large context blocks
CREATE TABLE IF NOT EXISTS parent_segments (
    id SERIAL PRIMARY KEY,
    parent_id TEXT UNIQUE NOT NULL,           -- e.g., "doc_architecture_p1"
    document_name TEXT NOT NULL,               -- Source document name
    page_number INTEGER NOT NULL,              -- Page where segment starts
    heading TEXT,                              -- Section heading if available
    agent_name TEXT,                           -- Logical agent/component name
    content TEXT NOT NULL,                     -- Full parent text (500-2000 tokens)
    parent_agent TEXT,                         -- Hierarchical parent agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Child chunks table: small chunks with embeddings for precision retrieval
CREATE TABLE IF NOT EXISTS child_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,            -- e.g., "doc_architecture_p1_c0"
    parent_id TEXT NOT NULL REFERENCES parent_segments(parent_id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,              -- Position within parent (0, 1, 2...)
    content TEXT NOT NULL,                     -- Child chunk text (100-300 tokens)
    embedding vector(768),                     -- 768-dim embedding for retrieval
    box_2d INTEGER[],                          -- Bounding box [ymin, xmin, ymax, xmax]
    entity_type TEXT DEFAULT 'TEXT',           -- TEXT, TABLE, CHART
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Segment relationships: lateral peer relationships between agents/components
CREATE TABLE IF NOT EXISTS segment_relationships (
    id SERIAL PRIMARY KEY,
    source_agent TEXT NOT NULL,               -- e.g., "billing_agent"
    target_agent TEXT NOT NULL,               -- e.g., "auth_agent"
    relationship_type TEXT DEFAULT 'related', -- related, depends_on, feeds_into
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_agent, target_agent, relationship_type)
);

-- Simple chunks table: flat RAG structure for comparison (no parent-child hierarchy)
CREATE TABLE IF NOT EXISTS simple_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,            -- e.g., "simple_doc_p1_c0"
    document_name TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,                     -- Same size as child chunks (~200 tokens)
    embedding vector(768),                     -- Same embedding model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HNSW index for fast vector search on child chunks
CREATE INDEX IF NOT EXISTS child_chunks_embedding_idx
ON child_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index for parent lookup
CREATE INDEX IF NOT EXISTS child_chunks_parent_idx ON child_chunks(parent_id);

-- Index for agent relationship expansion
CREATE INDEX IF NOT EXISTS parent_segments_agent_idx ON parent_segments(agent_name);
CREATE INDEX IF NOT EXISTS segment_relationships_source_idx ON segment_relationships(source_agent);

-- HNSW index for simple chunks (for comparison with hierarchical approach)
CREATE INDEX IF NOT EXISTS simple_chunks_embedding_idx
ON simple_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
"""


async def init_database():
    """Initialize database with parent-child schema."""
    # First connect to postgres to create database if needed
    try:
        conn = await asyncpg.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )

        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME
        )

        if not exists:
            await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Created database: {DB_NAME}")

        await conn.close()
    except Exception as e:
        print(f"Note: {e}")

    # Connect to our database and create schema
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    # Execute schema
    await conn.execute(SCHEMA_SQL)
    print("Schema initialized successfully!")

    # Verify tables
    tables = await conn.fetch("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    print(f"Tables: {[t['table_name'] for t in tables]}")

    await conn.close()


async def reset_database():
    """Drop and recreate all tables (for testing)."""
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    await conn.execute("""
        DROP TABLE IF EXISTS segment_relationships CASCADE;
        DROP TABLE IF EXISTS child_chunks CASCADE;
        DROP TABLE IF EXISTS parent_segments CASCADE;
    """)
    print("Tables dropped.")

    await conn.execute(SCHEMA_SQL)
    print("Schema recreated.")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())
