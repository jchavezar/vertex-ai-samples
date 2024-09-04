import os
import jax
import pickle
import jax.numpy as jnp
from google.cloud import storage
from fastapi import Request, FastAPI
from jax.scipy.special import logsumexp

app = FastAPI()

AIP_PROJECT_NUMBER = os.getenv("AIP_PROJECT_NUMBER")
AIP_STORAGE_URI = os.getenv("AIP_STORAGE_URI")

buck = AIP_STORAGE_URI.split("/")[2]
blb = "/".join(AIP_STORAGE_URI.split("/")[3:])
model_file_name = "model.json"

bucket = storage.Client(AIP_PROJECT_NUMBER).bucket(buck)
print("working")
pkl_files = ["X_columns.pkl", "encoders.pkl", "trained_params.pkl"]

for i in pkl_files:
  bucket.blob(blb+"/"+i).download_to_filename(i)

# Load the saved encoders and model parameters
with open('encoders.pkl', 'rb') as f:
  encoders = pickle.load(f)
with open('trained_params.pkl', 'rb') as f:
  trained_params = pickle.load(f)
with open('X_columns.pkl', 'rb') as f:
  X_columns = pickle.load(f)

print(X_columns)
def relu(x):
  return jnp.maximum(0, x)

# Jax Function Predictions
def predict(params, image, key=None, is_training=False):
  """Computes predictions with optional dropout."""
  activations = image
  for i, (w, b) in enumerate(params[:-1]):
    outputs = jnp.dot(w, activations) + b
    activations = relu(outputs)
  final_w, final_b = params[-1]
  logits = jnp.dot(final_w, activations) + final_b
  return logits - logsumexp(logits)

batched_predict = jax.vmap(predict, in_axes=(None, 0, None, None))

# def predict_from_dict(data_dict, params, X_columns):
#   """Makes a prediction from a dictionary of raw data."""
#   input_data = [encoders[col].transform([data_dict[col]])[0] if col in encoders
#                 else data_dict[col] for col in X_columns]
#   print("work?")
#   print(input_data)
#   input_array = jnp.array(input_data).reshape(1, -1)
#   predictions = batched_predict(params, input_array, None, False)
#   predicted_class = jnp.argmax(predictions)
#   probability = jnp.exp(predictions[0, 1])
#   print(probability)
#   return predicted_class, probability

def predict_from_dict(data_dicts, params, X_columns):
  """Makes predictions from a list of dictionaries of raw data."""
  input_data = []
  for data_dict in data_dicts:
    input_data.append([encoders[col].transform([data_dict[col]])[0] if col in encoders
                       else data_dict[col] for col in X_columns])

  input_array = jnp.array(input_data)  # Shape: (num_dicts, num_features)
  predictions = batched_predict(params, input_array, None, False)  # Use batched_predict here
  predicted_classes = jnp.argmax(predictions, axis=1)
  probabilities = jnp.exp(predictions[:, 1])  # Assuming class 1 is the positive class
  return predicted_classes, probabilities

@app.get(os.getenv("AIP_HEALTH_ROUTE", "/healthcheck"), status_code=200)
def read_root():
  return {"Hello": "World"}

@app.post(os.getenv("AIP_PREDICT_ROUTE", "/predict"), status_code=200)
async def predict(request: Request):
  body = await request.json()
  samples = body["instances"]
  # pre = {k: v for i in samples for k, v in i.items()}
  # print(pre)
  # Make the prediction
  predicted_class, probability = predict_from_dict(samples, trained_params, X_columns)
  predictions = [str(i) for i in predicted_class]

  return {"predictions": predictions}
