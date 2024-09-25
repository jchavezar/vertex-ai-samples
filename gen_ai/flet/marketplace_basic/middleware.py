import json
import time
import asyncio
from typing import Dict
from typing import List

import vertexai
import pandas as pd
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor

from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerationConfig
from vertexai.preview.generative_models import grounding
from vertexai.vision_models import MultiModalEmbeddingModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.preview.generative_models import GenerativeModel, Part, Tool

project_id = "vtxdemos"
bq_table = "demos_us.etsy-embeddings-full-latest"
bq_table = "vtxdemos.demos_us.etsy-10k-full"
region = "us-east1"
model_id = "gemini-1.5-flash-001"

bq_client = bigquery.Client(project=project_id)
df = bq_client.query(f"SELECT * EXCEPT(text_embedding, ml_generate_embedding_result) FROM  `{bq_table}`").to_dataframe()
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
image_emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

fv_multi = feature_store.FeatureView(name="projects/254356041555/locations/us-east1/featureOnlineStores/feature_store_marketplace/featureViews/etsy_view_image1")
fv_text = feature_store.FeatureView(name="projects/254356041555/locations/us-east1/featureOnlineStores/feature_store_marketplace/featureViews/etsy_view_text1")

vertexai.init(project=project_id, location=region)
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=grounding.GoogleSearchRetrieval()
    ),
]


system_instruction="""
**You are Chatsy, a friendly and helpful assistant for Etsy customers.** Your primary goal is to provide satisfying answers based on the specific context of their questions. 

**Tasks:**
1. **Respond:** 
    * **Provide the answer:** Use ONLY the appropriate source local_context_rag to give a concise, accurate response. 

**Rules:**
* **Be friendly and casual:** Write like you're chatting with a friend, no need for formal explanations. 
* **Honesty is key:** If you don't know the answer based on the available information, say so politely and suggest potentially relevant questions the user might want to ask. 
* **Smart and Intelligent:** Sound natural and smart, do not mention things like "according the listing" just if you have been asked for.
* **Truly Grounded:** Do not answer any other question is not part of your context or local data.

**Output format:**
Plain Text
"""

grounded_system_instruction = """
You might be asked for something regarding the image/picture/frame, if thats the case use <image_file> and create
a quick description then use that as a context for your grounding and respond the question.
"""

requery_instructions = """
By using both the Context and the Question do as follows.
        Tasks:
        * **summary_text:** Summarize the context and the question into a concise summary.
        * **concise_text:** From the summary, create a new text perfect to match with other summary listings.

        Rules:
        Only 1 text as output.
"""

model = GenerativeModel(
    model_id,
    #tools=tools,
    system_instruction=[system_instruction]
)
chat = model.start_chat()

grounded_model = GenerativeModel(
    model_id,
    tools=tools,
    system_instruction=[grounded_system_instruction]
)

requery_model = GenerativeModel(
    model_id,
    system_instruction=[requery_instructions]
)

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
def vector_search(prompt: str, multimodal=True):
  if multimodal:
    embeddings = image_emb_model.get_embeddings(
        contextual_text=prompt,
    ).text_embedding

    r = fv_multi.search(
        embedding_value = embeddings,
        neighbor_count = 6,
        approximate_neighbor_candidates=16,
        leaf_nodes_search_fraction=1.0,
        return_full_entity=True,  # returning entities with metadata
    ).to_dict()
    df = response_process(r, multimodal)

  else:
    texts = [prompt]
    inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
    embeddings = text_emb_model.get_embeddings(inputs)[0].values

    r = fv_text.search(
        embedding_value = embeddings,
        neighbor_count = 6,
        approximate_neighbor_candidates=16,
        leaf_nodes_search_fraction=1.0,
        return_full_entity=True,  # returning entities with metadata
    ).to_dict()
    df = response_process(r, multimodal)
  return df

async def async_vector_search(input: str):
  with ThreadPoolExecutor() as executor:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, vector_search, input)

