import base64
import json
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Form
from google.cloud import aiplatform, bigquery
from vertexai.vision_models import MultiModalEmbeddingModel, Image, Video
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project = "vtxdemos"
region = "us-central1"
bq_client = bigquery.Client()

embeddings_file = "gs://vtxdemos-vsearch-datasets/data.json"
my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/6712813156688723968",
)

my_index_endpoint_mm = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/4457635643282948096",
)

combined_index = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/6729138705337942016",
)


app = FastAPI()
mm = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

#sql = """
#select * from vtxdemos.abnb.sytheticdb_lat
#"""

#app.df = bq_client.query_and_wait(sql).to_dataframe()
app.df = pd.read_csv("data.csv")
app.df2 = pd.read_csv("combined_data.csv")
print("dataset loaded")

# Vector Search


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


@app.get('/scann/{query}')
def return_catalog_scann(query: str):
    """

    :param query: from flutter
    """
#    embeddings = mm.get_embeddings(
#        contextual_text=query,
#    ).text_embedding

    e = text_emb_model.get_embeddings([TextEmbeddingInput(query, "SEMANTIC_SIMILARITY")])[0].values


    response = my_index_endpoint.find_neighbors(
        deployed_index_id = "vs_abnb_deployed_text_3",
        queries = [e],
        num_neighbors = 10
    )

    nn_list = [int(i.id) for i in response[0]]
    order_df = pd.DataFrame({'id': nn_list})
    merged_df = app.df.merge(order_df, on='id', how='inner')
    final_df = merged_df.set_index('id').loc[nn_list].reset_index()
    final_df.fillna("value", inplace = True)

    res = final_df.to_json(orient="records")
    parsed = json.loads(res)
    print(merged_df["Img_exterior_url_0"].iloc[0])
    print(parsed)
    return parsed

@app.post('/image')
async def image_conversion(file: UploadFile = File(...), text_data: Optional[str] = Form(None)):
    contents = await file.read()
    print(contents)
    
#    e = mm.get_embeddings(image=Image(image_bytes=contents)).image_embedding

    def l2_normalize(vector):
        """Normalizes a vector to unit length using L2 normalization."""
        l2_norm = np.linalg.norm(vector)
        if l2_norm == 0:
            return vector  # Avoid division by zero
        return vector / l2_norm
    
    def normalize_query(text_data:str, video: bytes):
        e = mm.get_embeddings(
            video=Video(
                video_bytes=video
            ),
            contextual_text=text_data,
        )
        print("embeddings ready")
        
        normalized_video_embedding = l2_normalize(e.video_embeddings[0].embedding)
        normalized_text_embedding = l2_normalize(e.text_embedding)
        print("normalized done")
        we_ave =  (0.7 * normalized_video_embedding) + (0.3 * normalized_text_embedding)
        return we_ave
        
    if text_data:
        e = normalize_query(text_data, contents)
        print("it worked!")
    
    else:
        embeddings = mm.get_embeddings(video=Video(video_bytes=contents))
        e = embeddings.video_embeddings[0].embedding
    
    response = combined_index.find_neighbors(
        deployed_index_id = "vs_abnb_deployed_combined_1",
        queries = [e],
        num_neighbors = 10
        )
    
    print("response finished.")
    
    nn_list = [int(i.id) for i in response[0]]
    order_df = pd.DataFrame({'id': nn_list})
    merged_df = app.df2.merge(order_df, on='id', how='inner')
    final_df = merged_df.set_index('id').loc[nn_list].reset_index()
    final_df.fillna("value", inplace = True)
    
    res = final_df.to_json(orient="records")
    parsed = json.loads(res)
    
    print(final_df["Img_interior_url_0"].iloc[0])
    print(final_df["Img_interior_url_1"].iloc[0])
    print(final_df["Img_interior_url_2"].iloc[0])
    print(final_df["Img_interior_url_3"].iloc[0])
    print(final_df["Img_interior_url_4"].iloc[0])
    
    return parsed



@app.get('/all')
def return_catalog_full():
    """

    :param query: from flutter
    """
    parsed = json.loads(df.to_json(orient="records"))
    return parsed


