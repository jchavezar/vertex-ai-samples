#%%
import re
import vertexai
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel, Part, FunctionDeclaration, Tool, GenerationConfig, ToolConfig

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
system_instruction_prompt = f'''
You are an Agent assistant, a retail expert, that helps internal human agents to analyze information from users.

Rules:
* **Table Query**: You have a tool to gather any kind of information regarding users, purchases, etc (<sql_query>), use it.
* **Clear Output**: Your output must be a string of a correctly formatted SQL query.
* **Use Provided Schema**:  Use the following schema for all SQL queries:
    table: {table_id} | schema: {schema}
* **New Column Names**: if you query is an operation try to give a new name to the column that usually is marked as f0.
* **No Hallucination**: Never generate table or column names that are not present in the provided schema.
* **Simple Escaping**: Use single quotes (') for string values in SQL queries. Avoid using escape characters.

Task:
Detect the intent of the user's query and use the following tools:
- Tool: <answer_generation>: Any answer to the user's query. If the intent is about the data in the table, use the tool <sql_query> first.
- Tool: <answer_generation> (addendum): Besides the answer, Generate 3 questions that you would recommend to ask based on your schema (be creative).
- Tool: <sql_query>: SQL Query about anything related to the data in the table, like business unit, marketing channel, channel spend, acquisition date, purchase date, etc...

Example SQL Queries:
- "What is the total purchase amount for Electronics?" -> `SELECT SUM(purchase_amount) AS total_purchase FROM jesusarguelles-sandbox.demos_us.tb_data_s WHERE business_unit = 'Electronics'`
- "Average purchase amount per customer?" -> `SELECT AVG(purchase_amount) AS average_purchase FROM jesusarguelles-sandbox.demos_us.tb_data_s GROUP BY customer_id` 

'''

answer_generation = FunctionDeclaration(
    name="answer_generation",
    description="Get any answer by either using other tools (grounding) or using your knowledge base.",
    parameters={
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "The answer of the query."},
            "recommended_questions": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "The recommended questions that user might ask based on the schema.",
                "min_items": 2,
                "max_items": 2
            }

        },
    },
)

sql_query_func = FunctionDeclaration(
    name="sql_query",
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

tb_tools = Tool(
    function_declarations=[
        answer_generation,
        sql_query_func,
        # question_gen
    ],
)


model = GenerativeModel(
    "gemini-1.5-flash-002",
    generation_config=GenerationConfig(temperature=0),
    tools=[tb_tools],
    tool_config=ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
            allowed_function_names=["answer_generation", "sql_query"],
        )
    ),
    system_instruction=system_instruction_prompt
)


# Function Definition
def sql_query_api(query):
    query_job = bigquery.Client(project=project_id).query(
        query
    )
    api_response = query_job.result()
    return str([dict(row) for row in api_response])

chat = model.start_chat()

def preloaded_questions_recommendations():
    _re = chat.send_message("Give me questions recommendations that user might ask based on your schema")
    return _re.candidates[0].function_calls[0].args

def vertexai_conversation(query: str):
    details = []
    try:
        response = chat.send_message(query)
    except Exception as e:
        print(e)
        return f"There was a issue with the request: {e}", None
    print("here1")
    if "function_call" in response.candidates[0].content.parts[0].to_dict():
        print("function working")
        function_call = response.candidates[0].function_calls[0]

        if function_call.name == "sql_query":
            print("sql_query function")
            raw_query = function_call.args["query"].replace("\\n", " ").replace("\n", "").replace("\\", "")
            res1 = str(sql_query_api(raw_query))
            details.append(response)
            res2 = chat.send_message(
                Part.from_function_response(
                    name="sql_query",
                    response={"content": res1},
                )
            )
            details.append(res2)
            output = res2.candidates[0].function_calls[0].args["answer"]
            return output.strip(), details
        else:
            print("here")
            fc=response.candidates[0].function_calls[0]
            gemini_answer = fc.args["answer"].replace("\\n", " ").replace("\n", "").replace("\\", "")
            details.append(response)
            return gemini_answer.strip(), details


# re, details = vertexai_conversation("how much was in sales for electronics in 2023?")