# %%
import json
import vertexai
from variables import *
from process_doc import process_document_sample
from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

# %%
vertexai.init(project=project_id, location=region)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

chat_model = GenerativeModel(
    "gemini-1.5-flash-001",
)
chat = chat_model.start_chat()

emb_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

def document_extraction(filename_path: str):
  print(filename_path)
  print("-" * 80)
  print(str(filename_path))
  return process_document_sample(
      project_id,
      location,
      processor_id,
      mime_type,
      file_path=filename_path,
  )


def document_intelligent_refactor(document_ocr: str):
  with open(document_pdf, 'rb') as file:
    doc = file.read()
  file = Part.from_data(doc, mime_type="application/pdf")

  prompt = """
  You have 1 original file to understand the structure, layout, format, etc and
  an ocr extraction of the file. Your mission is to regenerate a digital file.
  
  """
  model = GenerativeModel(
      "gemini-1.5-pro-001",
  )

  rules = """
  Rules:
  If you detect structured tables, place the second table directly below the first table (concat),
  meaning: create 1 single table.

  """

  response = model.generate_content(
      [f"Instructions:\n{prompt}\n\nOcr_extraction:\n{document_ocr}\n\nFile:",
       file, "\n\nOutput:"],
  )
  re = response.text
  return re


# Conversational Bot
def conversation(query: str, online_context: str):

  print("-"*100)
  print(type(online_context))
  print(online_context)

  inputs = [TextEmbeddingInput(query, "RETRIEVAL_DOCUMENT")]
  embeddings = emb_model.get_embeddings(inputs)[0].values
  fv = feature_store.FeatureView(name=fview)
  r = fv.search(
      embedding_value=embeddings,
      neighbor_count=5,
      return_full_entity=True,  # returning entities with metadata
  ).to_dict()

  offline_context = []
  for neighbor in r["neighbors"]:
    for feature in neighbor["entity_key_values"]["key_values"]["features"]:
      if feature["name"] == "content":
        offline_context.append(feature["value"]["string_value"])
  print(offline_context)
  gemini_response = chat.send_message(
      [
          f'''
      Always use your offline_context to answer.
      If your online_context is not empty use it to answer questions regarding.
      
      offline_context:
      {str(offline_context)}
      
      online_context:
      {online_context.replace(',',' ')}
      
      rules:
      the output needs to have response, offline_context and online_context, if the value is empty, assign an empty string.
      
      original_query:
      {query}
      
      output_in_json:
      {{
        "response": <your response>,
        "offline_context": <a python list of the offline context>,
        "online_context": <a markdown of the online context>
      }}
      empty string if not available.
      '''
      ],
      generation_config=generation_config
  )
  try:
    gemini_response = gemini_response.text
  except:
    print("error en la matrix")
    print(gemini_response)

  print(type(gemini_response))
  print("-"*80)
  print(gemini_response)
  _ = json.loads(gemini_response)
  print("-"*80)
  print(_)

  return _["response"], _["offline_context"], _["online_context"]

