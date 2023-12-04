#%%
#region Import Libraries
import asyncio
import asyncpg
from typing import Dict
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        aiplatform.init(project="vtxdemos")
        self.model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        self.model_text = TextGenerationModel.from_pretrained("text-bison-32k")
    

    #region create table
    async def create_table(self):
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
            # Create the `text_embeddings` table.
            await conn.execute("DROP TABLE IF EXISTS text_embeddings CASCADE")
            await conn.execute(
                """CREATE TABLE text_embeddings(
                                    date DATE,
                                    human VARCHAR(1000000),
                                    asbot VARCHAR(1000000),
                                    embedding vector(768))"""
            )
            print("Create Table Done...")
            await conn.close()
    #endregion

    #region insert values
    async def insert_items_vdb(self, chat_history: str):
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
            
            for chat in chat_history:
                await conn.execute(
                    "INSERT INTO text_embeddings (date, human, asbot, embedding) VALUES ($1, $2, $3, $4)",
                    chat["date"],
                    chat["user"],
                    chat["asbot"],
                    self.model_emb.get_embeddings([f'query conversation time: {chat["date"]}, human query: {chat["user"]}, answer from asbot assistant: {chat["asbot"]}'])[0].values
                    )
            print("Insert Items Done...")
            await conn.close()
    #endregion
    
    async def query(self, query):
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
        emb_query = self.model_emb.get_embeddings([query])[0].values
        await register_vector(conn)
        similarity_threshold = 0.001
        num_matches = 2
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            """
                            WITH vector_matches AS (
                              SELECT date, human, asbot, embedding, 1 - (embedding <=> $1) AS similarity
                              FROM text_embeddings
                              WHERE 1 - (embedding <=> $1) > $2
                              ORDER BY similarity DESC
                              LIMIT $3
                            )
                            SELECT * FROM vector_matches
                            """,
            emb_query,
            similarity_threshold,
            num_matches,
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
    
    async def rag_query(self, query, database_name):
        matches=[]
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{database_name}",
            )
        emb_query = self.model_emb.get_embeddings([query])[0].values
        await register_vector(conn)
        similarity_threshold = 0.001
        num_matches = 5
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            """
                            WITH vector_matches AS (
                              SELECT page, text, embedding, 1 - (embedding <=> $1) AS similarity
                              FROM text_embeddings
                              WHERE 1 - (embedding <=> $1) > $2
                              ORDER BY similarity DESC
                              LIMIT $3
                            )
                            SELECT * FROM vector_matches
                            """,
            emb_query,
            similarity_threshold,
            num_matches,
        )
        if len(results) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")
        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(
                {
                    "page": r["page"],
                    "text": r["text"],
                    #"embedding": r["embedding"],
                    "similarity": r["similarity"]
                }
                )
        await conn.close()
        return matches
    
# %%
