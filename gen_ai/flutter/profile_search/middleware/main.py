import json
import pandas as pd
from fastapi import FastAPI
from google.cloud import aiplatform, storage
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project = "vtxdemos"
region = "us-central1"
data_uri = "gs://vtxdemos-vsearch-datasets/stgwell_data/df3.csv"
my_index_endpoint_2 = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/4390081648872390656"
)

app = FastAPI()
emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

storage.Client(project=project).bucket("vtxdemos-vsearch-datasets").blob("stgwell_data/df3.csv").download_to_filename("df3.csv")
app.df = pd.read_csv("df3.csv")
app.df.fillna("", inplace=True)
# Vector Search


@app.get('/scann/{query}')
def return_catalog_scann(query: str):
    """

    :param query: from flutter
    """
    
    request = emb_model.get_embeddings([TextEmbeddingInput(query, "RETRIEVAL_QUERY")])[0].values

    response = my_index_endpoint_2.find_neighbors(
      deployed_index_id = "vs_stgwell_deployed_v3",
      queries = [request],
      num_neighbors = 10
    )

    nn = [int(i.id) for i in response[0]]
    new_df = app.df.loc[[int(i.id) for i in response[0]],:]
    #df = app.df.loc[app.df['id'].isin(nn)]
    res = new_df.to_json(orient="records")
    parsed = json.loads(res)
    for i in parsed:
      print("-"*80)
      print(i["name"])
      print(i["company"])
      print(i["job_title"])
      print(i["location"])
      print(i["gemini_summ"])
    return parsed


@app.get('/all')
def return_catalog_full():
    """

    :param query: from flutter
    """
    parsed = json.loads(df.to_json(orient="records"))
    return parsed

