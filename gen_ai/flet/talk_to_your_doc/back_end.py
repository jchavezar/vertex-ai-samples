# %%
import vertexai
from variables import *
from vertexai.generative_models import GenerativeModel, Part
from process_doc import process_document_sample

# %%
vertexai.init(project=project_id, location=region)

chat_model = GenerativeModel(
    "gemini-1.5-flash-001",
)
chat = chat_model.start_chat()


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
       file, "\n\nOutput as Markdown of the entire file:"],
  )
  re = response.text
  return re


# Conversational Bot
def conversation(query: str, context: str):
  print("-"*80)
  print(context)
  print("-"*80)
  return chat.send_message(
      [
      f"""
      If your context is not empty use it to answer questions regarding.
      
      Context:
      {context}
      
      Query:
      {query}
      """
      ]
  ).text
