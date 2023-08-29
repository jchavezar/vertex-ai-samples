import asyncio
import asyncpg
import numpy as np
from google.cloud.sql.connector import Connector
from pgvector.asyncpg import register_vector

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
                    "INSERT INTO video_embeddings (index, ai_type, class, summary, frame_link, video_link, embedding) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    row["index"],
                    row["ai_type"],
                    row["class"],
                    row["summary"],
                    row["frame_link"],
                    row["video_link"],
                    row["embedding"],
                )
            print("Insert Items Done...")
            await conn.close()
    
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

            await register_vector(conn)
            similarity_threshold = 0.001
            num_matches = 10

            # Find similar products to the query using cosine similarity search
            # over all vector embeddings. This new feature is provided by `pgvector`.
            results = await conn.fetch(
                """
                                WITH vector_matches AS (
                                  SELECT index, ai_type, class, summary, frame_link, video_link, embedding, 1 - (embedding <=> $1) AS similarity
                                  FROM video_embeddings
                                  WHERE 1 - (embedding <=> $1) > $2
                                  ORDER BY similarity DESC
                                  LIMIT $3
                                )
                                SELECT * FROM vector_matches
                                """,
                query,
                similarity_threshold,
                num_matches,
            )

            if len(results) == 0:
                raise Exception("Did not find any results. Adjust the query parameters.")

            for r in results:
                # Collect the description for all the matched similar toy products.
                matches.append(
                    {
                        "index": r["index"],
                        "ai_type": r["ai_type"],
                        "class": r["class"],
                        "summary": r["summary"],
                        "frame_link": r["frame_link"],
                        "video_link": r["video_link"],
                        "embedding": r["embedding"],
                        "similarity": r["similarity"]
                    }
                )

            await conn.close()
            return matches

    async def delete(self):
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
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute("DROP TABLE IF EXISTS video_embeddings")

            await conn.close()
            return matches
    
    async def query_test(self, query):
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
            results = await conn.fetch(f"{query}")

            await conn.close()
            return results