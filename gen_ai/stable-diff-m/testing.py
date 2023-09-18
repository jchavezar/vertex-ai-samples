#%%
import base64
from google.cloud import aiplatform

instances={"instances": ["a hamburguer with shrimp"]}

endpoint=aiplatform.Endpoint("projects/254356041555/locations/us-central1/endpoints/7541314959427239936")
images=endpoint.predict(instances)

with open("hamburguer.jpeg", "wb") as f:
    f.write(base64.b64decode(images.predictions[0]))


# %%
