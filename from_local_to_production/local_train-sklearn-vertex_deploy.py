#%%

## Loading data from BigQuery locally
from google.cloud import bigquery

client = bigquery.Client(project='jchavezar-demo')
sql = f"""
    SELECT * 
    FROM `jchavezar-demo.vertex_datasets_public.credit-openml`
"""
df = client.query(sql).to_dataframe()
X_raw = df.iloc[:,:-1]  # features (pandas DataFrame)
y_raw = df.target  # labels (pandas Series)
# %%
