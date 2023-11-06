#%%
import os, glob
from tqdm import tqdm
from google.cloud import storage
from fastapi import FastAPI, Request
from utils.tokenizer import ExLlamaTokenizer
from utils.generator import ExLlamaGenerator
from starlette.responses import JSONResponse
from utils.model import ExLlama, ExLlamaCache, ExLlamaConfig

app = FastAPI()

AIP_PROJECT_NUMBER=os.getenv("AIP_PROJECT_NUMBER", "254356041555")
AIP_PREDICT_ROUTE=os.getenv("AIP_PREDICT_ROUTE", "/predict")
AIP_HEALTH_ROUTE=os.getenv("AIP_HEALTH_ROUTE", "/healthcheck")

print("-"*50)
print(os.getenv("AIP_STORAGE_URI"))
print(os.getenv("AIP_STORAGE_DIR"))
print("-"*50)

print("storage_dir")
print(os.listdir(os.getenv("AIP_STORAGE_DIR")))
print("storage_dir")

LOCAL_MODEL_DIR=os.getenv("AIP_STORAGE_DIR")
tokenizer_path = os.path.join(LOCAL_MODEL_DIR, "tokenizer.model")
model_config_path = os.path.join(LOCAL_MODEL_DIR, "config.json")
st_pattern = os.path.join(LOCAL_MODEL_DIR, "*.safetensors")
model_path = glob.glob(st_pattern)


# Create config, model, tokenizer and generator

config = ExLlamaConfig(model_config_path)               # create config from config.json
config.model_path = model_path                          # supply path to model weights file
config.set_auto_map("17.2,24")

model = ExLlama(config)                                 # create ExLlama instance and load the weights
tokenizer = ExLlamaTokenizer(tokenizer_path)            # create tokenizer from tokenizer model file

cache = ExLlamaCache(model)                             # create cache for inference
generator = ExLlamaGenerator(model, tokenizer, cache)   # create generator

# Configure generator

generator.disallow_tokens([tokenizer.eos_token_id])

generator.settings.token_repetition_penalty_max = 1.2
generator.settings.temperature = 0.95
generator.settings.top_p = 0.75
generator.settings.top_k = 0
generator.settings.typical = 0.5
    
@app.get(AIP_HEALTH_ROUTE, status_code=200)
def health():
    return dict(status="healthy")

@app.post(AIP_PREDICT_ROUTE)
async def predict(request: Request, status_code=200):
    body = await request.json()
    prompt = body["instances"]
    
    output = generator.generate_simple(prompt, max_new_tokens = 200)
    
    print("-"*80)
    print("Response")
    print(output)
    print("-"*80)
    print(type(output))
    
    return JSONResponse({"predictions": [output]})
# %%
