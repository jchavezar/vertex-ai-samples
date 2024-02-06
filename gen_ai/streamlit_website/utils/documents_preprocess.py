#%%
import io
import time
import PyPDF2
from typing import List
import concurrent
from google.cloud import documentai
from google.cloud.documentai_v1 import Document
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        self.docai_client = documentai.DocumentProcessorServiceClient(
            client_options = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
            )
        self.model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        
    #region PDF Document Extraction of Multiple Pages    
    def read_file(self, filename: str):
        pdfs = []
        docs = []
        pdf_data = PyPDF2.PdfReader(filename)
        print(f"Number of pages: {len(pdf_data.pages)}")
        for page in pdf_data.pages:
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            with io.BytesIO() as bytes_stream:
                pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())        

        rate_limit_minute = 120
        adjust_rate_limit = rate_limit_minute / 2

        
        print("Reading the file, please wait...")
        def docai_runner(p, start, raw_document):

          sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
          if sleep_time > 0: 
              time.sleep(sleep_time)
          return self.docai_client.process_document(
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
            for page, future in enumerate(concurrent.futures.as_completed(futures)):
                docs.append(Document.to_dict(future.result().document)["text"])
        print(f"Job Finished in: {time.time()-start} sec")
        return docs
    #endregion
        
    def split_docs(self, docs: List, chunk_size=500, chunk_overlap=20):
        print("Split and Chunk Text, please wait.")
        lang_docs = []
        start = time.time()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for page, doc in enumerate(docs):
            _docs = text_splitter.create_documents([doc])
            # Adding metadata to each chunk (page number)
            for lang_doc in _docs:
                lang_doc.metadata["page_number"]=page
                lang_docs.append(lang_doc)
        print(f"Job Finished in: {time.time()-start} sec")
        return lang_docs

        
    def create_embeddings(self, documents: List):
        print("Getting Embeddings Rep from Text, please wait.")
        start = time.time()
        pp = 0
        docs_with_emb = []
        for content in documents:
            
            rate_limit_minute = 550
            
            pp += 1
            #elapsed_time = time.time() - start
            sleep_time = (pp*(60/rate_limit_minute)) - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            docs_with_emb.append({f"page": str(content.metadata["page_number"]), f"content": content.page_content, "embedding": self.model_emb.get_embeddings([f"page: {content.metadata['page_number']}, {content.page_content}"])[0].values})
        print(f"Job Finished in:: {time.time()-start}")
        return docs_with_emb
    
    def run(self, filename):
        start = time.time()
        text = self.read_file(filename)
        docs = self.split_docs(text)
        docs_with_emb = self.create_embeddings(docs)
        print(f"Total Preprocessing Time: {time.time()-start}")
        return docs_with_emb
        

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "rag-pgvector-langchain-1",
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}


# %%