from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext

async def augment_data(tool_context: ToolContext):
    """

    :param extraction_data: full data extracted as it is from the file
    :return:
    """
    print("#"*80)
    print(tool_context)
    try:
        available_files = await tool_context.list_artifacts()
        print(available_files)
        te = await tool_context.load_artifact(filename=available_files[0])
        print(te)
    except Exception as e:
        te = e
    return f"data is {te}"

# async def secondary_action(tool_context: ToolContext):
#     try:
#         available_files = await tool_context.list_artifacts()
#         te = await tool_context.load_artifact(filename=available_files[0])
#         print(te)
#         return te
#
#     except Exception as e:
#         available_files = e
#     print("#"*80)
#     print(available_files)
#     return str(available_files)

root_agent = Agent(
    name="DataAugmenterAgent",
    description="You are an AI Assistant answer any question",
    model="gemini-2.0-flash-001",
    instruction="""
    You are receiving a file (if you dont have it ask for it) and your task is to extract everything from it as it is, if it contains
    images, annotate them (describe as deeply as possible) and use your tool `augment_data` to add a string.
    
    Respond with the entire string output of your tool
        """,
    tools=[FunctionTool(func=augment_data)],
)