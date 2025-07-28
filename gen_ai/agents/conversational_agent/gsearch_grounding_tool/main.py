#%%
from google import genai
from fastapi import FastAPI
from pydantic import BaseModel
from google.genai import types
import base64

app = FastAPI()

project_id = "jesusarguelles-sandbox"
region = "us-central1"
model = "gemini-2.5-flash-preview-04-17"

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region,
)

system_instruction = """
you are grounding with google search as one of your tools, any response needs to come with citations links.
"""

tools = [
    types.Tool(google_search=types.GoogleSearch()),
]

generate_content_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    ),
    tools=tools
)

contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text="""what are the latest news""")
        ]
    )
]

def generate_response(prompt : str):
    try:
        response = client.models.generate_content(
            model=model,
            contents=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
            config=generate_content_config
        )
        grounding = [i.web.uri for i in response.candidates[0].grounding_metadata.grounding_chunks]
        response = response.text
        return {"response": response, "citations": grounding}

    except Exception as e:
        print(f"Error: {e}")
        return e

#%%
class Response(BaseModel):
    response: str
    citations: list

class QueryRequest(BaseModel):
    prompt: str

@app.post(
    "/agent_1",
    response_model = Response,
    response_description = "Response from Gemini including citations"
)
async def agent_generate_content(
        request: QueryRequest
):
    print(request)
    re = generate_response(request.prompt)
    return re