#%%
#region Import Libraries
import io
import json
import time
import PyPDF2
import asyncio
import asyncpg
import vertexai
import concurrent
import numpy as np
import pandas as pd
from typing import Dict
from google.cloud import documentai
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector
from google.cloud.documentai_v1 import Document
from google.cloud.sql.connector import Connector
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        aiplatform.init(project="vtxdemos")
        self.model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        self.model_text = TextGenerationModel.from_pretrained("text-bison")

        self.text_bison_parameters = {
            "candidate_count": 1,
            "max_output_tokens": 2048,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
            }
    
    def prepare_file(self, filename: str):
        pdfs = []
        results = []
        documents = {}
        start_job_time = time.time()
                
        docai_client = documentai.DocumentProcessorServiceClient(
            client_options = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
            )

        pdf_data = PyPDF2.PdfReader(filename)
        
        for page in pdf_data.pages:
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            with io.BytesIO() as bytes_stream:
                pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())

        rate_limit_minute = 120
        adjust_rate_limit = rate_limit_minute / 2
        
        #region Doing OCR of multiple pages
        print("Entering in OCR zone")
        def docai_runner(p, start, raw_document):
          #print(f"Doc: {p}")
          sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
          if sleep_time > 0: 
              time.sleep(sleep_time)
          return docai_client.process_document(request = {"raw_document" : documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'), "name" : self.docai_processor_id})

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
        
        #region Creating embeddings from chunks

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
                embeddings.append({paragraph : self.model_emb.get_embeddings([paragraph])[0].values})
                documents[page] = embeddings
        print(f"Time checkpoint [embeddings]: {time.time()-start}")
        #endregion
        
        embeddings_time = time.time()-start_job_time
        print(f"Total time checkpoint: {embeddings_time}")
        return documents, ocr_time, embeddings_time

    #region create table
    async def create_table(self):
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

    #region insert values
    async def insert_documents_vdb(self, documents: Dict):
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
        emb_query = self.model_emb.get_embeddings([query])[0].values
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
                    "page": r["page"],
                    "text": r["text"],
                    #"embedding": r["embedding"],
                    "similarity": r["similarity"]
                }
                )
        await conn.close()
        return matches
    
    def llm_predict(self, prompt: str, context: json) -> str:
        
        response = self.model_text.predict(
            f"""Give a detailed answer to the question using information from the provided contexts.:
            {context}
            
            Question:
            {prompt}

            Answer and Explanation:
            """,
            **self.text_bison_parameters
            )
        return response.text.replace("$","")

# %%