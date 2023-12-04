#%%
#region Import Libraries
import io
import time
import PyPDF2
import asyncio
import asyncpg
import concurrent
from credentials import *
from typing import Dict
from google.cloud import documentai
from pgvector.asyncpg import register_vector
from google.cloud.documentai_v1 import Document
from google.cloud.sql.connector import Connector
from vertexai.preview.language_models import TextEmbeddingModel
#endregion


# Create the database first: gcloud sql databases create rag-pgvector-conversational-rag-1 --instance=pg15-pgvector-demo


#region variables
start_job_time = time.time()
file_name = "../northam.pdf"
pdfs = []
results = []
project_id = "vtxdemos"
region = "us-central1"
instance_name = "pg15-pgvector-demo"
database_user = "emb-admin"
database_password = DATABASE_PASSWORD
database_name = "rag-pgvector-conversational-rag-1"
docai_processor_id = "projects/254356041555/locations/us/processors/7e6b9d94d3bafa4f"
location = "us"
docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"us-documentai.googleapis.com"})
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
#endregion

#region reading pdf
pdf_data = PyPDF2.PdfReader(file_name)

for page in pdf_data.pages:
    writer = PyPDF2.PdfWriter()
    writer.add_page(page)
    with io.BytesIO() as bytes_stream:
        pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())
rate_limit_minute = 120
adjust_rate_limit = rate_limit_minute / 2
#endregion

#region Doing OCR of multiple pages
print("Entering in OCR zone")
def docai_runner(p, start, raw_document):
  #print(f"Doc: {p}")
  sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
  if sleep_time > 0: 
      time.sleep(sleep_time)
  return docai_client.process_document(
      request = documentai.ProcessRequest(
      name = docai_processor_id,
      raw_document = documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'),
      process_options = documentai.ProcessOptions(
      from_start = 5,
      ocr_config = documentai.OcrConfig(
          enable_symbol = True,
          enable_image_quality_scores = True,
          premium_features = documentai.OcrConfig.PremiumFeatures(
              compute_style_info = True)))))
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
ocr_time = time.time()-start_job_time
print(f"Time checkpoint [ocr]: {ocr_time}")
#endregion

#region Creating embeddings from chunk
start = time.time()
pp = 0
for page ,paragraphs in documents.items():
    embeddings = []
    
    rate_limit_minute = 550
    
    for paragraph in paragraphs:
        pp += 1
        #elapsed_time = time.time() - start
        sleep_time = (pp*(60/rate_limit_minute)) - (time.time()-start)
        if sleep_time > 0:
            time.sleep(sleep_time)
            #start = time.time()
            #sleep_time = 0
            #pp = 0
        embeddings.append({paragraph : model_emb.get_embeddings([paragraph])[0].values})
        documents[page] = embeddings
print(f"Time checkpoint [embeddings]: {time.time()-start}")
#endregion

embeddings_time = time.time()-start_job_time
print(f"Total time checkpoint: {embeddings_time}")

#return documents, ocr_time, embeddings_time

#region creating/dropping table
async def create_table():
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
        await conn.execute("DROP TABLE IF EXISTS text_embeddings CASCADE")
        await conn.execute(
            """CREATE TABLE text_embeddings(
                                page VARCHAR(1000),
                                text VARCHAR(1000),
                                embedding vector(768))"""
        )
        print("Create Table Done...")
        await conn.close()
#endregion

#region insert items into the table
async def insert_documents_vdb(documents: Dict):
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

await create_table()
await insert_documents_vdb(documents)
# %%

