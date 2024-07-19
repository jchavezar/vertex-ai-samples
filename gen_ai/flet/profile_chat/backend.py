#%%
import json
import base64
import vertexai
import numpy as np
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

project_id = "vtxdemos"
model_id= "gemini-1.5-flash-001"
bucket_id = "vtxdemos-vsearch-datasets"
bucket_folder = "profile_synthetic_data"

vertexai.init(project=project_id, location="us-central1")
model = GenerativeModel(
    model_id,
)
chat = model.start_chat()

# Store in GCS

client = storage.Client()
bucket = client.get_bucket(bucket_id)
blob = bucket.get_blob(f"{bucket_folder}/dataset.json")
blob_content = blob.download_as_string()
dataset_dict = json.loads(blob_content)

description = []
for i in dataset_dict:
  try:
    description.append(i["description"])
  except:
    continue

def multiturn_generate_content(text: str):
  context = f"""
  The following is a context you can use for answer questions about user profile in general:
  <context>
  {description}
  </context>
  
  <chat>
  """
  return chat.send_message(
      [context,text]
  ).text