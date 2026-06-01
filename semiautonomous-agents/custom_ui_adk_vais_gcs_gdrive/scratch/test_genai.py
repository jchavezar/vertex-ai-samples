import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]

print("Initializing GenAI client with location='global'...")
client = genai.Client(
    vertexai=True,
    project=PROJECT,
    location="global"
)

try:
    print("Sending generate_content request using gemini-3-flash-preview...")
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Hello",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_level="HIGH"
            )
        )
    )
    print("Success!")
    print("Thoughts:", response.candidates[0].thinking_process)
    print("Text:", response.text)
except Exception as e:
    logging.exception("Failed to query gemini-3-flash-preview via global")
