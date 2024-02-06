#region Create Vector Database
import json
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
#%%

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)

    #region create table
    async def create_table(self, table_name: str):
            loop = asyncio.get_running_loop()
            async with Connector(loop=loop) as connector:
                # Create connection to Cloud SQL database.
                conn: asyncpg.Connection = await connector.connect_async(
                    f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                    "asyncpg",
                    user=f"{self.database_user}",
                    password=f"{self.database_password}",
                    db=f"{self.database_name}",
                )
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Create the `embeddings` table.
            await conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name}(
                                    intent VARCHAR(1000),
                                    patient VARCHAR(1000),
                                    provider VARCHAR(1000),
                                    embedding vector(768))"""
            )
            print("Create Table Done...")
            await conn.close()
    #endregion

    #%%
    #region insert items into the table
    async def insert_items(self, documents: list, table_name: str):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector(conn)
        # Store all the generated embeddings back into the database.
        for doc in documents:
            print(len(doc["intent"]))
            print(len(doc["provider"]))
            print(doc["provider"])
            await conn.execute(
                f"INSERT INTO {table_name} (intent, patient, provider, embedding) VALUES ($1, $2, $3, $4)",
                doc["intent"],
                doc["patient"],
                doc["provider"],
                doc["embeddings"],   
                )
            print("Insert Items Done...")
        await conn.close()
    #endregion

    #%%
    #region query items for testing
    async def test_query(self, table_name : str):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )

        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(f"""SELECT * FROM {table_name}""",)
        for r in results:
            print(r)
        await conn.close()
        return results
    #endregion

    #%%
    
    
    #region query matching engine
    async def query(self, emb_prompt, table_name: str):
        matches=[]
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )
        await register_vector(conn)
        similarity_threshold = 0.001
        num_matches = 10
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            f"""
                            WITH vector_matches AS (
                              SELECT intent, provider, patient, embedding, 1 - (embedding <=> $1) AS similarity
                              FROM {table_name}
                              WHERE 1 - (embedding <=> $1) > $2
                              ORDER BY similarity DESC
                              LIMIT $3
                            )
                            SELECT * FROM vector_matches
                            """,
            emb_prompt,
            similarity_threshold,
            num_matches,
        )
        if len(results) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")
        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(
                {
                    "intent": r["intent"],
                    "provider": r["provider"],
                    "patient": r["patient"],
                    "similarity": r["similarity"]
                }
            )
            print(matches)
        await conn.close()
        return matches
    #endregion
    
    #region delete table
    async def delete(self, table_name: str):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )

            await register_vector(conn)
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute(f"DROP TABLE IF EXISTS {table_name}")

            await conn.close()
