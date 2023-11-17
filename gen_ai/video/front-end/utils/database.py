import asyncio
import asyncpg
import numpy as np
from google.cloud.sql.connector import Connector
from pgvector.asyncpg import register_vector

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
    
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
                                  SELECT index, ai_type, class, summary, image_transcript_link, frame_link, video_link, embedding, 1 - (embedding <=> $1) AS similarity
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
                        "image_transcript_link": r["image_transcript_link"],
                        "frame_link": r["frame_link"],
                        "video_link": r["video_link"],
                        "embedding": r["embedding"],
                        "similarity": r["similarity"]
                    }
                )

            await conn.close()
            return matches