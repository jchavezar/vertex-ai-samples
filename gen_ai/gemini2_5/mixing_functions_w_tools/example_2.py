#%%
import json
from google import genai
from google.genai import types

project_id = "jesusarguelles-sandbox"
region = "us-central1"
model = "gemini-2.5-flash-preview-05-20"

client = genai.Client(vertexai=True, project=project_id, location=region)


get_info_internet = types.FunctionDeclaration(
    name="get_info_internet",
    description="A single source of true information function",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
)

structure_output = types.FunctionDeclaration(
    name="structure_output",
    description="Output format after using single source of true",
    parameters = {
    "type": "object",
    "properties": {
        "team_names": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "date": {
            "type": "string",
            "format": "date"
        },
        "final_score": {
            "type": "string"
        }
    },
    "required": [
        "team_names",
        "date",
        "final_score"
    ]
    }
)

tools = types.Tool(
    function_declarations=[
        get_info_internet,
        structure_output
    ],
)

def google_search(query: str):
    response = client.models.generate_content(
        model=model, contents=query, config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            )
        )
    )
    return response.text

_response = client.models.generate_content(
    model=model,
    contents=types.Content(
        role="user", parts=[types.Part.from_text(text="""
    Get statistics from the 2025 UEFA Nations League final using 
    get_info_internet tool, and use the answer with structure_output tool
    """)]
    ),
    config=types.GenerateContentConfig(
        tools=[tools],
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        )
    ),
)

#%%
if _response.function_calls[0].name == "get_info_internet":
    _=google_search(query=_response.function_calls[0].args["query"])

    _response = client.models.generate_content(
        model=model,
        contents=types.Content(
            role="user", parts=[
                types.Part.from_text(
                    text="""
                    Get statistics from the 2025 UEFA Nations League final using 
                    get_info_internet tool, and use the answer with structure_output tool
                    """
                ),
                types.Part.from_text(text=_)
            ]
        ),
        config=types.GenerateContentConfig(
            tools=[tools],
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            )
        ),
    )

print(_response.function_calls)



