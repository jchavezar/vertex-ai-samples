from google.adk.agents import Agent
from google.adk.models import LlmRequest
from google.adk.agents.callback_context import CallbackContext
import pandas as pd
from io import BytesIO
from google.genai import types
import requests
from google.genai import types
from google import genai
from google.adk.tools import agent_tool

project_id = "vtxdemos"
location = "us-central1"
model = "gemini-2.5-flash"


def analyze_image_from_url(image_url: str):
    response_schema = {"type": "object","properties": {"Title": {"type": "string","description": "Extract the tile from the image"},"Author": {"type": "string","description": "Extract the name of the author from the image"},"ImageDescription": {"type": "string","description": "Describe this image"}},"required": ["Title","Author"]}


    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching the image: {e}"

    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)

        response = client.models.generate_content(model=model,
                                                  contents=[
                                                      types.Part.from_bytes(
                                                          data=response.content,
                                                          mime_type='image/jpeg',
                                                      ),'Analyse this image'
                                                  ],config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            ),
                                                  )
        return response.text
    except Exception as e:
        return f"Error during Gemini API call: {e}"


image_analyzer = Agent(
    name="image_analyzer",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="'''Analyze the image'''",
    tools=[analyze_image_from_url]
)


def extract_data_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):
    for content in llm_request.contents:
        if (content.role == "user" and
                len(content.parts) > 1 and
                content.parts[1].inline_data):
            excel_file_like_object = BytesIO(content.parts[1].inline_data.data)
            df = pd.read_excel(excel_file_like_object)
            markdown_output = df.to_markdown(index=False)
            content.parts[1] = types.Part.from_text(text=markdown_output)
            break
    return None

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a AGI",
    instruction="""
    Context : MCP Table Simulation<begin>
        tcin: 94663334, image_url: https://target.scene7.com/is/image/Target/GUEST_46b87607-f93d-40e7-8977-a49a4f4f5c50?wid=1200&hei=1200&qlt=80&fmt=webp
        tcin: 94635564, image_url: https://target.scene7.com/is/image/Target/GUEST_1b380e21-8aa6-4537-b776-bf6c510d992f?wid=1200&hei=1200&qlt=80&fmt=webp
    <end>
    
    From the document attached and by match the tcin with your MCP table and use the image_url with your tool agent 
    `image_analyzer` to validate the author,
    """,
    before_model_callback=extract_data_callback,
    tools=[agent_tool.AgentTool(image_analyzer)]
)
