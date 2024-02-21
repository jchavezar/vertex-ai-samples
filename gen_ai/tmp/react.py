#%%
#@title Helper Class - ReactAgent + Tool Specs{ display-mode: "form" }
import vertexai
import logging
import requests
import pandas as pd
from typing import List, Dict, Any, Tuple
from proto.marshal.collections import repeated
from proto.marshal.collections import maps
from google.cloud import logging as cloud_logging
from vertexai.preview.generative_models import (
    GenerativeModel,
    GenerationResponse,
    Content,
    Part,
    Tool
    )

vertexai.init(project="vtxdemos")

### EXAMPLES ###
EXAMPLES = """
    EXAMPLE 1:
    User: What are the last 10 WARNING logs?
    Thought: I should check the logs
    Action: google_logs_tool
    Action Input: severity=WARNING, num_logs=10
    Observation:
      - The `hid_regression.py` script is unable to refresh its credentials, resulting in a `RefreshError` exception being raised.
      - The error message indicates that the JWT signature is invalid, suggesting that the service account key used to generate the JWT may be incorrect or expired.
      - The full error message is: `google.auth.exceptions.RefreshError: ('invalid_grant: Invalid JWT Signature.', `'error': 'invalid_grant', 'error_description': 'Invalid JWT Signature.'`)`
    Thought: I now know the final answer
    Final Answer: The `hid_regression.py` script is unable to refresh its credentials, resulting in a `RefreshError` exception being raised.

    EXAMPLE 2:
    User: Where can I find some good bbq in Austin?
    Thought: I should search for POIs
    Action: places_search_tool
    Action Input: preferences=bbq, city=Austin
    Observation: I found the following results [1] [2] [3]
    Thought: I now know the final answer
    Final Answer: I found the following results [1] [2] [3]

    EXAMPLE 3:
    User: What is the best coffe shop in austin? What is their rating multipled by 3?
    Thought: I should search for POIs
    Action: places_search_tool
    Action Input: preferences=coffee, city=Austin
    Observation: I found the following results [1] [2] [3]
    Thought: Reference [2] has the highest rating, I should multiple it by 3.
    Thought: I know the final answer.
    Final Answer: [2] has the highest rating of 4.5, multipled by 3 is 13.5.

    EXAMPLE 4:
    User: What are the last 10 ERROR logs? and how many of them were JWT errors?
    Thought: I should check the logs
    Action: google_logs_tool
    Action Input: severity=ERROR, num_logs=10
    Observation: The following results [results] contained 3 JWT errors.
    Thought: I now know the final answer
    Final Answer: There were 3 JWT errors in the last 10 ERROR logs.
"""

