import time
import asyncio
from typing import List

import vertexai
import pandas as pd
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor
from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerativeModel
from vertexai.vision_models import MultiModalEmbeddingModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = "vtxdemos"
bq_table = "demos_us.etsy-embeddings-full-latest"
region = "us-central1"
model_id = "gemini-1.5-flash-001"

bq_client = bigquery.Client(project=project_id)
df = bq_client.query(f"SELECT * EXCEPT(text_embedding, ml_generate_embedding_result) FROM  `{bq_table}`").to_dataframe()
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
image_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

fv_multi = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_multimodal_emb")
fv_text = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_text_emb")

vertexai.init(project=project_id, location=region)
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json"
}
model = GenerativeModel(
    model_id,
    system_instruction=["""
    Your name is EtsyMate a mate for any Etsy's customer, you are a very friendly and capable agent which priority
    is to satisfy customer answers based on specific context.
    
    If the questions is related to the listing, use context only to answer the question, do not make up if you do not you gently say so.
    
    In the prompt you will receive possible questions to ask, because you need to recommend more questions after answer without repeating.
    
    Rules:
    Do not repeat questions.
    Always keep 4 questions.
    
    Output in JSON:
    {
      "response": <your response>,
      "questions_to_task": <a list of a new questions to ask related to the last question if the query/prompt is not related to the product leave it empty>
    }
    
    """]
)
chat = model.start_chat()

def response_process(result, multimodal: bool):
  neighbors = result["neighbors"]

  all_extracted_data = []
  for row in neighbors:
    extracted_data = {}
    if multimodal:
      extracted_data['image_distance'] = row['distance']  # Extract distance
    else:
      extracted_data['text_distance'] = row['distance']  # Extract distance

    for feature in row['entity_key_values']['key_values']['features']:
      name = feature['name']
      if name not in ['ml_generate_embedding_result', 'text_embedding']:
        if 'value' in feature:
          for value_type, value in feature['value'].items():
            extracted_data[name] = value
        else:
          extracted_data[name] = "no values"

    all_extracted_data.append(extracted_data)

  dataframe = pd.DataFrame(all_extracted_data)

  return dataframe

def vector_search(prompt: str, multimodal=True):
  if multimodal:
    embeddings = image_emb_model.get_embeddings(
        contextual_text=prompt,
    ).text_embedding

    r = fv_multi.search(
        embedding_value = embeddings,
        neighbor_count = 5,
        return_full_entity=True,  # returning entities with metadata
    ).to_dict()
    df = response_process(r, multimodal)

  else:
    texts = [prompt]
    inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
    embeddings = text_emb_model.get_embeddings(inputs)[0].values

    r = fv_text.search(
        embedding_value = embeddings,
        neighbor_count = 5,
        return_full_entity=True,  # returning entities with metadata
    ).to_dict()
    df = response_process(r, multimodal)
  return df

async def async_vector_search(input: str):
  with ThreadPoolExecutor() as executor:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, vector_search, input)

def parallel_vector_search(input: str):
  # No need for async here as we're not awaiting anything within this function
  # start_time = time.time()
  # texts = [input]
  # inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
  # embeddings = text_emb_model.get_embeddings(inputs)[0].values
  # text_emb_string = "[" + ",".join(map(str, embeddings)) + "]"
  #
  # embeddings = image_emb_model.get_embeddings(
  #     contextual_text=input,
  # ).text_embedding
  # image_emb_string = "[" + ",".join(map(str, embeddings)) + "]"

  with ThreadPoolExecutor() as executor:
    start_time=time.time()
    df_1 = executor.submit(vector_search, prompt=input, multimodal=True)
    df_2 = executor.submit(vector_search, prompt=input, multimodal=False)

    df_1 = df_1.result()
    df_2 = df_2.result()

    # Rename the distance column to distinguish between text and image
    df_1 = df_1.rename(columns={'distance_to_average_review': 'text_distance'})
    df_2 = df_2.rename(columns={'distance_to_average_review': 'image_distance'})

    # Perform an outer join to combine results, handling cases where
    # an row might have only text or image embeddings
    combined_results = pd.merge(df_1, df_2, on=['title', 'public_cdn_link', 'content', 'description', 'materials', 'llm_questions', 'tags', 'llm_title', "summary"], how='outer')

    # Fill missing values (in case an row has only one type of embedding)
    # combined_results['text_distance'] = combined_results['text_distance'].fillna(1)  # Maximum distance if no text embedding
    # combined_results['image_distance'] = combined_results['image_distance'].fillna(1)  # Maximum distance if no image embedding
    combined_results['text_distance'] = combined_results['text_distance'].fillna(-1000)  # Large negative value if no text embedding
    combined_results['image_distance'] = combined_results['image_distance'].fillna(-1000)  # Large negative value if no image embedding

    # Apply weights (e.g., 70% text, 30% image)
    # combined_results['weighted_distance'] = (0.7 * combined_results['text_distance']) + (0.3 * combined_results['image_distance'])
    combined_results['weighted_distance'] = (0.7 * abs(combined_results['text_distance'])) + (0.3 * abs(combined_results['image_distance']))

    ranked_df = combined_results.sort_values('weighted_distance')
    print(time.time()-start_time)

    response = [
        {
            "title": row["llm_title"],
            "subtitle":  row["title"],
            "summary":  row["summary"],
            "uri": row["public_cdn_link"],
            "content": row["content"],
            "description": row["description"],
            "materials": row["materials"],
            "tags": row["tags"],
            "questions": row["llm_questions"]
        } for index, row in ranked_df.iterrows()]

    # Wait for both futures to complete and return their results
    return response

def list_items():
  response = []
  for index,row in df.iterrows():
    # print(row["uri"])
    # print(row["llm_title"])
    # print(row["summary"])
    # print(row["public_cdn_link"])
    # print(row["content"])
    # print(row["description"])
    # print(row["materials"])
    # print(row["tags"])
    # print(row["llm_questions"])
    # print(type(row["uri"]))
    # print(type(row["llm_title"]))
    # print(type(row["summary"]))
    # print(type(row["public_cdn_link"]))
    # print(type(row["content"]))
    # print(type(row["description"]))
    # print(type(row["materials"]))
    # print(type(row["tags"]))
    # print(type(row["llm_questions"]))
    response.append(
        {
            "title": row["llm_title"] or "",
            "subtitle":  row["title"] or "",
            "summary":  row["summary"] or "",
            "uri": row["public_cdn_link"] or "",
            "content": row["content"] or "",
            "description": row["description"] or "",
            "materials": row["materials"] or "",
            "tags": row["tags"] or "",
            "questions": row["llm_questions"] or ""
        }
    )
  return response

def gemini_chat(prompt: str, context: str, questions: List):

  prompt = f"""
  Context:
  {context}
  
  Questions to ask:
  {questions}
    
  User/Customer prompt/Question:
  {prompt}
  """

  re = chat.send_message([prompt], generation_config=generation_config)
  return re.text
