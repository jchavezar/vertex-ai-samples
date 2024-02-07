# %%
#Extracting data and create embeddings prework

#region Import Libraries
import io
import time
import PyPDF2
import vertexai
import concurrent
import credentials
import numpy as np
from google.cloud import documentai
from google.cloud.documentai_v1 import Document
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
#endregion

#region Set Variables
project_id = "vtxdemos"
region = "us-central1"
location = "us"
docai_processor_id = "projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b"
rate_limit_minute = 120
adjust_rate_limit = rate_limit_minute / 2
source_document_name = "alphabet_10k"
instance_name = "pg15-pgvector-demo"
database_user = "emb-admin"
database_name = "text-emb-1"
database_password = credentials.db_password
pdfs = []
results = []
documents = []
page_images = []
#endregion

model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
vertexai.init(project="vtxdemos", location="us-central1")

#region set document_ai for ocr
docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
)
#endregion

#%%
#region Document Preprocess
#splitting per pages, ocr streaming and split it further by chunks
pdf_data = PyPDF2.PdfReader("20230203_alphabet_10K_removed.pdf")

for page_num, page in enumerate(pdf_data.pages, 1):
  writer = PyPDF2.PdfWriter()
  writer.add_page(page)
  with io.BytesIO() as bytes_stream:
    pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())

rate_limit_minute = 120
adjust_rate_limit = rate_limit_minute / 2

def docai_runner(p, start, raw_document):
  sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
  if sleep_time > 0: time.sleep(sleep_time)
  return docai_client.process_document(request = {"raw_document" : documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'), "name" : docai_processor_id})

start = time.time()
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(
            docai_runner,
            p, start,
            file
        ) for p, file in enumerate(pdfs)
    ]
    for future in concurrent.futures.as_completed(futures):
      results.append(Document.to_dict(future.result().document))
    
def split_text_by_chunks(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

documents = {}
for page, result in enumerate(results):
    documents[str(page)] = split_text_by_chunks(result["text"], 750)

for page,paragraphs in documents.items():
    embeddings = []
    for paragraph in paragraphs:
        embeddings.append({paragraph : model.get_embeddings([paragraph])[0].values})
    documents[page] = embeddings
#endregion


#%%
#region Create Vector Database
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
#%%
#region create database
!gcloud sql databases create --instance=pg15-pgvector-demo $database_name
#endregion
#%%

#region create table
async def create_table(database_name):
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
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Create the `text_embeddings` table.
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS text_embeddings(
                                    page VARCHAR(1000),
                                    text VARCHAR(1000),
                                    embedding vector(768))"""
            )
            print("Create Table Done...")
            await conn.close()
#endregion

await create_table(database_name=database_name)
#%%
#region insert items into the table
async def insert_item(documents, database_name):
    #if type(df["embedding"][0]) == list:
    #    df["embedding"] = df["embedding"].apply(lambda x: np.array(x))
    #elif type(df["embedding"][0]) == str:
    #    df["embedding"] = df["embedding"].apply(lambda x: np.array(x.strip("][").split(",")))
    #else: pass
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
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector(conn)
        # Store all the generated embeddings back into the database.
        for page, document in documents.items():
            for do in document:
                for text_paragraph, embeddings in do.items():
                    await conn.execute(
                        "INSERT INTO text_embeddings (page, text, embedding) VALUES ($1, $2, $3)",
                        page,
                        text_paragraph,
                        embeddings,   
                    )
        print("Insert Items Done...")
        await conn.close()
#endregion

await insert_item(documents=documents, database_name=database_name)

#%%
#region query items for testing
async def query(database_name):
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

            await register_vector(conn)
            similarity_threshold = 0.001
            num_matches = 10

            # Find similar products to the query using cosine similarity search
            # over all vector embeddings. This new feature is provided by `pgvector`.
            results = await conn.fetch("""SELECT * FROM text_embeddings""",)
            for r in results:
                print(r)
            await conn.close()
            return results
#endregion

results = await query(database_name=database_name)

#%%


#region query matching testing
async def query(emb_prompt, database_name=""):
        matches=[]
        if database_name=="":
             database_name=database_name
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

            await register_vector(conn)
            similarity_threshold = 0.001
            num_matches = 10

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
                emb_prompt,
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
                        "embedding": r["embedding"],
                        "similarity": r["similarity"]
                    }
                )

            await conn.close()
            return matches
#%%
prompt = "what was the Alphabet revenue for 2022?" 
emb_prompt = model.get_embeddings([prompt])[0].values
print(emb_prompt)
matches = await query(emb_prompt=emb_prompt, database_name=database_name)
#endregion
# %%