# RAG
def parallel_vector_search(input: str):
  start_time = time.time()
  with ThreadPoolExecutor() as executor:
    start_time=time.time()
    df_1 = executor.submit(vector_search, prompt=input, multimodal=True)
    df_2 = executor.submit(vector_search, prompt=input, multimodal=False)

    df_1 = df_1.result()
    df_2 = df_2.result()

    # Rename the distance column to distinguish between text and image
    df_1 = df_1.rename(columns={'distance_to_average_review': 'text_distance'})
    df_2 = df_2.rename(columns={'distance_to_average_review': 'image_distance'})
    # df_1['questions_cat1'] = df_1['questions_cat1'].apply(json.dumps)
    # df_2['questions_cat1'] = df_2['questions_cat1'].apply(json.dumps)

    # Perform an outer join to combine results, handling cases where
    combined_results = pd.merge(df_1, df_2, on=[
        'title',
        'price_usd',
        'public_cdn_link',
        'private_gcs_link',
        'content',
        'description',
        'materials',
        'tags',
        'llm_title',
        'summary',
        'questions_cat1',
        'answers_cat1',
        'questions_cat2',
        'answers_cat2',
        'textual_questions',
        'textual_answers',
        'visual_questions',
        'visual_answers',
        'textual_tile',
        'textual_image_uri',
        'visual_tile',
        'visual_image_uri'
    ], how='outer')

    # Fill missing values (in case an row has only one type of embedding)
    combined_results['text_distance'] = combined_results['text_distance'].fillna(-1000)  # Large negative value if no text embedding
    combined_results['image_distance'] = combined_results['image_distance'].fillna(-1000)  # Large negative value if no image embedding

    # Apply weights (e.g., 70% text, 30% image)
    combined_results['weighted_distance'] = (0.5 * abs(combined_results['text_distance'])) + (0.5 * abs(combined_results['image_distance']))

    ranked_df = combined_results.sort_values('weighted_distance')


    response = [
        {
            "title": row["llm_title"],
            "subtitle":  row["title"],
            "price": row["price_usd"],
            "summary":  row["summary"],
            "uri": row["public_cdn_link"],
            "private_uri": row["private_gcs_link"],
            "content": row["content"],
            "description": row["description"],
            "materials": row["materials"],
            "tags": row["tags"],
            #"questions": row["llm_questions"], # to be removed
            "questions_cat1": row["answers_cat1"],
            "answers_cat1": row["questions_cat1"],
            "questions_cat2": row["answers_cat2"],
            "answers_cat2": row["questions_cat2"],
            "textual_questions": row["textual_questions"],
            "textual_answers": row["textual_answers"],
            "visual_questions": row["visual_questions"],
            "visual_answers": row["visual_answers"],
            "textual_tile": row["textual_tile"],
            "textual_image_uri": row["textual_image_uri"],
            "visual_tile": row["visual_tile"],
            "visual_image_uri": row["visual_image_uri"],
        } for index, row in ranked_df.iterrows()]

    print(time.time()-start_time)
    # Wait for both futures to complete and return their results
    return response

def list_items():
  response = []
  for index,row in df.iterrows():
    response.append(
        {
            "private_uri": row.get("private_uri", ""),  # Handle potential missing key
            "title": row["llm_title"],
            "subtitle": row["title"],
            "price": row["price_usd"],
            "summary": row["summary"],
            "description": row["description"],
            "materials": row["materials"],
            "uri": row["public_cdn_link"],
            "content": row["content"],
            "questions_cat1": row["questions_cat1"],
            "answers_cat1": row["answers_cat1"],
            "questions_cat2": row["questions_cat1"],
            "answers_cat2": row["answers_cat2"],
            "textual_questions": row["textual_questions"],
            "textual_answers": row["textual_answers"],
            "visual_questions": row["visual_questions"],
            "visual_answers": row["visual_answers"],
            "textual_tile": row["textual_tile"],
            "textual_image_uri": row["textual_image_uri"],
            "visual_tile": row["visual_tile"],
            "visual_image_uri": row["visual_image_uri"]
         }
    )
  return response, df

def gemini_chat(data: Dict, context: str, image_uri: str, questions: List):

  user_query = data["question"]

  if data["type"] == "questions_category_1":
    print("cat1")
    prompt = f"""
    local_context_rag:
    {context}
    
    preloaded_questions:
    {questions}
    
    User/Customer prompt/Question:
    {user_query}
    """

    # image = Part.from_uri(image_uri, "image/jpg")
    _ = chat.send_message([prompt, "\n\nResponse: "])
    res = _.text
  elif data["type"] == "questions_category_2":
    print("cat2")
    gem_res = grounded_model.generate_content(f"Query: {user_query}\nAnswer:")
    res = gem_res.text
  else:
    print("cat3")
    _pre_re = requery_model.generate_content([f"Context:\n{context}\nQuestion:\n{user_query}\nResponse (concise_text only) as plain text:"])
    pre_re = _pre_re.text
    re = parallel_vector_search(pre_re)

    _ = chat.send_message([f"Use the following new findings to answer this question: {user_query},\n Findings (new context):\n{str(re)}"])
    res = _.text
  return res

