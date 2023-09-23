#%%
import json
import os
import pandas as pd
from google.cloud import storage
from fastapi import Request, FastAPI
from pytorch_tabular import TabularModel
from starlette.responses import JSONResponse

app = FastAPI()

storage_client = storage.Client(os.getenv("AIP_PROJECT_NUMBER"))
bucket = storage_client.bucket(os.getenv("AIP_STORAGE_URI").split("/")[2])
blobs = bucket.list_blobs(prefix=os.getenv("AIP_STORAGE_URI").split("/")[3])

bucket = storage.Client().bucket(bucket)
blob_names = list(bucket.list_blobs())

os.mkdir("/model")
for blob in blob_names:
    filename = blob.name.split("/")[-1]
    if filename == "":
        continue
    blob.download_to_filename(f"/model/{filename}")
    
loaded_model = TabularModel.load_from_checkpoint("/model")
#%%
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
    instances = body["instances"]
    output = []
    for i in instances:
        output.append(float(loaded_model.predict(pd.DataFrame.from_dict(i))["prediction"][0]))
    print(output)
    print("----------------- OUTPUTS -----------------")
    return JSONResponse({"predictions": output})