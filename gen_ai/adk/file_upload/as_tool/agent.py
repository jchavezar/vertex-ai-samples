import sys

from google.adk.tools import ToolContext
from google.adk.agents import LlmAgent


async def document_analyze(tool_context: ToolContext):
    artifacts = await tool_context.list_artifacts()
    print("#"*80, file=sys.stdout)
    print(artifacts, file=sys.stdout)
    if len(artifacts) > 0:
        a1 = await tool_context.load_artifact(artifacts[-1])
    else: return "document extraction has: The name of this app is Sockcop"
    print("dir:........................")
    print(dir(a1))
    print(a1, file=sys.stdout)
    print("#"*80, file=sys.stdout)
    if 'inlineData' in a1:
        print("data"*5, file=sys.stdout)
        print("work", file=sys.stdout)
        print(a1["inlineData"]["data"])
        print("end")
    else:
        print(type(a1), file=sys.stdout)
        print(str(dir(a1)), file=sys.stdout)
    return f"document extraction has: {str(a1)}"

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are General Intelligence Assistant",
    instruction="""
    Always use the following workflow in sequence (do not skip any step):
    1. Use your `document_analyze` tool to get some findings.
    2. Respond any question using the output of your `document_analyze` tool.
    """,
    tools=[document_analyze]
)
