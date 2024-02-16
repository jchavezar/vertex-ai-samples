
from proto.marshal.collections import repeated
from proto.marshal.collections import maps
from vertexai.preview.generative_models import GenerationResponse

def recurse_proto_repeated_composite(repeated_object):
    repeated_list = []
    for item in repeated_object:
        if isinstance(item, repeated.RepeatedComposite):
            item = recurse_proto_repeated_composite(item)
            repeated_list.append(item)
        elif isinstance(item, maps.MapComposite):
            item = recurse_proto_marshal_to_dict(item)
            repeated_list.append(item)
        else:
            repeated_list.append(item)

    return repeated_list

def recurse_proto_marshal_to_dict(marshal_object):
    new_dict = {}
    for k, v in marshal_object.items():
      if not v:
        continue
      elif isinstance(v, maps.MapComposite):
          v = recurse_proto_marshal_to_dict(v)
      elif isinstance(v, repeated.RepeatedComposite):
          v = recurse_proto_repeated_composite(v)
      new_dict[k] = v

    return new_dict

def get_text(response: GenerationResponse):
  """Returns the Text from the Generation Response object."""
  part = response.candidates[0].content.parts[0]
  print("part"*80)
  print(part)
  print("part"*80)
  try:
    text = part.text
  except:
    text = None

def get_function_name(response: GenerationResponse):
  return response.candidates[0].content.parts[0].function_call.name

def get_function_args(response: GenerationResponse) -> dict:
  return recurse_proto_marshal_to_dict(response.candidates[0].content.parts[0].function_call.args)

def parse_output_action(output: str) -> str:
  """Simple helper to set next `action` based on ReAct loop."""
  if "Final Answer" in output:
    return "final_answer"
  elif "FUNCTION CALL" in output:
    return "function_call"
  elif "TOOL_CALL" in output:
    return "tool_call"
  else:
    return "continue"

### EXAMPLES ###
EXAMPLES = """
    EXAMPLE 1:
    User: What are the total net farm and net gain together, context: net farm 4 and net gain 5?
    Thought: I should check math operation sum for 4 and 5
    Action: math_operation_calculate
    Action Input: net farm 4 and net gain 5
    Observation:
      -  By using the tool I know the answer is 9.
    Thought: I now know the final answer
    Final Answer: I found the result is 9.
"""