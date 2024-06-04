import base64

import pickle
import vertexai
import numpy as np
import pandas as pd
from google.cloud import storage
from flask import Flask, jsonify, request
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.generative_models import (
  GenerationConfig,
  FunctionDeclaration,
  GenerativeModel,
  Part,
  Tool,
)

# Variables
project_id = "jesusarguelles-sandbox"
location = "us-central1"
model_id = "gemini-1.0-pro-002"
model_file_path = "money_laundering_detection/model.pkl"  # Google Cloud Storage Model stored during the training
transformation_file_path = "money_laundering_detection/label_encoder.pkl"  # Google Cloud Storage Transform Pickle
# during the training

# Initialization
vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.0-pro-002")
bucket = storage.Client(project="jesusarguelles-sandbox").bucket("jesusarguelles-datasets-public")

with bucket.blob(model_file_path).open("rb") as f:
  laundering_model = pickle.load(f)
with bucket.blob(transformation_file_path).open("rb") as f:
  label_mappings = pickle.load(f)

# Gemini
generation_config = {
    "max_output_tokens": 2048,
    "temperature": 0.7,
    "top_p": 1,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

# Vertex Functions Calling Definition

get_laundering_prediction = FunctionDeclaration(
    name="get_laundering_prediction",
    description="Get if the money is laundered",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {
            "segment": {
                "type": "integer",
                "description": "The segment number"
            },
            "step": {
                "type": "integer",
                "description": "The number of step"
            },
            "trans_type": {
                "type": "object",
                "description": "Transaction Type"
            },
            "amount": {
                "type": "number",
                "format": "float",
                "description": "The amount of the transaction"},
            "nameOrig": {
                "type": "object",
                "description": "The id, or name of the transfer origin"},
            "oldbalanceOrg": {
                "type": "number",
                "format": "float",
                "description": "The old balance organization number, oldbalancerOrg",
            },
            "nameDest": {
                "type": "object",
                "description": "Name or id of the transfer destination"
            },
            "oldbalanceDest": {
                "type": "number",
                "format": "float",
                "description": "old balance destination",
            },
            "accountType": {
                "type": "object",
                "description": "The account type"
            }
        },
    },
)

ml_prediction_tool = Tool(
    function_declarations=[
        get_laundering_prediction,
    ],
)

# Python Function to call Vertex ML Money Laundering Detection


def get_laundering_prediction_function(
    segment,
    step,
    trans_type,
    amount,
    nameOrig,
    oldbalanceOrg,
    nameDest,
    oldbalanceDest,
    accountType
):
  """

  :param segment:
  :param step:
  :param trans_type:
  :param amount:
  :param nameOrig:
  :param oldbalanceOrg:
  :param nameDest:
  :param oldbalanceDest:
  :param accountType:
  :return:
  """
  predict = {
      "segment": [segment],
      "step": [step],
      "trans_type": [trans_type],
      "amount": [amount],
      "nameOrig": [nameOrig],
      "oldbalanceOrg": [oldbalanceOrg],
      "nameDest": [nameDest],
      "oldbalanceDest": [oldbalanceDest],
      "accountType": [accountType]
  }
  to_predict_df = pd.DataFrame(predict)
  cat_feat = [i for i in to_predict_df.columns if to_predict_df[i].dtypes == 'O']

  for i in cat_feat:
    to_predict_df[i] = to_predict_df[i].map(label_mappings[i])
  print(to_predict_df)
  re = str(laundering_model.predict(to_predict_df)[0])
  print(re)
  return {"is_laundered": re}


# Gemini Conversational mode Initialization
context = """
You are an AI chatbot for assistant with different tasks:
- task 1: Respond any question except money laundering with your knowledge.
- task 2: Respond any question about money laundering, use the following Money Laundering parameters as your knowledge.
 -- You have access to the following tools/functions only: get_laundering_prediction 
"""

model = GenerativeModel(
    model_name=model_id,
    system_instruction=[context],
    generation_config=GenerationConfig(temperature=0),
    safety_settings=safety_settings,
    tools=[ml_prediction_tool],
)

# Start a chat session
chat = model.start_chat()


def conversational_bot(query: str, context: str) -> str:
  """

  :param query:
  :param context:
  :return:
  """

  template = f"""
    <rules task 2>
    - During task 2 you call an external api service which return either 1 or 0 being 1 as laundered and 0 as not.
    - You have ac
    
    Money Laundering parameters:
    <money_laundering_param>
    {context}
    </money_laundering_param>
    <end rules task 2>
    
    User Query:
    """

  response = chat.send_message(template+query)
  try:

    function_call = response.candidates[0].function_calls[0]

    if function_call.name == "get_laundering_prediction":

      segment = function_call.args["segment"]
      step = function_call.args["step"]
      trans_type = function_call.args["trans_type"]
      amount = function_call.args["amount"]
      nameOrig = function_call.args["nameOrig"]
      oldbalanceOrg = function_call.args["oldbalanceOrg"]
      nameDest = function_call.args["nameDest"]
      oldbalanceDest = function_call.args["oldbalanceDest"]
      accountType = function_call.args["accountType"]

      api_response = get_laundering_prediction_function(
          segment,
          step,
          trans_type,
          amount,
          nameOrig,
          oldbalanceOrg,
          nameDest,
          oldbalanceDest,
          accountType
      )

    re = chat.send_message(
        Part.from_function_response(
            name="get_laundering_prediction",
            response={
                "content": api_response,
            },
        ),
    )
    re = re.text
  except:
    try:
      re = response.candidates[0].content.parts[0].text
    except:
      re = "no response"
  return re

app = Flask(__name__)


@app.route('/bot', methods=['GET'])
def bot():
  """

  :return:
  """
  prompt = request.args['prompt']
  try:
    context = request.args['context']
  except:
    context = ""
  response = conversational_bot(query=prompt, context=context)
  return jsonify(response)


if __name__ == '__main__' :
  app.run(debug=True, port=8002)