#%%
import os
import numpy as np
import pandas as pd
import xgboost as xgb
from google.cloud import storage
from fastapi import Request, FastAPI

app = FastAPI()

AIP_PROJECT_NUMBER=os.getenv("AIP_PROJECT_NUMBER", "254356041555")
AIP_STORAGE_URI=os.getenv("AIP_STORAGE_URI", "gs://vtxdemos-models/wholesales/10-04-23/1/model")

buck = AIP_STORAGE_URI.split("/")[2]
blb = "/".join(AIP_STORAGE_URI.split("/")[3:])
model_file_name = "model.json"

blob = storage.Client(AIP_PROJECT_NUMBER).bucket(buck).blob(blb+"/model.json")
blob.download_to_filename(model_file_name)

model = xgb.XGBClassifier()
model.load_model(model_file_name)

@app.get(os.getenv("AIP_HEALTH_ROUTE", "/healthcheck"), status_code=200)
def read_root():
    return {"Hello": "World"}

@app.post(os.getenv("AIP_PREDICT_ROUTE", "/predict"), status_code=200)
async def predict(request: Request):
    body = await request.json()
    samples = body["instances"]
    pre = {k:v for i in samples for k,v in i.items()}
    input_array= pd.DataFrame(pre)
    predictions = model.predict(input_array).tolist()
    return {"predictions": predictions}