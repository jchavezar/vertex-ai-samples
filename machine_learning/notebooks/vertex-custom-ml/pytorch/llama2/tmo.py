#%%
import os
from tqdm import tqdm
from google.cloud import storage
client = storage.Client(project="vtxdemos")
bucket= client.bucket("vtxdemos-models")
blob=bucket.blob("llama-2-13B-chat-gptq/tokenizer_config.json")

with open("/tmp/tokenizer_config.json", "wb") as f:
    with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
        client.download_blob_to_file(blob, file_obj)
# %%
