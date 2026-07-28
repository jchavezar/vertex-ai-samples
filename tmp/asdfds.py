#%%
from google import genai
from google.genai import types
import base64
import os

def generate():
    client = genai.Client(
        vertexai=True,
    )


    model = "gemini-3.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""hi""")
            ]
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature = 1,
        top_p = 0.95,
        seed = 0,
        max_output_tokens = 65535,
        safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )],
        thinking_config=types.ThinkingConfig(
            thinking_level="MEDIUM",
        ),
    )

    for chunk in client.models.generate_content_stream(
            model = model,
            contents = contents,
            config = generate_content_config,
    ):
        print(chunk.text, end="")

generate()