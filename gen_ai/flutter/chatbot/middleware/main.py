import base64
import json
import vertexai
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Form
from vertexai.generative_models import GenerativeModel, Part, FunctionDeclaration, Tool, Content
import vertexai.preview.generative_models as generative_models

project = "vtxdemos"
region = "us-central1"

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}


def request_image_upload(prompt):
  """Function to request an image upload from the user."""
  return {
      "function": "uploadImage",
      "args": {
          "prompt": "Please upload an image to help clarify your question.",
      }
  }

vertexai.init(project="vtxdemos", location="us-central1")
model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=["""
    Respond any question as raw text without any formatting, icons, emojis, etc.
    If the user needs a car crash evaluation ask him to upload and image using this response format: {"response": <response>, "image_required": "true"}
    Otherwise return your response as raw text.
    """],
    # tools=[tools],
)
chat = model.start_chat()

app = FastAPI()

@app.post('/query')
async def image_conversion(text_data: Optional[str] = Form(None)):
  re = chat.send_message(
      [text_data],
      generation_config=generation_config,
      safety_settings=safety_settings,
  )

  parsed = {
      "message": re.text
  }

  print(type(parsed))

  return parsed

