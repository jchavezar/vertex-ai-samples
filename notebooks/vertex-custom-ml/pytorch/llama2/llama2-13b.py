#%%
import os
import shutil
from tqdm import tqdm
from google.cloud import storage
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from transformers import AutoTokenizer, pipeline, logging
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

app = FastAPI()

AIP_PROJECT_NUMBER=os.getenv("AIP_PROJECT_NUMBER", "254356041555")
AIP_PREDICT_ROUTE=os.getenv("AIP_PREDICT_ROUTE", "/")
AIP_HEALTH_ROUTE=os.getenv("AIP_HEALTH_ROUTE", "/healthcheck")
AIP_STORAGE_URI=os.getenv("AIP_STORAGE_URI", "Llama-2-13B-chat-GPTQ")
LOCAL_MODEL_DIR="llama-2-13B-chat-gptq/"

print(AIP_HEALTH_ROUTE)
print(AIP_PREDICT_ROUTE)

os.mkdir(LOCAL_MODEL_DIR)
storage_client = storage.Client(AIP_PROJECT_NUMBER)
bucket = storage_client.bucket(AIP_STORAGE_URI.split("/")[2])
blobs = bucket.list_blobs(prefix=AIP_STORAGE_URI.split("/")[3])
for blob in blobs:
    print(f"Free Disk: {shutil.disk_usage(__file__)[2]/1024/1024/1024}")
    filename = blob.name.split("/")[-1]
    with open(LOCAL_MODEL_DIR+filename, "wb") as in_file:
        with tqdm.wrapattr(in_file, "write", total=blob.size, miniters=1, desc="Downloading") as destination_file_name:
            storage_client.download_blob_to_file(blob, destination_file_name) 
    
tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIR, use_fast=True)

model = AutoGPTQForCausalLM.from_quantized(LOCAL_MODEL_DIR,
        model_basename="model",
        use_safetensors=True,
        trust_remote_code=True,
        #device="cuda:0",
        use_triton=False,
        quantize_config=None,
        device_map="auto")
# %%
    
@app.get(AIP_HEALTH_ROUTE, status_code=200)
def health():
    return dict(status="healthy")

@app.post(AIP_PREDICT_ROUTE)
async def predict(request: Request, status_code=200):
    body = await request.json()
    prompt = body["instances"]
    
    system_message = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
    prompt_template=f'''[INST] <<SYS>>
    {system_message}
    <</SYS>>

    {prompt} [/INST]'''

    inputs = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    generated_ids = model.generate(inputs=inputs, temperature=0.7, max_new_tokens=254)
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    return JSONResponse({"predictions": response})