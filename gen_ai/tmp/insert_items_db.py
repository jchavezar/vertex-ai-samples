#%%
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector

project_id = "vtxdemos"  # @param {type:"string"}
database_password = "Pumasunam1!"  # @param {type:"string"}
region = "us-central1"  # @param {type:"string"}
instance_name = "pg15-pgvector-demo"  # @param {type:"string"}
database_name = "vi-llm"  # @param {type:"string"}
database_user = "emb-admin"  # @param {type:"string"}

#def insert_item(df):
async def insert_item(df):
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )
        # Store all the generated embeddings back into the database.
        for index, row in df.iterrows():
            await conn.execute(
                "INSERT INTO video_metadata (transcription, class, summary, video_link, snippet_link) VALUES ($1, $2, $3, $4, $5)",
                row["transcription"],
                row["class"],
                row["summary"],
                row["video_link"],
                row["snippet_link"],
            )
        await conn.close()

# %%
