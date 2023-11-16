import asyncio
import asyncpg
import numpy as np
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
    
    async def create_database(self):
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

                # Create the `video_embeddings` table.
                await conn.execute(
                    """CREATE TABLE IF NOT EXISTS video_embeddings(
                                        index VARCHAR(1000),
                                        ai_type VARCHAR(1000),
                                        class VARCHAR(1000),
                                        summary VARCHAR(1000),
                                        image_transcript_link VARCHAR(100000),
                                        frame_link VARCHAR(1000),
                                        video_link VARCHAR(1000),
                                        embedding vector(1408))"""
                )
                print("Create Table Done...")
                await conn.close()
    
    async def insert_item(self, df):
        if type(df["embedding"][0]) == list:
            df["embedding"] = df["embedding"].apply(lambda x: np.array(x))
        elif type(df["embedding"][0]) == str:
            df["embedding"] = df["embedding"].apply(lambda x: np.array(x.strip("][").split(",")))
        else: pass
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
            for index, row in df.iterrows():
                await conn.execute(
                    "INSERT INTO video_embeddings (index, ai_type, class, summary, image_transcript_link, frame_link, video_link, embedding) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                    row["index"],
                    row["ai_type"],
                    row["class"],
                    row["summary"],
                    row["image_transcript_link"],
                    row["frame_link"],
                    row["video_link"],
                    row["embedding"],
                )
            print("Insert Items Done...")
            await conn.close()