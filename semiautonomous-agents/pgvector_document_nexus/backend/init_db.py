"""Initialize the pgvector database schema."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

import asyncpg

async def init_database():
    """Create tables and indexes for pgvector document storage."""

    print("Connecting to Cloud SQL...")
    conn = await asyncpg.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )

    print("Connected! Initializing schema...")

    # Enable pgvector extension
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    print("  - pgvector extension enabled")

    # Create table
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
    print("  - document_chunks table created")

    # Create HNSW index
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    print("  - HNSW index created")

    # Verify
    result = await conn.fetchval(
        "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
    )
    print(f"\npgvector version: {result}")

    count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
    print(f"Current document chunks: {count}")

    await conn.close()
    print("\nDatabase initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_database())
