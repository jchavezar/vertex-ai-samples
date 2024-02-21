import io
import time
import PyPDF2
import asyncio
import asyncpg
import vertexai
import concurrent
from typing import Dict
from google.cloud import documentai
from pgvector.asyncpg import register_vector
from google.cloud.documentai_v1 import Document
from google.cloud.sql.connector import Connector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel


class Client:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        
        vertexai.init(project=self.project_id, location=self.region)
        
    
    def file_preprocessing(self, filename: str):
        #region Extracting text using fast processing (concurrent+futures) PyPDF2 to split per page and DocumentAI to extract text.
        pdfs = []
        results = []
        documents = {}
        start_job_time = time.time()
        
        docai_client = documentai.DocumentProcessorServiceClient(
            client_options = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
            )

        pdf_data = PyPDF2.PdfReader(filename)
        
        for page in pdf_data.pages: # pdf file is splitted in multiple pages.
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            with io.BytesIO() as bytes_stream:
                pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())
        rate_limit_minute = 120
        adjust_rate_limit = rate_limit_minute / 2
        
        print("DocumentAI: reading and splitting the document...")
        def docai_runner(p, start, raw_document):
          sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start) # DocumentAI has a limit of 120 QPM.
          if sleep_time > 0: 
              time.sleep(sleep_time)
          return docai_client.process_document(
              request = documentai.ProcessRequest(
              name = self.docai_processor_id,
              raw_document = documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'),
              process_options = documentai.ProcessOptions(
              from_start = 5,
              ocr_config = documentai.OcrConfig(
                  enable_symbol = True,
                  enable_image_quality_scores = True,
                  premium_features = documentai.OcrConfig.PremiumFeatures(
                      compute_style_info = True)))))
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor: # Here multithreads with futures is being used to speed up the reading process.
            futures = [
                executor.submit(
                    docai_runner,
                    p, start,
                    file
                ) for p, file in enumerate(pdfs)
            ]
            for future in concurrent.futures.as_completed(futures):
              results.append(Document.to_dict(future.result().document))
        #endregion
        
        #region Using Langchain (ONLY) to split by chunks
        documents = {}
        
        #re = []
        for page, result in enumerate(results):
            splits = []
            for i in RecursiveCharacterTextSplitter(chunk_size = self.embeddgins_chunk_size, chunk_overlap  = self.embeedings_chunk_overlap, length_function = len, add_start_index = True,).create_documents([result["text"]]):
                splits.append(i.page_content)                
            documents[str(page+1)] = splits
        
        reading_time = time.time()-start_job_time
        print(f"DocumentAI (splitting and reading): Job Finished, time: {time.time()-start_job_time}")
        #endregion
        
        #region Creating embeddings from document chunks
        print("Embeddings|LLM: creating embeddings from splits...")
        _ = time.time()
        pp = 0
        for page ,paragraphs in documents.items():
            embeddings = []
            
            rate_limit_minute = 550
            
            for paragraph in paragraphs:
                pp += 1
                sleep_time = (pp*(60/rate_limit_minute)) - (time.time()-start)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                text_to_embed = f"page_number: {page}, paragraph or text: {paragraph}" # Adding page number to embeddings to add it to the context
                embeddings.append({"text": text_to_embed, "embedding" : TextEmbeddingModel.from_pretrained(self.embeddings_model).get_embeddings([text_to_embed])[0].values}) # textembedding-gecko@001 is being used for each paragraph: {"text": "page number: 0, text: paragraph"}
                documents[page] = embeddings
        print(f"Embeddings|LLM: Job Finished,  time: {time.time()-start}")
        #endregion
        
        embeddings_time = time.time()-_
        print(f"Total time checkpoint: {time.time()-start_job_time}")
        return documents, reading_time, embeddings_time
    
    #region creating/dropping table
    async def create_table(self, database_name: str):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=database_name,
            )
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Create the `text_embeddings` table.
            await conn.execute("DROP TABLE IF EXISTS text_embeddings CASCADE")
            await conn.execute(
                """CREATE TABLE text_embeddings(
                                    page VARCHAR(1000),
                                    text VARCHAR(10000),
                                    embedding vector(768))"""
            )
            print("Create Table Done...")
            await conn.close()
    #endregion

    #region insert items into the table
    async def insert_documents_vdb(self, documents: Dict, database_name: str):
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=database_name,
            )
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Store all the generated embeddings back into the database.
            for page, document in documents.items():
                for do in document:
                    await conn.execute(
                        "INSERT INTO text_embeddings (page, text, embedding) VALUES ($1, $2, $3)",
                        page,
                        do["text"],
                        do["embedding"],   
                    )
            print("Insert Items Done...")
            await conn.close()
    #endregion