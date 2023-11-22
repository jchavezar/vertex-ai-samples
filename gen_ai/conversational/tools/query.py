import asyncio
import asyncpg
from typing import Dict
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector

async def query():
    matches=[]
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            "vtxdemos:us-central1:rag-pgvector-conversational-rag-1",  # Cloud SQL instance connection name
            "asyncpg",
            user="emb-admin",
            password="`)0/Lu1hJpQIrUb)",
            db="rag-pgvector-conversational-rag-1",
        )
    await register_vector(conn)

    # Find similar products to the query using cosine similarity search
    # over all vector embeddings. This new feature is provided by `pgvector`.
    results = await conn.fetch(
        """SELECT * FROM text_embeddings
        """,
    )
    if len(results) == 0:
        raise Exception("Did not find any results. Adjust the query parameters.")
    for r in results:
        # Collect the description for all the matched similar toy products.
        matches.append(
            {
                "date": r["date"],
                "human": r["human"],
                "asbot": r["asbot"],
                "similarity": r["similarity"]
            }
            )
    await conn.close()
    return matches