class ReactAgent:
  """Rudimentary ReAct Agent for Demo purposes."""
  def __init__(self, debug: bool = False):
    self.model = GenerativeModel("gemini-pro")
    self.__debug = debug

    if self.__debug:
      logging.basicConfig(level=logging.DEBUG, force=True)
    else:
      logging.basicConfig(level=logging.INFO, force=True)

  @staticmethod
  def __get_text(response: GenerationResponse) -> str:
    """Returns the Text from the Generation Response object."""
    part = response.candidates[0].content.parts[0]
    try:
      text = part.text
    except:
      text = None

    return text

  @staticmethod
  def __get_function_name(response: GenerationResponse) -> str:
    """Return the function name from the Generation Response object."""
    return response.candidates[0].content.parts[0].function_call.name

  def __get_function_args(self, response: GenerationResponse) -> dict:
    """Extract the args created by the Function call."""
    return self.__recurse_proto_marshal_to_dict(
        response.candidates[0].content.parts[0].function_call.args)

  def __recurse_proto_repeated_composite(self, repeated_object) -> List[Any]:
    """Recursively unpack proto repeated composite objects."""
    repeated_list = []
    for item in repeated_object:
        if isinstance(item, repeated.RepeatedComposite):
            item = self.__recurse_proto_repeated_composite(item)
            repeated_list.append(item)
        elif isinstance(item, maps.MapComposite):
            item = self.__recurse_proto_marshal_to_dict(item)
            repeated_list.append(item)
        else:
            repeated_list.append(item)

    return repeated_list

  def __recurse_proto_marshal_to_dict(self, marshal_object) -> Dict[str, Any]:
    """Recursively unpack proto marshal objects."""
    new_dict = {}
    for k, v in marshal_object.items():
      if not v:
        continue
      elif isinstance(v, maps.MapComposite):
          v = self.__recurse_proto_marshal_to_dict(v)
      elif isinstance(v, repeated.RepeatedComposite):
          v = self.__recurse_proto_repeated_composite(v)
      new_dict[k] = v

    return new_dict

  def __load_tools(self):
    """Returns the 2 predefined Tool specs.

    For demo purposes, these are utilized as Function calling specs for Gemini.
    No actual API calls are being made. However, these could be replaced with
    Vertex Extensions, or any other API call as needed.
    """
    weather_spec = {
        "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
          "type": "object",
          "properties": {
              "location": {
                  "type": "string",
                  "description": "The city and state, e.g. San Francisco, CA"
              },
              "unit": {
                  "type": "string",
                  "enum": [
                      "celsius",
                      "fahrenheit",
                  ]
              }
          },
          "required": [
              "location"
          ]
      }
    }

    places_search_spec = {
        "name": "places_search_tool",
        "description": "Provides point of interest (POI) information based on the user's search query.",
        "parameters": {
            "type": "object",
            "properties": {
                "preferences": {
                    "type": "string",
                    "description": "The user's preferences for the search, like skiing, beach, restaurants, bbq, etc."
                },
                "city": {
                    "type": "string",
                    "description": "The city to search for POIs in."
                }
            },
            "required": [
                "city"
            ]
        }
    }

    logs_spec = {
        "name": "google_logs_tool",
        "description": "Gets a set of logs from Google Cloud Logging.",
        "parameters": {
            "type": "object",
            "properties": {
                "severity": {
                    "type": "string",
                    "description": "The severity of the log type: ERROR, INFO, WARNING, CRITICAL."
                },
                "num_logs": {
                    "type": "integer",
                    "description": "The number of logs to return"
                }
            },
            "required": [
                "severity"
            ]
        }
    }

    return Tool.from_dict(
        {"function_declarations": [places_search_spec, logs_spec]}
        )

  def __build_tool_name_desc_str(self) -> str:
    """Builds a string of tool names and descriptions for the soft prompt."""
    tools = self.__load_tools()
    tool_name_description_str = ""
    for tool in tools._raw_tool.function_declarations:
      tool_name_description_str += f"{tool.name}: {tool.description}\n"

    return tool_name_description_str

  def __load_soft_prompt(self) -> str:
    """Our main ReAct prompt, with the tool names and descriptions."""

    tools_str = self.__build_tool_name_desc_str()
    tool_names = [tool.name for tool in self.__load_tools()._raw_tool.function_declarations]
    tool_names.append("no_action")

    prompt = f"""Your name is Gemini and you are a helpful and polite AI
    Assistant at Google. Your task is to assist humans in answering questions.

    You have access to the following tools:\n{tools_str}
    When calling `places_search_tool` or `google_logs_tool`, you can only use them once.

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

    logging.debug(prompt)

    return prompt

  def get_logs(self, project_id: str) -> List[Dict[str, Any]]:
    """Get a set of GCP logs as a list of JSON objects."""
    client = cloud_logging.Client(project=project_id)

    resources = [f"projects/{project_id}"]
    entries = list(client.list_entries(resource_names=resources))
    data = [entry.to_api_repr() for entry in entries]

    return data

  def logs_to_df(self, project_id: str, severity: str, num_logs: int = 10):
    data = self.get_logs(project_id)
    df = pd.DataFrame(data)
    df = df[df.severity == severity]
    df.reset_index(inplace=True, drop=True)

    df = df.head(int(num_logs))

    return df.to_json()

  def call_places_search(self, city: str, preferences: str):
    """Get point of interest information based on city and preference infomration from the user.

    Args:
      city: The city where the user wants to get point of interest information from.
      preferences: Filters for preferences like "bbq", "skiing", "family friendly", etc.
      """
    endpoint = "https://travel-places-search-v7b55neq7a-uc.a.run.app"
    headers =  {
            "Content-Type": "application/json",
            "Authorization": f"Bearer dsfsfdsafdsfs"
            }

    res = requests.post(
        f"{endpoint}/places_search_tool",
        headers=headers,
        json={"city": city, "preferences": preferences}
        )
    return res.text

  def call_api(self, name: str, args: Tuple[str]) -> str:
    """Check the incoming function name then call the appropriate API."""
    if name == "places_search_tool":
      print(f"\nCALLING CLOUD FUNCTION - Places Search...")
      city = args.get("city", None)
      preferences = args.get("preferences", None)

      return self.call_places_search(city=city, preferences=preferences)

    elif name == "google_logs_tool":
      print(f"\nCALLING API - Cloud Logging...")
      project_id = "pmarlow-ccai-dev"
      severity = args.get("severity", None)
      num_logs = args.get("num_logs", None)

      return self.logs_to_df(project_id=project_id, severity=severity, num_logs=num_logs)

    # elif name == "code_interpreter_tool":
    #   print(f"\nCALLING VERTEX EXTENSION...")
    #   query = args.get("query", None)
    #   timeout = args.get("timeout", None)
    #   files = args.get("files", None)

    #   return call_code_interpreter_extension(query=query, timeout=timeout, files=files)

    else:
      return None

  def summarize_api_result(self, text: str) -> str:
    """Summarize the API result."""
    prompt = """Summarize the result and provide 3 bullet points back to the user.
    Respond with something like:
    `Here's what I found:
    - result1
    - result2
    - result3
    `
    """
    model = GenerativeModel("gemini-pro")
    res = model.generate_content([prompt, text])

    return res.text

  def get_llm_output(self, res: GenerationResponse) -> Tuple[str, str]:
    """Helper to parse response and return the text or function details."""
    name = None
    args = None
    text = self.__get_text(res)
    if not text:
      name = self.__get_function_name(res)
      args = self.__get_function_args(res)
      output = f"FUNCTION CALL: {name}({args})\n"
    else:
      output = text

    action = self.__parse_output_action(output)
    print(f"ACTION: {action}")

    # Implementing a lazy output parser for the sake of the demo
    if action == "final_answer":
      output = output.split("Final Answer: ")[-1]
    elif name and action in ["function_call", "tool_call"]:
      output = self.call_api(name, args)
      # if output:
      #   output = self.summarize_api_result(output)

    return action, output

  def __parse_output_action(self, output: str) -> str:
    """Simple helper to set next `action` based on ReAct loop."""
    if "Final Answer" in output:
      return "final_answer"
    elif "FUNCTION CALL" in output:
      return "function_call"
    elif "TOOL_CALL" in output:
      return "tool_call"
    else:
      return "continue"

  def react_loop(self, query: str):
    """Run the ReAct loop until we complete the goal or hit exit state."""
    # Because we can't use System Message with Gemini, we force our soft prompt
    # and our initial user query together for the very first message
    prompt = self.__load_soft_prompt()
    init_prompt = prompt + f"\n ORIGNAL USER QUERY: {query}"
    chat = self.model.start_chat()

    # Using these to denote how the LLM is iterating throug hte steps / loop
    print("### LLM CALL #1 ###")
    res = chat.send_message(init_prompt, tools=[self.__load_tools()])
    action, output = self.get_llm_output(res)
    print(f"action: `{action}`\noutput: {output}")

    # Here, we'll enter a loop and run continue to hit the LLM with a new call
    # until we reach our hard cap of 5 turns, or we hit our stop condition,
    # which is when the LLM has a "Final Answer".
    i = 2
    while all([i < 6, action != "final_answer"]):
      print(f"\n### LLM CALL #{i} ###")
      prompt = prompt + f"\n{output}"
      # prompt = f"{self.__load_soft_prompt()}\n{output}"
      res = chat.send_message(prompt, tools=[self.__load_tools()])
      action, output = self.get_llm_output(res)
      print(f"action: `{action}`\noutput: {output}")
      i += 1

    return chat

  def query(self, query: str):
    chat = self.react_loop(query)
    return chat

      
#%%

from vertexai.preview.generative_models import GenerativeModel
QUERY = "Where can I find fruit in Mexico?"

agent = ReactAgent(debug=False)
chat = agent.query(QUERY)
# %%
