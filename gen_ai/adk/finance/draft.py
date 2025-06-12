#%%
import json

from google.cloud import storage

project_id = "vtxdemos"
bucket = "vtxdemos-datasets-public"

client = storage.Client(
    project=project_id
)

bucket = client.bucket(bucket_name=bucket)

for i in bucket.list_blobs(prefix="finance"):
    if "json" in i.name:
        print(i.name)
        blob = bucket.blob(i.name)
        json_data_string = blob.download_as_text()
        data = json.loads(json_data_string)
        print(data)

