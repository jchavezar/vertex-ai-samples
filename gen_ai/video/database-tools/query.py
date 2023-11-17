#%%
import asyncio
import asyncpg
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.vision_models import MultiModalEmbeddingModel
import sys
sys.path.append("../front-end")
from utils import variables, credentials

var={
    "project_id":variables.PROJECT_ID,
    "region":variables.REGION,
    "video_gcs_uri":variables.VIDEO_GCS_URI,
    "video_transcript_annotations_gcs":variables.VIDEO_TRANSCRIPT_ANNOTATIONS_GCS,
    "snippets_gcs_uri":variables.SNIPPETS_GCS_URI,
    "database_name":variables.DATABASE_NAME,
    "instance_name":variables.INSTANCE_NAME,
    "database_user":variables.DATABASE_USER,
    "database_password":credentials.DATABASE_PASSWORD,
    "linux":variables.LINUX,
}

mm=MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

async def query(query):
    matches=[]
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f'{var["project_id"]}:{var["region"]}:{var["instance_name"]}',  # Cloud SQL instance connection name
            "asyncpg",
            user=f'{var["database_user"]}',
            password=f'{var["database_password"]}',
            db=f'{var["database_name"]}',
        )
    emb_query = mm.get_embeddings(contextual_text=query).text_embedding
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
    print(matches)
    await conn.close()
    return matches

matches = await query("a ball")
# %%

