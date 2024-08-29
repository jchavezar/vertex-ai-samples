#%%
import time
import requests
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import Part

from variables import *
from google.cloud import bigquery
from vertexai.vision_models import Image as Img, MultiModalEmbeddingModel

# Variables (project_id, location, etc) are in variables.py

bq_client = bigquery.Client(project=project_id)
emb_model = MultiModalEmbeddingModel.from_pretrained(multimodal_model_id)

# Preload listing
sql_query = "SELECT * FROM `vtxdemos.demo_us_outputs.videos_emeddings_end_081624`"
job = bq_client.query(sql_query)
listing_results = job.result()

# Gemini
vertexai.init(project=project_id)
model = GenerativeModel(
    "gemini-1.5-pro-001",
)

def llm(prompt: str, video: str):
  response = requests.get(video)
  vid = Part.from_data(data=response.content, mime_type="video/mp4")
  response = model.generate_content(
      [prompt, vid],
  )
  return response.text

# Eng Gemini

def vector_search_images(prompt: str):
  start_time = time.time()
  emb = emb_model.get_embeddings(
      contextual_text=prompt
  ).text_embedding
  emb_string = "[" + ",".join(map(str, emb)) + "]"

  sql_query = f"""
      WITH database AS (
          SELECT
          title,
          uri as content,
          public_uri,
          thumbnails_uri,
          ml_generate_embedding_result as embedding, 
          ml_generate_embedding_start_sec as start_second,
          ml_generate_embedding_end_sec as end_second,
          ml_generate_text_llm_result_x as summary,
          ml_generate_text_llm_result_y as analytics
          FROM `vtxdemos.demo_us_outputs.videos_emeddings_end_081624`
      ),
      text_embedding AS (
          SELECT {emb_string} as embedding 
      )
      SELECT
          d.title,
          d.summary,
          d.analytics,
          d.content,
          d.public_uri,
          d.thumbnails_uri,
          d.start_second,
          d.end_second,
          ML.DISTANCE(
              te.embedding,
              d.embedding,
              'COSINE'
          ) AS distance_to_average_review
      FROM
          database d, text_embedding te
      ORDER BY distance_to_average_review
      LIMIT 15
      ;
  
  """

  job = bq_client.query(sql_query)
  _bq_results = job.result()

  response = {}
  for n, v in enumerate(_bq_results):
    val = {
        "title": v.title,
        "summary": v.summary,
        "analytics": v.analytics,
        "uri": v.public_uri,
        "thumbnails_uri": v.thumbnails_uri,
        "start_sec": v.start_second,
        "end_sec": v.end_second
    }
    response[f"image_{n}"] = val

  print(val["summary"])

  print(f"Response Time: {time.time() - start_time}")
  return response