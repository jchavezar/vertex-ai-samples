#%%
from google import genai
from google.genai import types

project_id = "jesusarguelles-sandbox"
region = "us-central1"
model = "gemini-2.5-flash-preview-05-20"

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region,
)

tools = [
    types.Tool(google_search=types.GoogleSearch()),
]

_response = client.models.generate_content(
    model=model,
    contents="""
    Get statistics from the 2025 UEFA Nations League final,
    Output in JSON format
    """,
    config=types.GenerateContentConfig(
        tools=tools,
    )
)

import json
print(json.loads(_response.text.replace("```json", "").replace("```", "")))