#%%
import csv
import io
import json
from google import genai
from google.genai import types
from google.cloud import storage

# inline_run
#%%
project = "jesusarguelles-sandbox"
region = "us-central1"
model_id = "gemini-2.5-pro-preview-05-06"
bucket_id = "jesusarguelles-datasets-public"

client = genai.Client(
    vertexai=True,
    project=project,
    location=region
)

storage_client = storage.Client(project=project)
bucket = storage_client.bucket(bucket_id)

def generate_synthetic_data(prompt: str):
    system_instruction="""
    You are an AI generator your main mission is to generate synthetic data with a randomness of 60% to make it more
    real, you will receive some possible columns in a paragraph that you need to use to create an output in the
    following json format:
    {
        "column_1": [List<String/Integer/or/Float>],
        "column_2": [List<String/Integer/or/Float>],
        "column_3": [List<String/Integer/or/Float>],
        ...,
        "column_n": [List<String/Integer/or/Float>]
    }
    
    Additional Instructions:
    - If you dont get the number of rows in the prompt use the default: 20 rows.
    - The json format is to create a table so each element position in the list needs to match with the position in 
    another column. (try to make the response verbose so I can use this data for RAG).
    """
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type = "application/json",
    )

    re = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=config,
    )

    return re.text

# inline_run
#%%
user_prompt = """Generate the following FAQ synthetic data with the following columns: question, answer, title, url.
The synthetic data needs to be synthetic Q&A about pixel 9 pro and apple iphone 16, samsung galaxy 25, do 50 rows.
"""

response = generate_synthetic_data(user_prompt)
print(response)

# inline_run
#%%
dictionary_response = json.loads(response)

headers = list(dictionary_response.keys())
num_rows = 0
if headers:
    num_rows = len(dictionary_response[headers[0]])

csv_output = io.StringIO()
writer = csv.writer(csv_output)

writer.writerow(headers)

for i in range(num_rows):
    row = [dictionary_response[header][i] for header in headers]
    writer.writerow(row)

csv_data =csv_output.getvalue()
csv_output.close()

blob = bucket.blob("synthetic_data_mobile_3.csv")
blob.upload_from_string(csv_data, content_type="text/csv")

print("done")