#%%
import os
from transformers import pipeline
from huggingface_hub import login
from fastapi import Request, FastAPI
from starlette.responses import JSONResponse

app = FastAPI()

unmasker = pipeline('fill-mask', model='bert-base-uncased')
unmasker("Hello I'm a [MASK] model.")
# %%

@app.get('/health_check')
def health():
    return 200
if os.environ.get('AIP_PREDICT_ROUTE') is not None:
    method = os.environ['AIP_PREDICT_ROUTE']
else:
    method = '/predict'
    
@app.post(method)
async def predict(request: Request):
    print("----------------- PREDICTING -----------------")
    body = await request.json()
    output=unmasker(body["instances"])
    return JSONResponse({"predictions": output})