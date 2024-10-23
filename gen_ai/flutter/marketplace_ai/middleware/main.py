import json

import vertexai
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from google.protobuf.json_format import MessageToDict
from fastapi import FastAPI, Request, UploadFile, File, Form
from google.cloud import discoveryengine_v1 as discoveryengine

app = FastAPI()

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
engine_id = "etsy-10k-v2_1729686705897"
serving_config = f"projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

vertexai.init(project=project_id, location=region)
client = discoveryengine.SearchServiceClient()

@app.post('/vais')
async def retrieve_text(text_data: str = Form(...)):
  print("vais")
  print(text_data)
  print(type(text_data))
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
      "a_cat_1": [],
      "q_cat_1": [],
      "tags": [],
      "generated_description": [],
      "a_cat_2": [],
      "price_usd": [],
      "category_id": [],
      "attributes": [],
      "category_path": [],
      "image_url": [],
      "title": [],
      "generated_title": [],
      "combined_text": [],
      "q_cat_2": [],
      "detailed_description": [],
      "listing_id": [],
      "public_cdn_link": [],
      "public_gcs_link": [],
      "private_gcs_link": [],
      "description": [],
      "cat_3_questions": [],
      "questions_only_cat3": [],
  }

  documents = [MessageToDict(result.document._pb) for result in response.results]
  for doc in documents:
    for k, v in doc["structData"].items():
      rag[k].append(v)
  print(rag["q_cat_1"][0])
  print(rag["questions_only_cat3"][0])

  # with open('../assets/rag_data.json', 'w') as f:
  #   json.dump(rag, f, indent=4)  # Use indent for pretty printing
  return rag

