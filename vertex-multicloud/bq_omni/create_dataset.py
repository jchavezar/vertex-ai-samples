#%%

from google.cloud.bigquery import Client, QueryJobConfig
client = Client(project="vtxdemos")

datasets = ["vtxdemos.public.train_dataset", "vtxdemos.public.eval_dataset"]

for n,dataset in enumerate(datasets):
    query = [f"""SELECT * FROM `{dataset}`"""]
    job = client.query(query)
    df = job.to_dataframe()
    df.to_csv(f"{datasets[n].split('.')[2]}.csv", index=False)
# %%

## Copy to AWS
import pandas as pd
import boto3
s3 = boto3.client('s3')

for i in datasets:
    s3.upload_file(f"{i.split('.')[2]}.csv", 'sockcop-datasets-public', f"{i.split('.')[2]}.csv")
# %%