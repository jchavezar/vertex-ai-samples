#%%
from google.cloud import storage

client = storage.Client(project="vtxdemos")

list(client.bucket("vtxdemos-datasets-public").list_blobs())
# %%
