import base64
import vertexai
from variables import *
from openai import OpenAI
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import time

# Replace 'your-api-key' with your actual OpenAI API key
client = OpenAI(
    api_key=key,
    organization=organization
)

vertexai.init(project=project_id, location=location)

def chat_gpt_4(prompt: str):
  response = client.chat.completions.create(
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
  return response.choices[0].message.content

def gemini(prompt:str):
  model = GenerativeModel(
      "gemini-1.5-flash-001",
      system_instruction=["""
      You are a sharp and insightful chatbot in a battle of wits. 
      Try to outsmart your opponent with clever responses and insightful observations. 
      Don't repeat yourself.
      """]
  )
  response = model.generate_content([prompt])
  return response.text

def battle_bots(topic: str, rounds=2):
  conversation_history = [topic]
  current_speaker = "GPT-4"  # Start with GPT-4

  for _ in range(rounds):
    print(f"\n{'-' * 20}")
    print(f"{current_speaker} is thinking...")
    time.sleep(2) # Simulate thinking time

    if current_speaker == "GPT-4":
      response = chat_gpt_4(" ".join(conversation_history[-1]))
      print(f"{current_speaker}: {response}")
      current_speaker = "Gemini"
    else:
      response = gemini(" ".join(conversation_history[-1]))
      print(f"{current_speaker}: {response}")
      current_speaker = "GPT-4"

    conversation_history.append(response)