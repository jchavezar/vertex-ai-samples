#%%
import base64
import requests
from PIL import Image
from io import BytesIO
from google.cloud import aiplatform
from google.cloud.aiplatform import Endpoint

model_name = "vilt-vqa"
model_id = "dandelin/vilt-b32-finetuned-vqa"
project_id = "jesusarguelles-sandbox"
region = "us-central1"
staging_bucket = "gs://jesusarguelles-staging"

aiplatform.init(project=project_id, location=region, staging_bucket=staging_bucket)

endpoint=Endpoint(endpoint_name=Endpoint.list(filter='display_name="vilt-vqa-endpoint"')[0].resource_name)
#%%

def download_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def image_to_base64(image, format="JPEG"):
    buffer = BytesIO()
    image.save(buffer, format=format)
    image_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_str

#image = download_image("http://images.cocodataset.org/val2017/000000039769.jpg")

image = Image.open("fridge.png")
display(image)

#%%
question = "List the food items by name in the image."
instances = [
    {"image": image_to_base64(image), "text": question},
]
preds = endpoint.predict(instances=instances).predictions
print(question)
print(preds)
# %%
