import json
import base64
import vertexai
import time
from typing import Dict
from variables import *
from google.cloud import storage, bigquery
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, \
  FinishReason
import vertexai.preview.generative_models as generative_models

vertexai.init(project=project_id, location=location)
storage_client = storage.Client(project=project_id)
bq_client = bigquery.Client(project=project_id)
mm_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

system_instruction = """You are an auction agent analysit, your missions is to find inconsistencies in the fill form for customer submiting their item.

There are different items like:
      - fine_arts
      - watches
      - collectibles
      - dinasours
      - jowels

Rules: 
Take the input text and validate it against the image if the input is not related with the image then discard.

Output in Json:
{
  \"item\": <description of item from input text>,
  \"image\": <description of the image>,
  \"related\": <True/False>
}"""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json"
}

model = GenerativeModel(
    model_id,
    system_instruction=[system_instruction]
)


def llm(input_text: Dict, image="gs://vtxdemos-auction/mona.jpeg"):
  if "gs:" in image:
    img = Part.from_uri(uri=image, mime_type="image/jpeg")
  else:
    img = Part.from_data(image, mime_type="image/jpeg")
    print(img)

  prompt = f'''
  input_text:
    item_name={input_text["item_name"]}
    country_ori_name={input_text["country_ori_name"]}
    artist_name={input_text["artist_name"]}
    title_work_name={input_text["title_work_name"]}
  image:
  {img}
  '''
  response = model.generate_content(
      [prompt],
      generation_config=generation_config,
  )
  return response.text


def vector_search(input_text: str):
  start_time = time.time()
  sql_query = f'''
    WITH database AS (
        SELECT gcs_uri as content, embedding FROM `demos_us.auction_items`
    ),
    text_embedding AS (
        SELECT ml_generate_embedding_result as embedding
        FROM
            ML.GENERATE_EMBEDDING(
                MODEL `demos_us.multimodalembedding`,
                (SELECT "{input_text}" AS content)
            )
    )
    SELECT
        d.content,
        ML.DISTANCE(
            te.embedding,
            d.embedding,
            'COSINE'
        ) AS distance_to_average_review
    FROM
        database d, text_embedding te
    ORDER BY distance_to_average_review;
  '''
  print(sql_query)
  job = bq_client.query(sql_query)
  _bq_results = job.result()

  response = {}
  for n, v in enumerate(_bq_results):
    response[f"image_{n}"] = v.content.replace("gs:/",
                                               "https://storage.googleapis.com")
  print(f"Response Time: {time.time() - start_time}")

  return response

def vector_search_images(image):
  start_time = time.time()
  with open(image, "rb") as f:
    image_data = f.read()
    img = Image(image_data)
    emb = mm_emb_model.get_embeddings(image=img).image_embedding
    emb_string = "[" + ",".join(map(str, emb)) + "]"

  sql_query = f"""
      WITH database AS (
          SELECT gcs_uri as content, embedding FROM `demos_us.auction_items`
      ),
      text_embedding AS (
          SELECT {emb_string} as embedding  # Removed double quotes here
      )
      SELECT
          d.content,
          ML.DISTANCE(
              te.embedding,
              d.embedding,
              'COSINE'
          ) AS distance_to_average_review
      FROM
          database d, text_embedding te
      ORDER BY distance_to_average_review;
  
  """

  job = bq_client.query(sql_query)
  _bq_results = job.result()

  response = {}
  for n, v in enumerate(_bq_results):
    response[f"image_{n}"] = v.content.replace("gs:/",
                                               "https://storage.googleapis.com")
  print(f"Response Time: {time.time() - start_time}")
  return response