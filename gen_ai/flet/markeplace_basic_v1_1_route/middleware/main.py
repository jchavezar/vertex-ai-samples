import json
import vertexai
import numpy as np
import pandas as pd
from google.cloud import bigquery
from google.cloud import discoveryengine_v1 as discoveryengine
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = "vtxdemos"
embeddings_model_name = "text-embedding-004"
engine_id = "etsy_1728670138036"

vertexai.init(project=project_id)
client = discoveryengine.SearchServiceClient()
text_emb_model = TextEmbeddingModel.from_pretrained(embeddings_model_name)
serving_config = f"projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"
listing_queries = pd.read_pickle("gs://vtxdemos-datasets-private/marketplace/queries_10k.pkl")
listing_all = bigquery.Client().query("select * from `demos_us.etsy-v1_1_10k_v2`").to_dataframe()

class VaIS:
  def __init__(self):
    pass

  def search(self, query):
    self.request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=20,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )
    response = client.search(self.request)

    rag = {
        "a_cat_1": [],
        "q_cat_1": [],
        "tags": [],
        "generated_description": [],
        "a_cat_2": [],
        "price_usd": [],
        "category_id": [],
        "attributes": [],
        "category_path": [],
        "image_url": [],
        "title": [],
        "generated_title": [],
        "combined_text": [],
        "q_cat_2": [],
        "detailed_description": [],
        "listing_id": [],
        "public_cdn_link": [],
        "public_gcs_link": [],
        "private_gcs_link": [],
        "description": [],
        "cat_3_questions": [],
    }

    for page in response.pages:
      for result in page.results:
        for k,v in result.document.struct_data.items():
          rag[k].append(v)

    return pd.DataFrame(rag)

class LocalEmbeddings:
  def __init__(self):
    # super().__init__()
    self.dataframe = pd.read_pickle("gs://etsy-demo/artifacts/final_df_v11_cdn.pkl")
    self.matrix_len_x = self.dataframe.shape[0]
    self.matrix_len_y = len(self.dataframe.iloc[0]["embedding"])
    self.img = np.array([row["embedding"] for index, row in self.dataframe.iterrows()])

  def load_suggestion_list(self):
    return self.dataframe["generated_queries"].tolist()

  def cosine_similarity(self, b: np.array):
    return np.dot(self.img ,b)/(np.linalg.norm(self.img )*np.linalg.norm(b))

  def vector_search(self, text: str):
    inputs = [TextEmbeddingInput(text, "SEMANTIC_SIMILARITY")]
    input_text_emb = text_emb_model.get_embeddings(inputs)[0].values
    similarities = self.cosine_similarity(input_text_emb)
    neighbors = np.argsort(similarities)[-10:][::-1]
    return self.dataframe.iloc[neighbors]