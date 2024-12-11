#%%

from google import genai
from google.genai import types
from google.cloud import bigquery

project_id = "vtxdemos"
model_id = "gemini-2.0-flash-exp"
bq_table = "vtxdemos.demos_us.tb_data_s"
bq_schema = {'Field: acquisition_date, Type: DATE, Description: None',
             'Field: business_unit, Type: STRING, Description: None',
             'Field: channel_spend, Type: FLOAT, Description: None',
             'Field: customer_id, Type: INTEGER, Description: None',
             'Field: customer_type, Type: STRING, Description: None',
             'Field: marketing_channel, Type: STRING, Description: None',
             'Field: product_id, Type: INTEGER, Description: None',
             'Field: purchase_amount, Type: FLOAT, Description: None',
             'Field: purchase_date, Type: DATE, Description: None'}

bq_client = bigquery.Client(project=project_id)

gemini_client = genai.Client(
    vertexai=True,
    project=project_id,
    location="us-central1"
)

# Gemini Instructions
content = []
system_instruction = f"""
You are an Agent assistant, a retail expert, that helps internal human agents to analyze information from users.
Rules:
* **Table Query**: You have an Agent/Tool to gather any kind of information regarding users, purchases, etc (<sql_query>), use it.
* **Use Provided Schema**:  Use the following schema for all SQL queries:
    table: {bq_table} | schema: {bq_schema}

Task:
Respond the question using your agents if required.
"""

def sql_query(sql_query: str) -> str:
  """
  return the bigquery response.
  Args:
    sql_query: the query needed according to your schema.
  """

  print(sql_query)
  query_job = bq_client.query(
      sql_query
  )
  api_response = query_job.result()
  _response = [dict(row) for row in api_response]
  print(_response)
  return str(_response)

def gemini(input: str):
  content.append(
      types.Content(
          role="user",
          parts=[
              types.Part.from_text(input)
          ]
      )
  )
  _response=gemini_client.models.generate_content(
      model=model_id,
      contents=content,
      config=types.GenerateContentConfig(
          tools=[sql_query],
          system_instruction=system_instruction
      ),
  )
  content.append(
      types.Content(
          role="model",
          parts=[types.Part.from_text(_response.text)]
      )
  )
  return _response.text, _response



