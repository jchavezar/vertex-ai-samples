import os
import numpy as np
import tensorflow as tf
from fastapi import Request, FastAPI

app = FastAPI()

model=tf.keras.models.load_model(os.environ["AIP_STORAGE_URI"]+"/model")

@app.get(os.environ["AIP_HEALTH_ROUTE"], status_code=200)
def read_root():
    return {"Hello": "World"}

@app.post(os.environ["AIP_PREDICT_ROUTE"], status_code=200)
async def predict(request: Request):
    body = await request.json()
    samples = body["instances"]
    
    pre = {k:v for i in samples for k,v in i.items()}
    input_array= {name: tf.convert_to_tensor(value) for name, value in pre.items()}
    predictions = model.predict(input_array)
    prob = tf.nn.sigmoid(predictions)
    return {"predictions": np.where(np.array(prob) > 0.5, 1,0).tolist()}