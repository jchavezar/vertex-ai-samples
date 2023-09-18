import os
import torch
import base64
import argparse
from io import BytesIO
from google.cloud import storage
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from diffusers import StableDiffusionXLPipeline

AIP_STORAGE_URI=os.getenv("AIP_STORAGE_URI")
MODEL_FILE_NAME=os.getenv("MODEL_FILE_NAME")

print(AIP_STORAGE_URI)
app = FastAPI()

AIP_PROJECT_NUMBER=os.getenv("AIP_PROJECT_NUMBER")
BUCKET_ID=AIP_STORAGE_URI.split("/")[2]
BLOB_ID="/".join(AIP_STORAGE_URI.split("/")[3:])+"/"+MODEL_FILE_NAME

print(BUCKET_ID)
print(BLOB_ID)

storage_client = storage.Client(AIP_PROJECT_NUMBER)
bucket = storage_client.bucket(BUCKET_ID)
blob = bucket.blob(BLOB_ID)
blob.download_to_filename(MODEL_FILE_NAME)
            
pipeline = StableDiffusionXLPipeline.from_single_file(
    MODEL_FILE_NAME,
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16",
    device="auto"
    )
pipeline.to("cuda")

@app.get(os.getenv("AIP_HEALTH_ROUTE"), status_code=200)
def health():
    return dict(status="healthy")

@app.post(os.getenv("AIP_PREDICT_ROUTE"))
async def predict(request: Request, status_code=200):
    body = await request.json()
    prompt = body["instances"]
    data_out=[]
    
    fp=BytesIO()
    #prompt = "A burger with shrimps and cottage cheese"
    image = pipeline(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
    image.save(fp, format="JPEG")
    data_out.append(base64.b64encode(fp.getvalue()).decode('utf-8'))
    fp.close()
    
    return JSONResponse({"predictions": data_out})