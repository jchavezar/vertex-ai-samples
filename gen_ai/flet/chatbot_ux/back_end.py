#%%
import re
import vertexai
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel, SafetySetting, Part, FunctionDeclaration, Tool

project_id = "jesusarguelles-sandbox"
table_id = "jesusarguelles-sandbox.demos_us.tb_data_s"

# Construct a BigQuery client object and Initialize Vertex AI Client.
client = bigquery.Client()
vertexai.init(project=project_id, location="us-central1")

# Get table schema
table = client.get_table(table_id)  # Make an API request.

# Schema / Description
schema = {f"Field: {field.name}, Type: {field.field_type}, Description: {field.description}" for field in table.schema}

# Vertex AI Definition
system_instruction_prompt = f"""
You are an Agent assistant, a retail expert, that helps internal human agents to analyze information from users.

Rules:
** Table Query **: you have a tool to gather any kind of information regarding users, purchases, etc (<sql_query>), use it.
** Clear SQL Output**: Your output needs to be a string of a valid SQL formatted query. 
                     Do not escape any characters within the query (e.g., don't use \' instead of '). 
                     Ensure the query can be directly executed in BigQuery.

Schema for BQ Table:
table: {table_id} | schema: {schema}
"""

function_name = "sql_query"
sql_query_func = FunctionDeclaration(
    name=function_name,
    description="Get information from data in BigQuery using SQL queries.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a BigQuery dataset and table. In the SQL query, always use the fully qualified dataset and table names"
            }
        },
        "required": ["query"]
    },
)

retail_tool = Tool(
    function_declarations=[
        sql_query_func,
    ],
)

model = GenerativeModel(
    "gemini-1.5-flash-002",
    system_instruction=[system_instruction_prompt],
    tools=[retail_tool]
)


# Function Definition
def sql_query_api(query):
    df = bigquery.Client(project=project_id).query(query).to_dataframe()
    return df.to_json(orient="records")


chat = model.start_chat()


def vertexai_conversation(query: str):
    details = []
    try:
        response = chat.send_message(query)
    except Exception as e:
        print(e)
        return f"There was a issue with the request: {e}", None

    if "function_call" in response.candidates[0].content.parts[0].to_dict():
        function_call = response.candidates[0].function_calls[0]

        if function_call.name == "sql_query":
            raw_query = function_call.args["query"]
            raw_query = re.sub(r"\\'", "'", raw_query)
            res1 = str(sql_query_api(raw_query))
            details.append(response)
            res2 = chat.send_message(
                Part.from_function_response(
                    name=function_name,
                    response={"content": res1},
                )
            )
            details.append(res2)
            output = res2.text
            return output.strip(), details
    else:
        print("here")
        output = response.text
        details.append(response)
        return output.strip(), details


# re, details = vertexai_conversation("how much was in sales for electronics in 2023?")