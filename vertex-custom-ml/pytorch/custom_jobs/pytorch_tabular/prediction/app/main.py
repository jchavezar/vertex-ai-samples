import json
import os
import pandas as pd
from fastapi import Request, FastAPI
from pytorch_tabular import TabularModel

app = FastAPI()
columns = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/train.csv', nrows=0).iloc[:,:-1].columns.to_list()
loaded_model = TabularModel.load_from_checkpoint("../../training/tabular_random_model")

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
    data_pred = pd.DataFrame([instances],columns=columns)
    print(data_pred)
    outputs = loaded_model.predict(data_pred)
    response = outputs['prediction'].tolist()
    print("----------------- OUTPUTS -----------------")
    return {"predictions": response}