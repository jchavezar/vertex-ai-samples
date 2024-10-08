import json
import vertexai
import numpy as np
import pandas as pd
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = "vtxdemos"
embeddings_model_name = "text-embedding-004"

vertexai.init(project=project_id)
text_emb_model = TextEmbeddingModel.from_pretrained(embeddings_model_name)

class LocalEmbeddings:
  def __init__(self):
    # super().__init__()
    self.dataframe = pd.read_pickle("gs://etsy-demo/artifacts/final_df_v11_cdn.pkl")
    self.matrix_len_x = self.dataframe.shape[0]
    self.matrix_len_y = len(self.dataframe.iloc[0]["embedding"])
    self.img = np.array([row["embedding"] for index, row in self.dataframe.iterrows()])

  def cosine_similarity(self, b: np.array):
    return np.dot(self.img ,b)/(np.linalg.norm(self.img )*np.linalg.norm(b))

  def vector_search(self, text: str):
    inputs = [TextEmbeddingInput(text, "SEMANTIC_SIMILARITY")]
    input_text_emb = text_emb_model.get_embeddings(inputs)[0].values
    similarities = self.cosine_similarity(input_text_emb)
    neighbors = np.argsort(similarities)[-10:][::-1]
    return self.dataframe.iloc[neighbors]