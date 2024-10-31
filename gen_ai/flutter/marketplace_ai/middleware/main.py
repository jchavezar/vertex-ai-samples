import vertexai
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from google.protobuf.json_format import MessageToDict
from vertexai.generative_models import GenerativeModel
from google.cloud import discoveryengine_v1 as discoveryengine


app = FastAPI()
# vertexai.init(project="vtxdemos", location="us-central1")
#
# system_instruction = """
# I'm building a "You might also like" recommendation system for an Etsy-like marketplace.
#
# A user just clicked on this item:
#
# * **Title:** [Item Title]
# * **Description:** [Item Description]
# * **Category:** [Item Category]
# * **Tags:** [Item Tags]
# * **Materials:** [Item Materials]
# * **Price:** [Item Price]
# * *(Optional) User Implicit Feedback:* [e.g., "User spent a long time viewing images of the item's details."]
#
# Based on this information, generate a search query optimized for finding similar items.  The query should be suitable for a semantic search engine that uses embeddings.  Focus on capturing the item's style, function, target audience, and key features.  Avoid including overly specific details like the exact dimensions or minor color variations.
#
# The generated query should be no longer than [a reasonable length, e.g., 50 words].
# """
# app.model = GenerativeModel(
#     "gemini-1.5-flash-002",
#     system_instruction=[system_instruction]
# )

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

project_id = "vtxdemos"
region = "us-central1"
engine_id = "etsy-100k-v2"
serving_config = f"projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

vertexai.init(project=project_id, location=region)
client = discoveryengine.SearchServiceClient()

@app.get("/healthz")
async def healthz():
  return {"status": "ok"}

@app.post('/vais')
async def retrieve_text(text_data: str = Form(...)):
  request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=text_data,
        page_size=20,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

  response = client.search(request)
  rag = {
      "answers_cat1": [],
      "questions_cat1": [],
      "tags": [],
      "generated_description": [],
      "answers_cat2": [],
      "price_usd": [],
      "category_id": [],
      "attributes": [],
      "category_path": [],
      "image_url": [],
      "title": [],
      "generated_title": [],
      # "combined_text": [],
      "questions_cat2": [],
      # "detailed_description": [],
      "concatenated_product_info": [],
      "listing_id": [],
      "public_cdn_link": [],
      "public_gcs_link": [],
      "private_gcs_link": [],
      "description": [],
      "cat_3_questions": [],
      "questions_only_cat3": [],
      "llm_generated_description": [],
      "generated_rec": [],
  }

  documents = [MessageToDict(result.document._pb) for result in response.results]
  for doc in documents:
    for k, v in doc["structData"].items():
      rag[k].append(v)

  print(rag["llm_generated_description"])
  # with open('../assets/rag_data.json', 'w') as f:
  #   json.dump(rag, f, indent=4)  # Use indent for pretty printing
  return rag

# @app.post('/rec')
# async def retrieve_rec(text_data: str = Form(...)):
#   try:
#     #responses = app.model.generate_content(["Listing Information:\n", text_data])
#
#     request = discoveryengine.SearchRequest(
#         serving_config=serving_config,
#         query=text_data,
#         page_size=20,
#         query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
#             condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
#         ),
#         spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
#             mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
#         ),
#     )
#     response = client.search(request)
#     rag = {
#         "answers_cat1": [],
#         "questions_cat1": [],
#         "tags": [],
#         "generated_description": [],
#         "answers_cat2": [],
#         "price_usd": [],
#         "category_id": [],
#         "attributes": [],
#         "category_path": [],
#         "image_url": [],
#         "title": [],
#         "generated_title": [],
#         # "combined_text": [],
#         "questions_cat2": [],
#         # "detailed_description": [],
#         "concatenated_product_info": [],
#         "listing_id": [],
#         "public_cdn_link": [],
#         "public_gcs_link": [],
#         "private_gcs_link": [],
#         "description": [],
#         "cat_3_questions": [],
#         "questions_only_cat3": [],
#         "generated_rec": [],
#         "llm_generated_description": [],
#     }
#     documents = [MessageToDict(result.document._pb) for result in response.results]
#     for doc in documents:
#       for k, v in doc["structData"].items():
#         rag[k].append(v)
#     return rag
#   except Exception as e:
#     print(e)
#     return None
