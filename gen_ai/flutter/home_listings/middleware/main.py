import os
import json
import base64
import vertexai
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from vertexai.vision_models import MultiModalEmbeddingModel, Image, Video
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = os.environ["PROJECT_ID"]
region = "us-central1"
combined_index_endpoint = os.environ["COMBINED_INDEX_ENDPOINT"]
combined_index_id = os.environ["COMBINED_INDEX_ID"]
text_index_endpoint = os.environ["TEXT_INDEX_ENDPOINT"]
text_index_id = os.environ["TEXT_INDEX_ID"]
datastore_bucket = os.environ["DATASET_BUCKET"]

vertexai.init(project=project_id, location=region)

img_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# Vector Search
combined_index = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=combined_index_endpoint,
)

text_index = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=text_index_endpoint
)

app = FastAPI()

app.df = pd.read_csv(f"gs://{datastore_bucket}/dataset/data.csv")

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


@app.post('/text')
async def image_conversion(text_data: Optional[str] = Form(None)):
  embeddings = img_emb_model.get_embeddings(
      contextual_text=text_data).text_embedding

  text_response = text_index.find_neighbors(
      deployed_index_id=text_index_id,
      queries=[embeddings],
      num_neighbors=10
  )

  nn_list = [int(i.id) for i in text_response[0]]
  order_df = pd.DataFrame({'id': nn_list})
  merged_df = app.df.merge(order_df, on='id', how='inner')
  final_df = merged_df.set_index('id').loc[nn_list].reset_index()
  final_df.fillna("value", inplace=True)

  res = final_df.to_json(orient="records")
  parsed = json.loads(res)
  return parsed


@app.post('/image')
async def image_conversion(file: UploadFile = File(...),
    text_data: Optional[str] = Form(None)):
  contents = await file.read()

  def l2_normalize(vector):
    """Normalizes a vector to unit length using L2 normalization."""
    l2_norm = np.linalg.norm(vector)
    if l2_norm == 0:
      return vector  # Avoid division by zero
    return vector / l2_norm

  def normalize_query(text_data: str, video: bytes):
    e = img_emb_model.get_embeddings(
        video=Video(
            video_bytes=video
        ),
        contextual_text=text_data,
    )
    normalized_video_embedding = l2_normalize(e.video_embeddings[0].embedding)
    normalized_text_embedding = l2_normalize(e.text_embedding)
    we_ave = (0.7 * normalized_video_embedding) + (
        0.3 * normalized_text_embedding)
    return we_ave

  if text_data:
    e = normalize_query(text_data, contents)

  else:
    embeddings = img_emb_model.get_embeddings(video=Video(video_bytes=contents))
    e = embeddings.video_embeddings[0].embedding

  combined_response = combined_index.find_neighbors(
      deployed_index_id=combined_index_id,
      queries=[e],
      num_neighbors=10
  )

  nn_list = [int(i.id) for i in combined_response[0]]
  order_df = pd.DataFrame({'id': nn_list})
  merged_df = app.df.merge(order_df, on='id', how='inner')
  final_df = merged_df.set_index('id').loc[nn_list].reset_index()
  final_df.fillna("value", inplace=True)

  res = final_df.to_json(orient="records")
  parsed = json.loads(res)

  return parsed


if __name__ == "__main__":
  uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
