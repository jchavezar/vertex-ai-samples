#%%
import json
import os
import pandas as pd
from fastapi import Request, FastAPI
from pytorch_tabular import TabularModel
from starlette.responses import JSONResponse

app = FastAPI()
#columns = pd.read_csv('gs://vtx-datasets-public/pytorch_tabular/synthetic/train.csv', nrows=0).iloc[:,:-1].columns.to_list()
loaded_model = TabularModel.load_from_checkpoint("tabular_random")
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
    #data_pred = pd.DataFrame.from_dict(instances)
    #print(data_pred)
    #outputs = loaded_model.predict(data_pred)
    #response = outputs['prediction'].tolist()[0]
    output = []
    for i in instances:
        output.append(float(loaded_model.predict(pd.DataFrame.from_dict(i))["prediction"][0]))
    print(output)
    print("----------------- OUTPUTS -----------------")
    #return {
    #    "predictions": [{"probability": response}]
    #    }
    return JSONResponse({"predictions": output})
