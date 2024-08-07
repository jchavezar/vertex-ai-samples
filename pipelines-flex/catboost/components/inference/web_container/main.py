# %%
import os
import argparse
import pandas as pd
from google.cloud import storage
from catboost import CatBoostClassifier
from fastapi import Request, FastAPI

parser = argparse.ArgumentParser(description='Catboost Inference')
parser.add_argument("--project-id", type=str, default="vtxdemos")
parser.add_argument("--aip-storage-uri")
args = parser.parse_args()

app = FastAPI()

AIP_PROJECT_NUMBER = args.project_id
AIP_STORAGE_URI = args.aip_storage_uri

buck = AIP_STORAGE_URI.split("/")[2]
blb = "/".join(AIP_STORAGE_URI.split("/")[3:])
model_file_name = "model.json"

blob = storage.Client(AIP_PROJECT_NUMBER).bucket(buck).blob(blb + "/model.json")
blob.download_to_filename(model_file_name)

cb_model: CatBoostClassifier = CatBoostClassifier()
cb_model.load_model(model_file_name)


@app.get(os.getenv("AIP_HEALTH_ROUTE", "/healthcheck"), status_code=200)
def read_root():
  return {"Hello": "World"}


@app.post(os.getenv("AIP_PREDICT_ROUTE", "/predict"), status_code=200)
async def predict(request: Request):
  body = await request.json()
  samples = body["instances"]
  pre = {k: v for i in samples for k, v in i.items()}
  input_array = pd.DataFrame(pre)
  input_array = input_array.reindex(sorted(input_array.columns), axis=1)
  predictions = cb_model.predict(input_array).tolist()
  return {"predictions": predictions}
