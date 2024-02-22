import os
import numpy as np
import tensorflow as tf
from fastapi import Request, FastAPI

app = FastAPI()

@app.get(os.environ["AIP_HEALTH_ROUTE"], status_code=200)
def read_root():
    return {"Hello": "World"}

@app.post(os.environ["AIP_PREDICT_ROUTE"], status_code=200)
async def predict(request: Request):
    body = await request.json()
    samples = body["instances"]

    pre = {k: v for i in samples for k, v in i.items()}
    input_array = {name: tf.convert_to_tensor(value) for name, value in pre.items()}
    predictions = str(input_array.keys())
    return {"predictions": [predictions]}