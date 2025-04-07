#%%
import openai
import google.auth
from io import BytesIO
from google.cloud import storage
from pdf2image import convert_from_path
from google.auth.transport import Request

user_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/The_Blue_Marble_%28remastered%29.jpg/580px-The_Blue_Marble_%28remastered%29.jpg"  # @param {type: "string"}
region = "us-central1"
project_num = "254356041555"
endpoint_id = "768396999606140928"
service_account_file = "/Users/jesusarguelles/Documents/vtxdemos-3ef37f9251ca.json"
endpoint_resource_name = f"projects/{project_num}/locations/{region}/endpoints/768396999606140928"
bucket_name = "vtxdemos-datasets-public"
bucket_folder = "sample_images"

base_url = (
    f"https://{region}-aiplatform.googleapis.com/v1beta1/{endpoint_resource_name}"
)

credentials, detected_project_id = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token


def upload_file_to_gcs(file_url: str):
    # Google Cloud Storage
    if file_url:
        pass
    else:
        file_url = "/Users/jesusarguelles/Downloads/sample_invoice.pdf"
    file_name = file_url.split('/')[-1]
    images = convert_from_path(file_url, first_page=1, last_page=1)
    image_bytes = BytesIO()
    images[0].save(image_bytes, "PNG")
    image_bytes = image_bytes.getvalue()
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    image_file = f"{file_name.split(".")[0]}.png"
    blob = bucket.blob(f"{bucket_folder}/{image_file}")
    blob.upload_from_string(image_bytes, content_type="image/png")
    return {"status": "ok", "file_name": f"https://storage.googleapis.com/{bucket_name}/{bucket_folder}/{image_file}"}

# OpenAI
client = openai.OpenAI(base_url=base_url, api_key=access_token)


def generate_content(file_uri: str) -> str:
    file = upload_file_to_gcs(file_uri)
    try:
        if file["status"] == "ok":
            model_response = client.chat.completions.create(
                model="",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": file["file_name"]}},
                            {"type": "text", "text": "Extract all the information from this document, do not miss anything"},
                        ],
                    }
                ]
            )
            return model_response.choices[0].message.content
    except Exception as e:
        return f"There was and Error: {e}"

def conversational_bot(prompt: str, history: str = None) -> str:
    if history is not None:
        prompt = f"File Extraction: {history}\nPrompt:{prompt}"
    else:
        prompt = prompt
    try:
        model_response = client.chat.completions.create(
            model="",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return model_response.choices[0].message.content
    except Exception as e:
        return f"There was an error: {e}"