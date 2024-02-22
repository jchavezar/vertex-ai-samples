#%%
import asyncio
import vertexai
from typing import Tuple
from utils import vector_database
from utils.video.credentials import *
from vertexai.language_models import TextEmbeddingModel
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel, Tool, GenerationResponse

from utils.function_helpers import get_text, get_function_name, get_function_args, EXAMPLES, parse_output_action


variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "database_password": DATABASE_PASSWORD, #utils.video.credentials
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}


model = GenerativeModel("gemini-pro")
vector_database_client = vector_database.Client(variables)
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

#region Python Functions
def math_operation_calculate(text: str):
    """Operation using Eval."""
    print("llm for math operation")

    responses = model.generate_content(
        f"""
    your task is to interpret the following query and transform in a way readable by eval pyton function:
    - Your response should be the string argument inside of eval only.
    - Do not add either word python or backticks to the response.
    
    Example:
    Query: The residual between 8 and 4?
    Output: 8-4
    
    Query: {text}
    
    Output:""",
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1
        },
        safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        },
    )
    print(responses.text)

    return f"The final answer is {eval(responses.text)}"

    #return eval(responses.text)

def call_api(name: str, args: Tuple[str]) -> str:
    """Check the incoming function name then call the appropriate API."""
    print(name)
    if name == "math_operation_calculate":
        print(f"\nMath Operation Calculate Tool...")
        text = args.get("values", None)
        return math_operation_calculate(text=text)

def get_llm_output(res: GenerationResponse) -> Tuple[str, str]:
    """Helper to parse response and return the text or function details."""
    name = None
    args = None
    text = get_text(res)
    print("supertext")
    print(text)
    if not text:
        name = get_function_name(res)
        args = get_function_args(res)
        output = f"FUNCTION CALL: {name}({args})\n"
    else:
        output = text

    action = parse_output_action(output)
    print(f"ACTION: {action}")

    # Implementing a lazy output parser for the sake of the demo
    if action == "final_answer":
        output = output.split("Final Answer: ")[-1]
    elif name and action in ["function_call", "tool_call"]:
        print("functioncall and toolcall")
        output = call_api(name, args)
        # if output:
        #   output = self.summarize_api_result(output)

    return action, output

def summarize_api_result(text: str) -> str:
    """Summarize the API result."""
    prompt = """Summarize the result and provide 3 bullet points back to the user.
  Respond with something like:
  `Here's what I found:
  - result1
  - result2
  - result3
  
  result:
  `
  """
    model = GenerativeModel("gemini-pro")
    res = model.generate_content(prompt + text)

    return res.text
#endregion

#region RAG
def find_match(input, schema):
    query = model_emb.get_embeddings([input])[0].values
    result = asyncio.run(vector_database_client.query(query, schema))
    return result
#endregion

#%%
#region Function Calling Definition
math_spec ={
    "name": "math_operation_calculate",
    "description": "Get the mathematical operation of numbers",
    "parameters": {
        "type": "object",
        "properties": {
            "values": {
                "type": "string",
                "description": "the numbers to evaluate"
            },
        },
        "required": [
            "values"
        ]
    }
}

all_tools = Tool.from_dict(
    {
        "function_declarations": [
            math_spec,
        ]
    }
)

tool_name_description_str = ""
for tool in all_tools._raw_tool.function_declarations:
    tool_name_description_str += f"{tool.name}: {tool.description}\n"
#tools_str = self.__build_tool_name_desc_str()
tool_names = [tool.name for tool in all_tools._raw_tool.function_declarations]
tool_names.append("no_action")


react_prompt_def = f"""Your name is Gemini and you are a helpful and polite AI
  Assistant at Google. Your task is to assist humans in answering questions.

  You have access to the following tools:\n{tool_name_description_str}

  Use the following format when answering questions:
  Question: the input question you must answer
  Thought: you should always think about what to do
  Action: the action to take, should be one of {tool_names}
  Action Input: the input to the action
  Observation: the result of the action
  ... (this Thought/Action/Action Input/Observation can repeat N times)
  Thought: I now know the final answer
  Final Answer: the final answer to the original input question

  ### EXAMPLES ###
  {EXAMPLES}

  ### CURRENT CONVERSATION ###
  """


#endregion
#%%
#region Main
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}
query = "What's the sum of 2 and 2?"
init_prompt = react_prompt_def + f"\n ORIGNAL USER QUERY: {query}"
fc_chat = model.start_chat()
res = fc_chat.send_message(init_prompt, tools=[all_tools], safety_settings=safety_settings)
action, output = get_llm_output(res)
print("-"*80)
print(res.candidates[0].content.parts[0].function_call.name)
print("-"*80)

print(action)
print(output)

i = 2
while all([i < 6, action != "final_answer"]):
    #prompt = "hello, do you know what's the sum of 2 and 2?"
    prompt = react_prompt_def + f"\n{output}"
    res = fc_chat.send_message(prompt, tools=[all_tools], safety_settings=safety_settings)
    print("#"*80)
    print(res)
    print("#"*80)
    action, output = get_llm_output(res)
    print(f"action: `{action}`\noutput: {output}")
    i += 1

#print(USER:  + prompt)
#res = fc_chat.send_message(prompt, tools=[all_tools])
#text = get_text(res)

#if not text:
#    name = get_function_name(res)
#    args = get_function_args(res)
#    print(fAGENT: FUNCTION CALL: {name}({args})\n)
#    
#    api_result = call_api(name, args)
#    if api_result:
#        print(api_result)
#        print(summarize_api_result(api_result) + "\n")
# %%
