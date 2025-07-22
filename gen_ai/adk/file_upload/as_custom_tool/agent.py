import os
import sys
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
from google.adk.agents import LlmAgent


client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

async def document_analyze(tool_context: ToolContext):
    from google import adk
    print(adk.__version__, file=sys.stdout)
    artifacts = await tool_context.list_artifacts()
    print("#"*80, file=sys.stdout)
    print(artifacts, file=sys.stdout)
    if len(artifacts) > 0:
        print(artifacts[-1])
        a1 = await tool_context.load_artifact(filename=artifacts[-1])
        if 'inlineData' in a1:
            file = types.Part.from_bytes(
                data=a1['inlineData']['data'],
                mime_type=a1['inlineData']['mimeType'],
            )
            try:
                re = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=0
                        )
                    ),
                    contents=[
                        types.Part.from_text(text="Describe the following document"),
                        file
                    ]
                )
                re = re.text
            except Exception as e:
                re = e
            return re
    else: return "No Documents Found"

    return f"document extraction has: {str(artifacts)}"

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are General Intelligence Assistant",
    instruction="""
    Always use the following workflow in sequence (do not skip any step):
    1. Use your `document_analyze` tool to get the file content if No Documents Found just skip this step.
    2. Respond any question.
    """,
    tools=[document_analyze]
)
