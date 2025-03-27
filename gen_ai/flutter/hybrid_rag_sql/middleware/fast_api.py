from google import genai
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

project_id = "vtxdemos"
region = "us-central1"
model_id = "gemini-2.0-flash-001"

app = FastAPI()

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=region,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
  text: str

@app.post("/process/")
async def process_text(item: Item):
  """
  Receives a string in JSON format, adds "processed" to it, and returns the modified string as JSON.
  """
  print(item)
  try:
    re = client.models.generate_content(
        model=model_id,
        contents=item
    )
    output = {"response": re.text}
  except Exception as e:
    output={"response": f"There was an error: {e}"}
  return output

