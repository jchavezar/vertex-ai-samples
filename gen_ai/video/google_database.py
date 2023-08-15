import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector

class vector_db:
    def __init__(self,
                 project_id,
                 region,
                 instance_name,
                 database_user,
                 database_password
                 ):
        self.project_id = project_id
        self.region = region
        self.instance_name = instance_name
        self.database_user = database_user
        self.database_password = database_password
    
    async def create_database(self, database_name):
            self.database_name = database_name
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
                                        index VARCHAR(100),
                                        sports_type VARCHAR(10),
                                        summary VARCHAR(1000),
                                        frame_link VARCHAR(100),
                                        video_link VARCHAR(100),
                                        embedding vector(1408))"""
                )
                print("Create Table Done...")
                await conn.close()
    
    async def insert_item(self, df, database_name=""):
        if database_name=="":
             database_name=self.database_name
        else: pass
        df2 = df.copy()
        df2["embedding"] = df2["embedding"].apply(lambda x: np.array(x.strip("][").split(",")))
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

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Store all the generated embeddings back into the database.
            for index, row in df2.iterrows():
                await conn.execute(
                    "INSERT INTO video_embeddings (index, sports_type, summary, frame_link, video_link, embedding) VALUES ($1, $2, $3, $4, $5, $6)",
                    row["index"],
                    row["sports_type"],
                    row["summary"],
                    row["frame_link"],
                    row["video_link"],
                    row["embedding"],
                )
            print("Insert Items Done...")
            await conn.close()
    
    async def query(self, query, database_name=""):
        matches=[]
        if database_name=="":
             database_name=self.database_name
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

            await register_vector(conn)
            similarity_threshold = 0.001
            num_matches = 10

            # Find similar products to the query using cosine similarity search
            # over all vector embeddings. This new feature is provided by `pgvector`.
            results = await conn.fetch(
                """
                                WITH vector_matches AS (
                                  SELECT index, sports_type, summary, frame_link, video_link, embedding, 1 - (embedding <=> $1) AS similarity
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
                        "sports_type": r["sports_type"],
                        "summary": r["summary"],
                        "frame_link": r["frame_link"],
                        "video_link": r["video_link"],
                        "embedding": r["embedding"],
                        "similarity": r["similarity"]
                    }
                )

            await conn.close()
            return matches

    async def delete(self, query, database_name=""):
        matches=[]
        if database_name=="":
             database_name=self.database_name
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

            await register_vector(conn)
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute("DROP TABLE IF EXISTS video_embeddings")

            await conn.close()
            return matches
