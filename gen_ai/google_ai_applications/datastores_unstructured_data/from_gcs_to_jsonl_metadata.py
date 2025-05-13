#%%
import json
from google import genai
from google.genai import types
from google.cloud import storage

project = "jesusarguelles-sandbox"
region = "us-central1"
bucket_name = "jesusarguelles-dataset-private"
bucket_folder = "deloitte_data_extraction"
gemini_model = "gemini-2.0-flash-lite-001"

gemini_client = genai.Client(
    vertexai=True,
    project=project,
    location=region
)

st_client = storage.Client(
    project=project,
)

bucket = st_client.bucket(bucket_name)
blobs = bucket.list_blobs(prefix=bucket_folder)

#%%
# Gemini Config
config = types.GenerateContentConfig(
    system_instruction="""
    System Role: Creative Title Generator.
    Input: Text.
    Task: Generate a short, concise title representing the entirety of the input text.
    Output Specification: Raw format, containing only the generated title.
    """
)

# Function to create metadata
def generate(prompt: str) -> str:
    re = gemini_client.models.generate_content(
        model=gemini_model,
        contents=f"Input: {prompt}",
        config=config,
    )
    return re.text.strip().replace("\\n","")

n = 0
with open("dataset.jsonl", "w") as f:
    for blob in blobs:
        if "pdf" in blob.name:
            n+=1
            f.write(
                json.dumps(
                    {
                        "id": str(n),
                        "structData": {
                            "title": generate(blob.name),
                            "category": ["gartner_document"],
                            "time_created": str(blob.time_created),
                        },
                        "content": {"mimeType": "application/pdf", "uri": f"gs://{bucket_name}/{blob.name}"}
                    }
                ) + "\n"
            )


#%%
bucket.blob(f"{bucket_folder}/dataset.jsonl").upload_from_filename("dataset.jsonl")