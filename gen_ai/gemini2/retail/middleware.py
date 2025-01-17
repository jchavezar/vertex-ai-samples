import json
import time
import asyncio
from typing import List

import numpy as np
import vertexai
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor

from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerationConfig
from vertexai.preview.generative_models import grounding
from vertexai.vision_models import MultiModalEmbeddingModel
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from vertexai.preview.generative_models import GenerativeModel, Part, Tool

project_id = "vtxdemos"
bq_table = "demos_us.etsy-embeddings-full-latest"
bq_table = "demos_us.etsy-embeddings-full-version1-title"
region = "us-central1"
model_id = "gemini-1.5-flash-001"
dataset_uri = "gs://vtxdemos-datasets-public/retail/dataset_backup_final.pkl"

dataset = pd.read_pickle(dataset_uri)
# bq_client = bigquery.Client(project=project_id)
# df = bq_client.query(f"SELECT * EXCEPT(text_embedding, ml_generate_embedding_result) FROM  `{bq_table}`").to_dataframe()
emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
# text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
# image_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

# fv_multi = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_multimodal_embe_version1")
# fv_text = feature_store.FeatureView(name="projects/254356041555/locations/us-central1/featureOnlineStores/fs_etsy/featureViews/fs_etsy_view_text_emb_version1")

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
        "answer": {"type": "string"},
        "questions_to_ask": {
            "type": "object",
            "properties": {
                "category_1": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "category_2": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "category_3": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "category_picked": {
            "type": "object",
            "properties": {
                "local_context_rag": {
                    "type": "boolean",
                },
                "google_search_ground": {
                    "type": "boolean",
                },
                "similar_products_rag": {
                    "type": "boolean",
                }
            }
        }
    }
}

tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=grounding.GoogleSearchRetrieval()
    ),
]

output_json = """
    Output in JSON:
    {
      "response": <your response>,
      "questions_to_task": <a list of a new questions to ask related to the last question if the query/prompt is not related to the product leave it empty>
    }
"""

system_instruction="""
**You are Chatsy, a friendly and helpful assistant for Etsy customers.** Your primary goal is to provide satisfying answers based on the specific context of their questions. 

**Tasks:**

1. **Categorize:** Analyze each user question and determine if it's best answered using:
    * **local_context_rag:** Information from the current listing or Etsy's internal data (title, description, materials, tags, etc.).
    * **google_search_ground:**  Broader knowledge found on the internet, related to the product but beyond the explicit listing details. 
      Think about potential applications, material properties, comparisons to similar items, usage scenarios, care instructions, or historical/cultural context.
      These questions should pique the customer's interest and encourage them to explore the product further.
    * **similar_products_rag:** Information from similar products or Etsy's internal data (title, description, materials, tags, etc.).

2. **Respond:** 
    * **Provide the answer:** Use ONLY the appropriate source (local_context_rag or google_search_ground, similar_products_rag) to give a concise, accurate response. 
    * **Suggest further questions:**  Offer 2 additional questions per each category (local_context_rag and google_search_ground, similar_products_rag) that the **user might want to ask** related to the topic or listing. 
    * **Provide the category you picked:** Indicate whether you used "local_context_rag", "google_search_ground" or "similar_products_rag" to answer the question.

**Rules:**
* **Be friendly and casual:** Write like you're chatting with a friend, no need for formal explanations. 
* **Honesty is key:** If you don't know the answer based on the available information, say so politely and suggest potentially relevant questions the user might want to ask. 
* **Question management:** 
    * Start with the preloaded questions (if any).
    * After answering a question, remove it from the list.
    * Generate 2 NEW questions (per each category) that the user might find helpful.
    * Base new questions on the context of the conversation and the product information.
* **Smart and Intelligent:** Sound natural and smart, do not mention things like "according the listing" just if you have been asked for.

**Extra reasoning thoughts:**
* **Category Selection Accuracy:** If you recommend questions under category 2 and your next iteration you get that question you should follow categorization as it is; in this case google_search_ground.
The same applies for the other categories.
"""

grounded_system_instruction = """
You might be asked for something regarding the image/picture/frame, if thats the case use <image_file> and create
a quick description then use that as a context for your grounding and respond the question.
"""

model = GenerativeModel(
    model_id,
    #tools=tools,
    system_instruction=[system_instruction]
)
grounded_model = GenerativeModel(
    model_id,
    tools=tools,
    system_instruction=[grounded_system_instruction]
)
chat = model.start_chat()

# RAG
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

# RAG
def vector_search(text, top_n=10):
  t_emb = emb_model.get_embeddings(contextual_text=text).text_embedding
  query_embedding = np.array(t_emb)
  print(query_embedding)
  # Calculate similarities and combine using .loc
  dataset.loc[:, 'text_similarity'] = dataset['text_embeddings'].apply(
      lambda x: cosine_similarity(x.reshape(1, -1), query_embedding.reshape(1, -1))[0][0]
  )
  dataset.loc[:, 'image_similarity'] = dataset['image_embeddings'].apply(
      lambda x: cosine_similarity(x.reshape(1, -1), query_embedding.reshape(1, -1))[0][0]
  )
  dataset.loc[:, 'combined_similarity'] = dataset['text_similarity'] + dataset['image_similarity']
  dataset.sort_values('combined_similarity', ascending=False, inplace=True)

  # Deduplicate and build results
  ranked_results = []
  added_items = set()
  for index, row in dataset.iterrows():
    item = row['Description'] if not pd.isna(row['Description']) else row['image_public_uri']
    if item not in added_items:
      ranked_results.append(row.drop(['text_embeddings', 'image_embeddings', 'text_similarity', 'image_similarity', 'combined_similarity']))
      added_items.add(item)

    if len(ranked_results) >= top_n:
      break
  print(pd.DataFrame(ranked_results)["image_public_uri"].iloc[0])
  return pd.DataFrame(ranked_results)

# def list_items():
#   response = []
#   for index,row in df.iterrows():
#     response.append(
#         {
#             "title": row["llm_title"] or "",
#             "subtitle":  row["title"] or "",
#             "price": row["price_usd"] or "",
#             "summary":  row["summary"] or "",
#             "uri": row["public_cdn_link"] or "",
#             "content": row["content"] or "",
#             "description": row["description"] or "",
#             "materials": row["materials"] or "",
#             "tags": row["tags"] or "",
#             "questions": row["llm_questions"] or ""
#         }
#     )
#   return response

def gemini_chat(user_query: str, context: str, image_uri: str, questions: List):

  prompt = f"""
  local_context_rag:
  {context}
  
  preloaded_questions:
  {questions}
  
  User/Customer prompt/Question:
  {user_query}
  """

  image = Part.from_uri(image_uri, "image/jpg")
  _ = chat.send_message([prompt, "Image of listing: ", image, "\n\nResponse: "], generation_config=GenerationConfig(response_mime_type="application/json", response_schema=response_schema))
  res = json.loads(_.text)
  print(res)
  if res["category_picked"]["local_context_rag"]:
    return res
  elif res["category_picked"]["google_search_ground"]:
    gem_res = grounded_model.generate_content(f"Query: {user_query}\nOptional Image: <image_file>{image}\nAnswer:")
    _ = chat.send_message([f"Google Grounded Data:\n{gem_res.text}\n",prompt, "Image of listing: ", image, "\n\nResponse: "], generation_config=GenerationConfig(response_mime_type="application/json", response_schema=response_schema))
    res = json.loads(_.text)
    return res

