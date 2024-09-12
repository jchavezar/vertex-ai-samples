import time
import asyncio
from typing import List

import vertexai
import pandas as pd
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor

from vertexai.generative_models import GenerationConfig
from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerativeModel, Part
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

fv_multi = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_multimodal_embe_version1")
fv_text = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_text_emb_version1")

vertexai.init(project=project_id, location=region)
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json"
}

response_schema = {
    "type": "object",
    "properties": {
        "response": {"type": "string"},
        "questions_to_ask": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

output_json = """
    Output in JSON:
    {
      "response": <your response>,
      "questions_to_task": <a list of a new questions to ask related to the last question if the query/prompt is not related to the product leave it empty>
    }
"""

model = GenerativeModel(
    model_id,
    system_instruction=["""
    Your name is EtsyMate a mate for any Etsy's customer, you are a very friendly and capable agent which priority
    is to satisfy customer answers based on specific context.
    
    Rules:
    Respond friendly and naturally, there is no reason to explain your answer, you need to sell!
    If the questions are related to the listing, use context only to answer the question, do not make up if you do not you gently say so.
    There are preloaded questions which was previously recommended by the system, discard the used question and keep the others, try to generate new questions based on your response.
    Always keep 4 questions.
    
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
    combined_results = pd.merge(df_1, df_2, on=['title', 'public_cdn_link', 'private_gcs_link', 'content', 'description', 'materials', 'llm_questions', 'tags', 'llm_title', "summary"], how='outer')

    # Fill missing values (in case an row has only one type of embedding)
    combined_results['text_distance'] = combined_results['text_distance'].fillna(-1000)  # Large negative value if no text embedding
    combined_results['image_distance'] = combined_results['image_distance'].fillna(-1000)  # Large negative value if no image embedding

    # Apply weights (e.g., 70% text, 30% image)
    combined_results['weighted_distance'] = (0.7 * abs(combined_results['text_distance'])) + (0.3 * abs(combined_results['image_distance']))

    ranked_df = combined_results.sort_values('weighted_distance')
    print(time.time()-start_time)

    response = [
        {
            "title": row["llm_title"],
            "subtitle":  row["title"],
            "summary":  row["summary"],
            "uri": row["public_cdn_link"],
            "private_uri": row["private_gcs_link"],
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

def gemini_chat(prompt: str, context: str, image_uri: str, questions: List):

  prompt = f"""
  Context:
  {context}
  
  Preloaded Questions:
  {questions}
  
  User/Customer prompt/Question:
  {prompt}
  """
  image = Part.from_uri(image_uri, "image/jpg")
  re = chat.send_message([prompt, "Image of listing: ", image], generation_config=GenerationConfig(response_mime_type="application/json", response_schema=response_schema))
  return re.text
