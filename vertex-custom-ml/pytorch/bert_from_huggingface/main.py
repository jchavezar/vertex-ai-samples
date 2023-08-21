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

@app.get(os.environ['AIP_HEALTH_ROUTE'], status_code=200)
def health():
    return dict(status="healthy")
    
@app.post(os.environ['AIP_PREDICT_ROUTE'], status_code=200)
async def predict(request: Request):
    print("----------------- PREDICTING -----------------")
    body = await request.json()
    output=unmasker(body["instances"])
    return JSONResponse({"predictions": output})