#%%
from google import genai
from google.genai import types
from pydantic import BaseModel
from utils import plot_bounding_boxes

project="vtxdemos"
location="us-central1"
model_id="gemini-2.5-flash"

client = genai.Client(
    vertexai=True,
    project=project,
    location=location,
)

class BoundingBox(BaseModel):
    box_2d: list[int]
    label: str

config = types.GenerateContentConfig(
    system_instruction="""Return bounding boxes as an array with labels. Never return masks. Limit to 25 objects.
    If an object is present multiple times, give each object a unique label according to its distinct characteristics (colors, size, position, etc..).""",
    temperature=0.5,
    response_mime_type="application/json",
    response_schema=list[BoundingBox],
)

image_uri = "https://storage.googleapis.com/generativeai-downloads/images/Cupcakes.jpg"
prompt = "Detect the 2d bounding boxes of the cupcakes (with `label` as topping description)"  # @param {type:"string"}

response = client.models.generate_content(
    model=model_id,
    contents=[
        prompt,
        types.Part.from_uri(
            file_uri=image_uri,
            mime_type="image/jpeg",
        ),
    ],
    config=config,
)

print(response.text)

#%%
image = plot_bounding_boxes(image_uri, response.parsed)
image.show()