#%%
import vertexai
from vertexai.language_models import TextGenerationModel

vertexai.init(project="vtxdemos", location="us-central1")
parameters = {
    "temperature": 0.2,
    "max_output_tokens": 256,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison@001")
response = model.predict(
    """Summary the following:
American Sign Language (ASL) is a natural language that uses hand and arm movements, facial expressions, and body gestures to convey information. ASL is the predominant sign language of Deaf communities in the United States and most of Anglophone Canada. It is the primary language of many North Americans.
""",
    **parameters
)
print(f"Response from Model: {response.text}")
# %%
