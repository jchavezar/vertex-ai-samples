#%%
from google import genai
from google.genai import types
from markitdown import MarkItDown

project_id = "jesusarguelles-sandbox"
region = "us-central1"
model_id = "gemini-2.5-flash-preview-04-17"

md = MarkItDown(enable_plugins=False)
result = md.convert("GenerativeAI_tweets.csv")

print(result.text_content)

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region
)

re = client.models.generate_content(
    model=model_id,
    contents=f"what is the following about?: {result.text_content}"
)

print(re.text)

