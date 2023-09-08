import os
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
    sample=body["instances"]
    input_dict = {name: tf.convert_to_tensor([value]) for name, value in sample.items()}
    predictions = model.predict(input_dict)
    prob = tf.nn.sigmoid(predictions[0])
    return {"predictions": f"Will buy on return probability: %.1f."  % (100 * prob)}