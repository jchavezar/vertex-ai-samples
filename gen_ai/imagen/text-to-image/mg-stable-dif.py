#%%
#import torch
#from diffusers import StableDiffusionPipeline


##############
#%%
import base64
import glob
import os
from datetime import datetime
from io import BytesIO
from google.cloud import aiplatform as aip

import requests
from google.cloud import aiplatform, storage
from PIL import Image

def download_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def image_to_base64(image, format="JPEG"):
    buffer = BytesIO()
    image.save(buffer, format=format)
    image_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image_str

def base64_to_image(image_str):
    image = Image.open(BytesIO(base64.b64decode(image_str)))
    return image

init_image = download_image(
    "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"
)
display(init_image)
instances = [
    {
        "prompt": "A fantasy landscape, trending on artstation",
        "image": image_to_base64(init_image),
    },
]
#%%
PROJECT_ID = "cloud-llm-preview1"
aip.init(project=PROJECT_ID)
aip.Endpoint.list(project=PROJECT_ID)[0].resource_name
endpoint = aip.Endpoint(endpoint_name="projects/801452371447/locations/us-central1/endpoints/1535793443631005696")

#%%
response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])


# %%
instances = [
    {
        "prompt": "A futuristic city with a robot helping humanity",
        "image": image_to_base64(init_image),
    },
]

response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])
# %%
instances = [
    {
        "prompt": "a store front that has the word ‘openai’ written on it. . . .",
        "image": image_to_base64(init_image),
    },
]

response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])

#%%
instances = [
    {
        "prompt": "an armchair in the shape of an avocado. . . .",
        "image": image_to_base64(init_image),
    },
]

response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])


# %%

instances = [
    {
        "prompt": "Hackers may have possibly stolen roughly $320 million",
        "image": image_to_base64(init_image),
    },
]

response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])
# %%


#############################

#%%
PROJECT_ID = "cloud-llm-preview1"
aip.init(project=PROJECT_ID)
aip.Endpoint.list(project=PROJECT_ID)[0].resource_name
endpoint = aip.Endpoint(endpoint_name="projects/801452371447/locations/us-central1/endpoints/1535793443631005696")

with open('bedroom.jpg', 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read())

#%%

instances = [
    {
        "prompt": "same image more futuristic",
        "image": encoded_string.decode("utf-8"),
    },
]

response = endpoint.predict(instances=instances)
images = [base64_to_image(image) for image in response.predictions]
display(images[0])
    

# %%
images_ = image_to_base64(init_image)
images_
# %%
