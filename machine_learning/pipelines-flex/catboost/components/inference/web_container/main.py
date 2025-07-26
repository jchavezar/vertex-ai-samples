# %%
import os
import pandas as pd
from google.cloud import storage
from catboost import CatBoostClassifier
from fastapi import Request, FastAPI

app = FastAPI()

AIP_PROJECT_NUMBER = os.getenv("CLOUD_ML_PROJECT_ID")
AIP_STORAGE_URI = os.getenv("AIP_STORAGE_URI")

buck = AIP_STORAGE_URI.split("/")[2]
blb = "/".join(AIP_STORAGE_URI.split("/")[3:])
model_file_name = "model.json"

blob = storage.Client(AIP_PROJECT_NUMBER).bucket(buck).blob(blb + "/model.json")
blob.download_to_filename(model_file_name)

cb_model: CatBoostClassifier = CatBoostClassifier()
cb_model.load_model(model_file_name, format="json")


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
