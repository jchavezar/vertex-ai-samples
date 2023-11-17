#%%
import asyncio
import asyncpg
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.vision_models import MultiModalEmbeddingModel
import sys
sys.path.append("..")
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

print(var)

async def delete():
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
        await register_vector(conn)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute("DROP TABLE IF EXISTS video_embeddings")
        await conn.close()
        return matches
# %%

await delete()
# %%

