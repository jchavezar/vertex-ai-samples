import json
import numpy as np
import pandas as pd
from google import genai
from google.genai import types
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

project_id = "vtxdemos"
region = "us-central1"
model_id = "gemini-1.5-flash-001"
dataset_uri = "gs://vtxdemos-datasets-public/retail/dataset_backup_final.pkl"
contents = []

# Client Definitions
dataset = pd.read_pickle(dataset_uri)
emb_model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
text_emb_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
gemini_client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region
)

# Gemini Definitions
system_instruction = """
  You are an Etsy customer service representative.  Create 4 responses for each of the following:
  
  Customer service assistant response.
  - questions_cat_1: Two recommended questions answerable using Etsy catalog_metadata provided later.
  - questions_cat_2: Two recommended questions expanding customer curiosity using the selected metadata, requiring a Google search, without looking for similar products, just things you may ask about that product: These questions should prompt a search for information related to the product but not about other similar products. Think about the properties, care, or origin of the materials, construction techniques, or related historical/cultural context that would require external research.
  - questions_cat_3: Two recommended questions about similar products to broaden the customer's search.
  
  Restrictions:
  If user_query has the question, do not suggest the same question.
  Never suggest the same question used before.
  
  """
generate_content_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    response_mime_type = "application/json",
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "answer": {"type": "STRING"},
            "questions_cat_1": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": 2,
                "maxItems": 2
            },
            "questions_cat_2": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": 2,
                "maxItems": 2
            },
            "questions_cat_3": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": 2,
                "maxItems": 2
            }
        },
        "required": ["answer", "questions_cat_1", "questions_cat_2", "questions_cat_3"]
    }
)

# RAG
# Defining Helper Functions
def get_mm_embeddings(thing: str):
  if "gs://" in thing:
    print("processing image embeddings...")
    image = Image.load_from_file(thing)
    image_embeddings = emb_model.get_embeddings(image=image)
    print("done")
    return image_embeddings.image_embedding
  else:
    print("processing text embeddings...")
    text = emb_model.get_embeddings(contextual_text=thing)
    print("done")
    return text.text_embedding

def get_text_embeddings(thing: str):
  print("processing text embeddings...")
  inputs = [TextEmbeddingInput(thing, "RETRIEVAL_DOCUMENT")]
  embeddings = text_emb_model.get_embeddings(inputs)
  print("done")
  return embeddings[0].values

def vector_search(text, top_n=10):
  text_mm_emb = np.array(get_mm_embeddings(text))
  text_emb = np.array(get_text_embeddings(text))

  # Calculate weighted combined similarity directly
  dataset['combined_similarity'] = 0.65 * np.dot(np.stack(dataset['text_embeddings']), text_emb) + 0.25 * np.dot(np.stack(dataset['image_embeddings']), text_mm_emb)

  # Sort and deduplicate
  df_sorted = dataset.sort_values('combined_similarity', ascending=False)
  ranked_results = []
  seen = set()
  for _, row in df_sorted.iterrows():
    item = row['Description'] if not pd.isna(row['Description']) else row['image_public_uri']
    if item not in seen:
      ranked_results.append(row.drop(['text_embeddings', 'image_embeddings', 'combined_similarity']))
      seen.add(item)
      if len(ranked_results) >= top_n:
        break
  return pd.DataFrame(ranked_results)

# Listing all items
def list_items():
  response = []
  for index,row in dataset.iterrows():
    response.append(
        {
            "title": row["title"] or "",
            "gemini_description": row["gemini_description"] or "",
            "subtitle":  row["ProductBrand"] or "",
            "price": row["Price (INR)"] or "",
            "summary":  row["Description"] or "",
            "uri": row["image_public_uri"] or "",
            "content": row["prompt"] or "",
            "description": row["Description"] or "",
            "materials": row["Gender"] or "",
            # "tags": row["tags"] or "",
            # "questions": row["llm_questions"] or ""
        }
    )
  return response

# Chat
def chat_message(text: str, context:str):
  contents.append(
      types.Content(
          role="user",
          parts=[
              types.Part.from_text(text=f"catalog_metadata:\n{context}\n\n user_query:\n{text}")
          ]
      )
  )

  try:
    res = gemini_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=contents,
        config=generate_content_config
    )
    contents.append(
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text=res.text)
            ]
        )
    )
    return json.loads(res.text)
  except Exception as e:
    print(e)
