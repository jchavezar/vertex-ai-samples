# @title Vertex AI Utility functions for using with Langchain

import time
from typing import List
import pandas as pd
from pydantic import BaseModel
from langchain.llms import VertexAI
from google.cloud.bigquery import Client
from langchain.document_loaders.dataframe import DataFrameLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import VertexAIEmbeddings

class LLM:
  def __init__(self, bq_source: str, text_model: str):
    self.bq_source = bq_source
    self.text_model = text_model
  
  def LoadModels(self):
    # Utility functions for Embeddings API with rate limiting
    def rate_limit(max_per_minute):
      period = 60 / max_per_minute
      print('Waiting')
      while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
          print('.', end='')
          time.sleep(sleep_time)
    class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
      requests_per_minute: int
      num_instances_per_batch: int

      # Overriding embed_documents method
      def embed_documents(self, texts: List[str]):
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
          # Working in batches because the API accepts maximum 5
          # documents per request to get embeddings
          head, docs = docs[:self.num_instances_per_batch], docs[self.num_instances_per_batch:]
          chunk = self.client.get_embeddings(head)
          results.extend(chunk)
          next(limiter)
        
        return [r.values for r in results]
      
    self.llm = VertexAI(
      model_name=self.text_model,
      max_output_tokens=256,
      temperature=0.1,
      top_p=0.8,
      top_k=40,
      verbose=True,
      )
      
      # Embedding
    self.embeddings = CustomVertexAIEmbeddings(
          requests_per_minute=100,
          num_instances_per_batch=5,
    )
  
    return self.llm, self.embeddings  
  
  def LoadDataset(self) -> pd.DataFrame:
    client = Client(project=self.bq_source.split(".")[0])
    query = f"""SELECT * FROM {self.bq_source}"""
    df = client.query(query).to_dataframe()
    
    data = []
    for index, rows in df.iterrows():
      text = """On {0}, the service: {1}, located on region: {2}, had a consumption of: {3}.
      """.format(
          rows['month'],
          rows['service'],
          rows['regions'],
          rows['consumption']
          )
      data.append(text)

    # Put it in a dataframe so we can easily index it
    nl_df = pd.DataFrame(data, columns=['text'])
    
    persistent_path = 'local_data'
    
    df_loader = DataFrameLoader(nl_df, page_content_column="text")
    df_index = VectorstoreIndexCreator(embedding=self.embeddings, vectorstore_kwargs={
      'persist_directory': f'{persistent_path}/billing'
      }).from_loaders([df_loader])
    
    return df, nl_df, df_index