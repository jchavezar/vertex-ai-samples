import vertexai
import http.client
from typing import List
from variables import *
from openai import OpenAI
from vertexai.preview import reasoning_engines
from vertexai.generative_models import GenerativeModel

# Artificial Mind 1: OpenAI
openai_client = OpenAI(
    api_key=key, # Replace 'your-api-key' with your actual OpenAI API key / variables.py
    organization=organization
)

vertexai.init(project=project_id, location=location)

# Artificial Mind 2: Gemini
gemini_model = GenerativeModel(
    "gemini-1.5-pro-001",
    system_instruction=["Be smart and creative and give details"]
)

# Functions
# Judge Function
# Tool Internet Search
def get_real_time_internet_search(
    query: str,
):
  """Use the query to use serper to get answer from real time internet search"""
  import json

  headers = {
      'X-API-KEY': serperapi_key,
      'Content-Type': 'application/json'
  }

  conn = http.client.HTTPSConnection("google.serper.dev")

  # Create the payload for the Serper API request
  payload = json.dumps({"q": query})

  # Send the request to Serper API
  conn.request("POST", "/search", payload, headers)
  res = conn.getresponse()
  context = json.loads(res.read().decode("utf-8"))
  return context

# Local Reasoning Engine
agent = reasoning_engines.LangchainAgent(
    model="gemini-1.5-pro-001",
    tools=[get_real_time_internet_search],
    agent_executor_kwargs={"return_intermediate_steps": True},
)

# Verification/Judge Main Function
def verification(prompt: str):
  re = agent.query(
      input=f"""Get a summary of the statement below and use the real time internet search agent to
    respond if you think the statement is true or not
    
    statement:
    ```{prompt}```
    """,
  )

  if len(re["intermediate_steps"]) != 0:
    ref = [i["link"] for i in re["intermediate_steps"][0][1]["organic"]]
    if "answerBox" in re["intermediate_steps"][0][1]:
      answer_box = re["intermediate_steps"][0][1]["answerBox"]["snippet"]
  else:
    ref = ["none"]
  return {"justification": re["output"], "veracity": "100", "citations": ref}


# OpenAI ChatGPT Function
def chat_gpt_4(conversation_history: List):
  global prompt_template
  prompt_template = """
  You are an artificial mind, tasked with engaging in a debate with another AI. Your goal is to 
  collaborate and reach a conclusion or solution for the given topic.  Carefully consider the 
  previous statements made by your opponent and contribute by providing new insights, information, 
  or perspectives.  Maintain a clear and concise communication style.

  <chat_history>
  {chat_history}
  <chat_history>

  Response as raw text:
  """

  if isinstance(conversation_history[-1], dict) and "topic" in \
      conversation_history[-1]:
    print("topic")
    prompt = prompt_template.format(
        chat_history=str(conversation_history))
    text = "begin the collaboration"
  else:
    text = str(conversation_history[-1])
    prompt = prompt_template.format(
        chat_history=str(conversation_history))


  llm_response = openai_client.chat.completions.create(
      model="gpt-4",  # Consider using "gpt-3.5-turbo" for cost-effectiveness
      messages=[
          {"role": "user", "content": text},
          {"role": "system",
           "content": f"Be smart and creative:\n{prompt}"},
      ],
  )
  llm_response = llm_response.choices[0].message.content
  response = verification(prompt=llm_response)
  justification = response["justification"]
  veracity = response["veracity"]
  citations = response["citations"]

  return llm_response, justification, veracity, citations

# Gemini Function
def gemini(conversation_history: List):
  global prompt_template
  prompt_template = """
  You are an artificial mind, tasked with engaging in a debate with another AI. Your goal is to 
  collaborate and reach a conclusion or solution for the given topic.  Carefully consider the 
  previous statements made by your opponent and contribute by providing new insights, information, 
  or perspectives.  Maintain a clear and concise communication style.

  <chat_history>
  {chat_history}
  <chat_history>

  Response as raw text:
  """

  prompt = prompt_template.format(chat_history=str(conversation_history))
  llm_response = gemini_model.generate_content([prompt])
  llm_response = llm_response.text
  response = verification(prompt=llm_response)
  justification = response["justification"]
  veracity = response["veracity"]
  citations = response["citations"]

  return llm_response, justification, veracity, citations
