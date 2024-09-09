import asyncio
import pandas as pd
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor
from vertexai.vision_models import MultiModalEmbeddingModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = "vtxdemos"
bq_table = "demos_us.etsy-embeddings-full-2-title"

bq_client = bigquery.Client(project=project_id)
df = bq_client.query(f"SELECT * FROM  `{bq_table}`").to_dataframe()
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
image_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

def vector_search(emb_string: str, embeddings_type):
  sql_query = f"""
  WITH database AS (
    SELECT *,
    {embeddings_type} as embedding
    FROM `vtxdemos.demos_us.etsy-embeddings-full-2-title`
  ),
  text_embedding AS (
    SELECT {emb_string} as embedding
  )
  SELECT
    d.ml_generate_text_llm_result as title,
    d.public_cdn_link,
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

  # print(sql_query)
  df = bq_client.query(sql_query).to_dataframe()
  # print(job)
  # _bq_results = job.result()
  #
  # response = []
  # for n, v in enumerate(_bq_results):
  #   print(v)
  #   val = {
  #       "title": v.title,
  #       "uri": v.public_cdn_link
  #   }
  #   response.append(val)
  return df

async def async_vector_search(input: str):
  with ThreadPoolExecutor() as executor:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, vector_search, input)

def parallel_vector_search(input: str):
  # No need for async here as we're not awaiting anything within this function
  texts = [input]
  inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
  embeddings = text_emb_model.get_embeddings(inputs)[0].values
  text_emb_string = "[" + ",".join(map(str, embeddings)) + "]"

  embeddings = image_emb_model.get_embeddings(
      contextual_text=input,
  ).text_embedding
  image_emb_string = "[" + ",".join(map(str, embeddings)) + "]"

  with ThreadPoolExecutor() as executor:
    df_1 = executor.submit(vector_search, text_emb_string, "text_embedding")
    df_2 = executor.submit(vector_search, image_emb_string, "ml_generate_embedding_result")

    df_1 = df_1.result()
    df_2 = df_2.result()

    # combined_results = pd.concat([df_1, df_2])
    # ranked_df = combined_results.groupby(['title', 'public_cdn_link']).agg({'distance_to_average_review': 'mean'}).reset_index()
    # ranked_df = ranked_df.sort_values('distance_to_average_review')

    # Rename the distance column to distinguish between text and image
    df_1 = df_1.rename(columns={'distance_to_average_review': 'text_distance'})
    df_2 = df_2.rename(columns={'distance_to_average_review': 'image_distance'})

    # Perform an outer join to combine results, handling cases where
    # an item might have only text or image embeddings
    combined_results = pd.merge(df_1, df_2, on=['title', 'public_cdn_link'], how='outer')

    # Fill missing values (in case an item has only one type of embedding)
    combined_results['text_distance'] = combined_results['text_distance'].fillna(1)  # Maximum distance if no text embedding
    combined_results['image_distance'] = combined_results['image_distance'].fillna(1)  # Maximum distance if no image embedding

    # Apply weights (e.g., 70% text, 30% image)
    combined_results['weighted_distance'] = (0.7 * combined_results['text_distance']) + (0.3 * combined_results['image_distance'])

    ranked_df = combined_results.sort_values('weighted_distance')

    print(ranked_df)
    print(ranked_df["public_cdn_link"].iloc[0])

    response = [{"title": row["title"], "uri": row["public_cdn_link"]} for index, row in ranked_df.iterrows()]

    # Wait for both futures to complete and return their results
    return response

def list_items():
  return [{"title": row["ml_generate_text_llm_result"].strip() , "uri": row["public_cdn_link"]} for index, row in df.iterrows()]
