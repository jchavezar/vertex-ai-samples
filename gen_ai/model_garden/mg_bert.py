#%%

import pandas as pd
import json

# %%
from google.cloud import storage

client = storage.Client(project='vtxdemos')
bucket = client.bucket('vtxdemos-datasets-public')
blob = bucket.blob('train.jsonl')

with open("train.jsonl", "wb") as f:
    blob.download_to_file(f)
# %%

with open("train.jsonl", "r") as f:
    for i in f:
        print(i)
        break


# %%
