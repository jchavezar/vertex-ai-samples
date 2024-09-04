import os
import jax
import json
import time
import pickle
import pandas as pd
import jax.numpy as jnp
import snowflake.connector
from jax import random, vmap
from jax.scipy.special import logsumexp
from jax.example_libraries import optimizers
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from google.cloud import bigquery, storage, secretmanager

secret_id = os.environ.get('SECRET_ID', 'projects/254356041555/secrets/snow_pass/versions/1')

# Reading from SnowFlake
client = secretmanager.SecretManagerServiceClient()
name = secret_id
response = client.access_secret_version(name=name)
data = response.payload.data.decode('UTF-8')
data = json.loads(data)

con = snowflake.connector.connect(
    user=data["user"],
    password=data["pass"],
    account=data["account"],
    warehouse='COMPUTE_WH',
    database='ECOMMERCE',
    schema='PUBLIC',
    role='ACCOUNTADMIN'
)

cur = con.cursor()
cur.execute("SELECT * FROM ECOMMERCE_BALANCED")
columns = [desc[0].lower() for desc in cur.description]
data_fetch = cur.fetchall()
df = pd.DataFrame(data_fetch, columns=columns)

# Encode categorical columns
categorical_cols = df.select_dtypes(include='object').columns
encoders = {}
for col in categorical_cols:
  encoders[col] = LabelEncoder().fit(df[col])
  df[col] = encoders[col].transform(df[col])

# Save encoders for later use
with open('encoders.pkl', 'wb') as f:
  pickle.dump(encoders, f)

# Prepare data for training
X = df.drop("will_buy_on_return_visit", axis=1).fillna(0).astype('int64')
y = df["will_buy_on_return_visit"].fillna(0).astype('int64')

X_columns = X.columns.tolist()  # Get the column names as a list
with open('X_columns.pkl', 'wb') as f:
  pickle.dump(X_columns, f)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=104)

# Convert to JAX arrays
X_train, X_test, y_train, y_test = map(jnp.array, (X_train, X_test, y_train, y_test))

# Hyperparameters
layer_sizes = [9, 128, 256, 2]
step_size = 0.001   # learning rate
num_epochs = 200  # Increased epochs
batch_size = 32
n_targets = 2
l2_lambda = 0.05  # L2 regularization strength

# Initialize the optimizer
opt_init, opt_update, get_params = optimizers.adam(step_size)


def initialize_everything(seed=42):
  """Initializes neural network parameters and optimizer state."""
  global params, opt_state

  key = random.PRNGKey(seed)

  def random_layer_params(m, n, key, scale=1e-2):
    w_key, b_key = random.split(key)
    return scale * random.normal(w_key, (n, m)), scale * random.normal(b_key, (n,))

  def init_network_params(sizes, key):
    keys = random.split(key, len(sizes))
    return [random_layer_params(m, n, k) for m, n, k in zip(sizes[:-1], sizes[1:], keys)]

  params = init_network_params(layer_sizes, key)
  opt_state = opt_init(params)

  return params, opt_state


# Utility functions
def one_hot(x, k, dtype=jnp.float32):
  return jnp.array(x[:, None] == jnp.arange(k), dtype)

def relu(x):
  return jnp.maximum(0, x)

def dropout(x, rate, key):
  """Applies dropout to the input tensor."""
  keep_prob = 1.0 - rate
  mask = random.bernoulli(key, keep_prob, shape=x.shape)
  return (x * mask) / keep_prob

def predict(params, image, key=None, is_training=False):
  """Computes predictions with optional dropout."""
  activations = image
  for i, (w, b) in enumerate(params[:-1]):
    outputs = jnp.dot(w, activations) + b
    activations = relu(outputs)

    if is_training:
      key, subkey = random.split(key)
      activations = dropout(activations, rate=0.5, key=subkey)

  final_w, final_b = params[-1]
  logits = jnp.dot(final_w, activations) + final_b
  return logits - logsumexp(logits)

batched_predict = vmap(predict, in_axes=(None, 0, None, None))

def accuracy(params, images, targets, key=None, is_training=False):
  """Calculates accuracy."""
  target_class = jnp.argmax(targets, axis=1)
  predicted_class = jnp.argmax(batched_predict(params, images, key, is_training), axis=1)
  return jnp.mean(predicted_class == target_class)

def loss(params, images, targets, key=None, is_training=False):
  """Calculates the loss with L2 regularization."""
  preds = batched_predict(params, images, key, is_training)
  cross_entropy_loss = -jnp.mean(preds * targets)
  l2_penalty = sum(jnp.sum(w**2) for w, b in params)
  return cross_entropy_loss + l2_lambda * l2_penalty

# Initialize accuracy lists
train_accuracies = []
test_accuracies = []

# Initialize parameters and optimizer state
params, opt_state = initialize_everything(seed=42)

# Training loop
key = random.PRNGKey(42)
for epoch in range(num_epochs):
  start_time = time.time()

  # Shuffle training data
  perm = random.permutation(key, len(X_train))
  X_train = X_train[perm]
  y_train = y_train[perm]

  for i in range(0, len(X_train), batch_size):
    x_batch = X_train[i:i+batch_size]
    y_batch = one_hot(y_train[i:i+batch_size], n_targets)

    key, subkey = random.split(key)
    params = get_params(opt_state)

    loss_value, grads = jax.value_and_grad(loss)(params, x_batch, y_batch, subkey, True)
    opt_state = opt_update(epoch * len(X_train) // batch_size + i // batch_size, grads, opt_state)

  epoch_time = time.time() - start_time

  # Evaluate accuracy (no dropout during evaluation)
  params = get_params(opt_state)
  train_acc = accuracy(params, X_train, one_hot(y_train, n_targets))
  test_acc = accuracy(params, X_test, one_hot(y_test, n_targets))
  train_accuracies.append(train_acc)
  test_accuracies.append(test_acc)
  print(f"Epoch {epoch+1}/{num_epochs}, Train acc: {train_acc:.3f}, Test acc: {test_acc:.3f}")

trained_params = get_params(opt_state)
with open('trained_params.pkl', 'wb') as f:
  pickle.dump(trained_params, f)

# Uploading Artifacts
model_uri = os.getenv("AIP_MODEL_DIR", "vtxdemos-models")
if "gs" in model_uri:
  bucket = model_uri.split("/")[2]
  suffix_file_name = "/".join(model_uri.split("/")[3:])
else:
  bucket = model_uri
  suffix_file_name = "tmp/model/"

for filename in os.listdir():
  if filename.endswith(".pkl"):
    print(suffix_file_name)
    storage.Client(project=os.getenv("CLOUD_ML_PROJECT_ID", "vtxdemos")).bucket(bucket).blob(suffix_file_name+filename).upload_from_filename(filename)