#%%
#region Import Libraries
from functools import reduce
import asyncio
import asyncpg
import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
#endregion

class Client:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
            
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
                f"""CREATE TABLE text_embeddings({self.schema}, embedding vector(768))"""
            )
            #st.markdown(":blue[Create Table Done...]")
            await conn.close()
    #endregion

    #region insert values
    async def insert_documents_vdb(self):
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
            for doc in self.documents:
                values = tuple(list(doc.values()))
                await conn.copy_records_to_table('text_embeddings', records=[values])
            #st.markdown(":blue[Insert Items Done...]")
            await conn.close()
    #endregion
    
    async def query(self, query, schema_keys):
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
        emb_query = query
        await register_vector(conn)
        similarity_threshold = 0.001
        num_matches = 5
        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            f"""
                            WITH vector_matches AS (
                              SELECT {schema_keys}, embedding, 1 - (embedding <=> $1) AS similarity
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
        
        keys_list = list([str(v) for v in schema_keys.split(",")])
        #data = " | ".join(keys_list) + " | " + "similarity_score"
        data = ""
        lst = []
        
        for r in results:
            # Collect the description for all the matched similar toy products.

            res = str([v for v in r.values()][1])
            data += res + "\n"
            lst.append(res)
        with st.expander(label="Vector Query Result"):
            st.write(lst)
        #st.dataframe(pd.DataFrame({"text": lst}))

        await conn.close()
        return data
    
    async def run(self, docs: List):
        
        self.documents = docs
        self.schema_keys = ",".join([doc for doc in self.documents[0].keys() if doc != "embedding"])
        self.schema = ", ".join([f"{k} VARCHAR(10000)" for k,v in self.documents[0].items() if k != "embedding"])
        
        await self.create_table()
        await self.insert_documents_vdb()
        return self.schema_keys
        
# %%