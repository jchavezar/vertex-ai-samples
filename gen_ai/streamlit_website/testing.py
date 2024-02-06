#%%
import asyncio
import asyncpg
from utils.video.credentials import *
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel

model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

embeddings = []
embeddings.append({"Page":0, "Content": "Hola como le va senior", "Embedding": model_emb.get_embeddings(["Hola como le va senior"])[0].values})

# %%
variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_rag_lang",
    "database_password": DATABASE_PASSWORD, #utils.video.credentials
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

#%%
async def query(documents):
  import numpy as np
  schema_col = ", ".join([k for k,v in documents[0].items() if k != "Embedding"])
  schema = ", ".join([f"{k} VARCHAR(10000)" for k,v in documents[0].items() if k != "Embedding"])
  
  print(schema_col)      
  loop = asyncio.get_running_loop()
  async with Connector(loop=loop) as connector:
      # Create connection to Cloud SQL database.
      conn: asyncpg.Connection = await connector.connect_async(
          "vtxdemos:us-central1:pg15-pgvector-demo",  # Cloud SQL instance connection name
          "asyncpg",
          user="emb-admin",
          password=f"{variables['database_password']}",
          db="ask_your_doc_rag_lang",
      )
      await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
      await register_vector(conn)
      x = ("0", "testing", np.arange(768))
      #await conn.copy_records_to_table('text_embeddings', records=[x])
      
      res = await conn.fetch('SELECT * FROM text_embeddings')
      print(res)

      print("Insert Items Done...")
      await conn.close()

asyncio.run(query(embeddings))

# %%
