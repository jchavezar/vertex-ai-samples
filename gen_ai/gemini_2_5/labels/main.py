#%%
import os
from google import genai

# Note: Set ENV Variables before running (GOOGLE_CLOUD_PROJECT & GOOGLE_LOCATION)

MODEL_ID = "gemini-2.5-flash"

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_LOCATION"),
)

for i in range(100):
    re = client.models.generate_content(
        model=MODEL_ID,
        contents="Who won last night in MLB?",
        config=genai.types.GenerateContentConfig(
            labels={
                "experience": "recruit",
                "grounding": "yes",
                "google_search": "yes"
            },
            tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())]
        )
    )
    print(re.text)