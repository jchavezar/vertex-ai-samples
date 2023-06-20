#%%
import torch
from diffusers import StableDiffusionPipeline

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "a photo of an astronaut riding a horse on mars"

results = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=7.5)
images = results.images
nsfw_detects = results.nsfw_content_detected
display(images[0])
print(nsfw_detects[0])


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

aip.init(project="vtxdemos")
aip.Endpoint.list(project="vtxdemos")[0].resource_name

endpoint = aip.Endpoint(endpoint_name=aip.Endpoint.list(project="vtxdemos")[0].resource_name)

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





# %%
