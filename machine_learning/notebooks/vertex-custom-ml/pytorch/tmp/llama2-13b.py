#%%
import os
import shutil
from tqdm import tqdm
import subprocess
from google.cloud import storage
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from transformers import AutoTokenizer, pipeline, logging
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

app = FastAPI()

print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))
print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))
print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))
print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))
print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))

AIP_PROJECT_NUMBER=os.getenv("AIP_PROJECT_NUMBER", "254356041555")
AIP_PREDICT_ROUTE=os.getenv("AIP_PREDICT_ROUTE", "/")
AIP_HEALTH_ROUTE=os.getenv("AIP_HEALTH_ROUTE", "/healthcheck")
AIP_STORAGE_URI=os.getenv("AIP_STORAGE_URI", "Llama-2-13B-chat-GPTQ")
LOCAL_MODEL_DIR="llama-2-13B-chat-gptq/"

# %%
    
@app.get(AIP_HEALTH_ROUTE, status_code=200)
def health():
    return dict(status="healthy")

@app.post(AIP_PREDICT_ROUTE)
async def predict(request: Request, status_code=200):
    body = await request.json()
    prompt = body["instances"]
    
    print(subprocess.check_output(["nvidia-smi"]).decode("utf-8"))


    return JSONResponse({"predictions": "test"})