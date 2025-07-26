#%%
from google.cloud import bigquery

client = bigquery.Client(project="vtxdemos")
df = client.query("select * from `vtxdemos.public.train_nlp` limit 2").to_dataframe()
 
# %%
print({"instances": [str(df.iloc[0,:]['text'])]})
# %%
