#%%
# Libraries
import os
from typing import List
import numpy as np
from onnxruntime import InferenceSession
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import storage

# Variables
MODEL_DIR = os.environ['AIP_STORAGE_URI']
BUCKET_NAME = MODEL_DIR.split('/')[2]
MODEL_SUF = '/'.join(MODEL_DIR.split('/')[2:])
MODEL_PATH = "/tmp/ecommerce.onnx"
AIP_HEALTH_ROUTE = os.environ['AIP_HEALTH_ROUTE']
AIP_PREDICT_ROUTE = os.environ['AIP_PREDICT_ROUTE']

# Download model to local pred-container
client = storage.Client()

print('\n\n\n')
print('begin')
for i in client.list_blobs(BUCKET_NAME, prefix=MODEL_DIR.split('/')[2]):
   print(i)
print('finish')
print(MODEL_SUF)
bucket = client.get_bucket(BUCKET_NAME)
blob = bucket.blob(f'{MODEL_SUF}/ecommerce.onnx')
blob.download_to_filename(MODEL_PATH)

# Variables
MODEL_DIR = os.environ['AIP_STORAGE_URI']
BUCKET_NAME = MODEL_DIR.split('/')[2]
MODEL_SUF = '/'.join(MODEL_DIR.split('/')[2:])
MODEL_PATH = "/tmp/ecommerce.onnx"
AIP_HEALTH_ROUTE = os.environ['AIP_HEALTH_ROUTE']
AIP_PREDICT_ROUTE = os.environ['AIP_PREDICT_ROUTE']

print(AIP_HEALTH_ROUTE)

#AIP_HEALTH_ROUTE = "/health"
#AIP_PREDICT_ROUTE = "/predict"

# initiate serving server
app = FastAPI(title="Serving Model")


# represent data point
class User(BaseModel):
   latest_ecommerce_progress: int
   bounces: int
   time_on_site: int
   pageviews: int
   source: str
   medium: str
   channel_grouping: str
   device_category: str
   country: str

# represent records
class Records(BaseModel):
   instances: List[User]


# load model
@app.on_event("startup")
def load_inference_session():
   global sess
   sess = InferenceSession(MODEL_PATH)


# check health
@app.get(AIP_HEALTH_ROUTE, status_code=200)
def health():
   return dict(status="healthy")

# get prediction
@app.post(AIP_PREDICT_ROUTE)
async def predict(records: Records, status_code=200):
   predictions = []
   for user in records.instances:
       # convert data to numpy array
       data = dict(
           latest_ecommerce_progress=np.array([[user.latest_ecommerce_progress]]),
           bounces=np.array([[user.bounces]]),
           time_on_site=np.array([[user.time_on_site]]),
           pageviews=np.array([[user.pageviews]]),
           source=np.array([[user.source]]),
           medium=np.array([[user.medium]]),
           channel_grouping=np.array([[user.channel_grouping]]),
           device_category=np.array([[user.device_category]]),
           country=np.array([[user.country]]),
       )
       predictions.append(sess.run([], data)[0].tolist())
   return dict(predictions=predictions)