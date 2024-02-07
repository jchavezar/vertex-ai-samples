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
import streamlit as st
from typing import Dict
from google.cloud import documentai
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector
from google.cloud.documentai_v1 import Document
from google.cloud.sql.connector import Connector
from vertexai.preview.language_models import TextGenerationModel, TextEmbeddingModel
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        aiplatform.init(project="vtxdemos")
        self.model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    
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
          return docai_client.process_document(
              request = documentai.ProcessRequest(
              name = self.docai_processor_id,
              raw_document = documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'),
              process_options = documentai.ProcessOptions(
              from_start = 5)))
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
              results.append(Document.to_dict(future.result().document)["text"])
        
        def split_text_by_chunks(text, chunk_size):
            return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        documents = {}
        for page, result in enumerate(results):
            documents[str(page)] = split_text_by_chunks(result, 750)
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
    

    __ = """"You are an expert analyst on tax forms, your expertise is better on forms like 1065. 
            From the following context respond the question in a vert detailed way:
            - Do not make up answers, if you do not know it just say it.
            - Always bring all the responses if ambigous never leave back any repeatable response.
            - Include all the responses and their reasoning.
            - Be verbose.
            """
    
    def llm_predict(self, prompt: str, context: json, model_id: str, parameters: dict) -> str:
        
        st.write(f"testing model: {model_id}")
        
        model_text = TextGenerationModel.from_pretrained(model_id)
        
        response = model_text.predict(
            f"""

            You are Tax Returns Preparer, friendly and helpful AI assistant that answers questions related to tax return documents.You are given texts from the forms and you give short and precise answers with the line number from the IRS form mentioned in current context.
            Some table information from forms is given as text,each line is a row in table and columns are separated by pipe symbol(|).
            Sometimes there are multiple values associated to a single line item and are separated by pipe symbol(|).In this case,give all the values instead of the first value.
            If amount values are 0,then return the amounts as 0 rather than no information provided.
            If you are asked Yes/No questions,then look out for selected and unselected text with Yes or No to answer these better.
            If Yes:selected then the answer is yes or if No:selected then the answer is no
            Use the following pieces of context to help answer the user's question. You must include sources used to answer this question. If its not relevant to the question, provide friendly responses.
            Answer the questions that are only related to tax forms or the data provided.If asked other questions,then respond as cannot answer.
            
            Context:
            {context}
            
            Question:
            {prompt}

            Answer and Explanation:
            """,
            **parameters
            )
        return response.text.replace("$","")

# %%