import json
import base64
import vertexai
from variables import *
from openai import OpenAI
from vertexai.generative_models import GenerativeModel, Part, FinishReason, Tool
import vertexai.preview.generative_models as generative_models
import time

# Replace 'your-api-key' with your actual OpenAI API key
client = OpenAI(
    api_key=key,
    organization=organization
)

vertexai.init(project=project_id, location=location)

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
}

tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=False)
    ),
]
ver_model = GenerativeModel(
    "gemini-1.5-pro-001",
    tools=tools,
)

def verification(prompt: str):

  text1 = f'''
  Your only task is to validate the following statement against internet and give me the % level of veracity:
  
  <example>
  {{"justification": "Is tru that x is y because...", "veracity": "80%"}}
  </example>

  Query:
  {prompt}
  '''

  response = ver_model.generate_content(
      [text1],
      generation_config=generation_config,
      safety_settings=safety_settings,
  )

  return response


def chat_gpt_4(prompt: str):
  llm_response = client.chat.completions.create(
      model="gpt-4",  # Consider using "gpt-3.5-turbo" for cost-effectiveness
      messages=[
          {"role": "user", "content": prompt},
          {"role": "system", "content": """
          You are a witty and engaging chatbot in a battle of wits. 
          Try to outsmart your opponent with clever responses and unexpected turns of phrase. 
          Don't repeat yourself.
          """},
      ],
  )
  llm_response = llm_response.choices[0].message.content
  res = verification(prompt=llm_response)
  response = json.loads(res.text)
  justification = response["justification"]
  veracity = response["veracity"]
  citations = [i.web.uri for i in res.candidates[0].grounding_metadata.grounding_attributions]
  return llm_response, justification, veracity, citations


def gemini(prompt:str):
  model = GenerativeModel(
      "gemini-1.5-flash-001",
      system_instruction=["""
      You are a sharp and insightful chatbot in a battle of wits. 
      Try to outsmart your opponent with clever responses and insightful observations. 
      Don't repeat yourself.
      """]
  )
  llm_response = model.generate_content([prompt])
  llm_response = llm_response.text
  res = verification(prompt=llm_response)
  response = json.loads(res.text)
  justification = response["justification"]
  veracity = response["veracity"]
  citations = [i.web.uri for i in res.candidates[0].grounding_metadata.grounding_attributions]
  return llm_response, justification, veracity, citations
