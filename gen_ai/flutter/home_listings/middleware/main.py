import base64
import json
import vertexai
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from vertexai.vision_models import MultiModalEmbeddingModel, Image, Video
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project = "vtxdemos"
region = "us-central1"

vertexai.init(project="vtxdemos", location="us-central1")

img_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

embeddings_file = "gs://vtxdemos-vsearch-datasets/data.json"
combined_index = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/5429850212841553920",
)

text_index = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name="projects/254356041555/locations/us-central1/indexEndpoints/8168601736236236800"
)

app = FastAPI()

app.df = pd.read_csv("gs://vtxdemos-vsearch-datasets/homes_listings/data.csv")
app.df2 = pd.read_csv("gs://vtxdemos-vsearch-datasets/homes_listings/combined_data.csv")
app.df3 = pd.read_pickle("gs://vtxdemos-vsearch-datasets/homes_listings/df_back.pkl")
app.df3.loc[:, 'id'] = app.df3 .index

origins = [
    "*"
]

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post('/image')
async def image_conversion(file: UploadFile = File(...), text_data: Optional[str] = Form(None)):
  contents = await file.read()
  print(text_data)

  def l2_normalize(vector):
    """Normalizes a vector to unit length using L2 normalization."""
    l2_norm = np.linalg.norm(vector)
    if l2_norm == 0:
      return vector  # Avoid division by zero
    return vector / l2_norm

  def normalize_query(text_data:str, video: bytes):
    e = img_emb_model.get_embeddings(
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
    embeddings = img_emb_model.get_embeddings(video=Video(video_bytes=contents))
    e = embeddings.video_embeddings[0].embedding

  response = combined_index.find_neighbors(
      deployed_index_id = "vs_abnb_deployed_image_text_1",
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

@app.post('/text')
async def image_conversion(text_data: Optional[str] = Form(None)):
  embeddings = img_emb_model.get_embeddings(contextual_text=text_data).text_embedding

  response = text_index.find_neighbors(
      deployed_index_id = "vs_abnb_deployed_text_1",
      queries = [embeddings],
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

@app.post('/image')
async def image_conversion(file: UploadFile = File(...), text_data: Optional[str] = Form(None)):
  contents = await file.read()
  print(contents)

  def l2_normalize(vector):
    """Normalizes a vector to unit length using L2 normalization."""
    l2_norm = np.linalg.norm(vector)
    if l2_norm == 0:
      return vector  # Avoid division by zero
    return vector / l2_norm

  def normalize_query(text_data:str, video: bytes):
    e = img_emb_model.get_embeddings(
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
    embeddings = img_emb_model.get_embeddings(video=Video(video_bytes=contents))
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

@app.post('/mlb')
async def image_conversion(text_data: Optional[str] = Form(None)):
  embeddings = img_emb_model.get_embeddings(contextual_text=text_data).text_embedding

  response = mlb_index.find_neighbors(
      deployed_index_id = "vs_mlb_deployed_v1",
      queries = [embeddings],
      num_neighbors = 10
  )

  print("response finished.")

  nn_list = [int(i.id) for i in response[0]]
  order_df = pd.DataFrame({'id': nn_list})
  merged_df = app.df3.merge(order_df, on='id', how='inner')
  final_df = merged_df.set_index('id').loc[nn_list].reset_index()
  final_df.fillna("value", inplace = True)

  res = final_df.to_json(orient="records")
  parsed = json.loads(res)

  print(final_df["title"].iloc[0])

  return parsed

if __name__ == "__main__":
  uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))