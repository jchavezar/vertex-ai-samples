#%%
from time import time
import base64
from google.cloud import aiplatform

instances={"instances": ["a hamburguer with shrimp and cheese"]}

endpoint=aiplatform.Endpoint("projects/254356041555/locations/us-central1/endpoints/2543445272952832000")
start=time()
images=endpoint.predict(instances)
final_lap=time()-start
print(f"V100: {final_lap}")
with open("hamburguer-2.jpeg", "wb") as f:
    f.write(base64.b64decode(images.predictions[0]))


# %%
from time import time
import base64
from google.cloud import aiplatform

instances={"instances": ["a burger with cheese"]}

endpoint=aiplatform.Endpoint("projects/254356041555/locations/us-central1/endpoints/77724476967485440")
start=time()
images=endpoint.predict(instances)
final_lap=time()-start
print(f"L4: {final_lap}")
with open("hamburguer.jpeg", "wb") as f:
    f.write(base64.b64decode(images.predictions[0]))
# %%
