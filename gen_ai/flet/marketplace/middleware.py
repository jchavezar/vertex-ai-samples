from google.cloud import bigquery

project_id = "vtxdemos"
bq_table = "demos_us.etsy-embeddings-full-2-title"

bq_client = bigquery.Client(project=project_id)
df = bq_client.query(f"SELECT * FROM  `{bq_table}`").to_dataframe()

def search(query: str = ""):
  print("fk")

  return [{"title": row["ml_generate_text_llm_result"].strip() , "uri": row["public_cdn_link"]} for index, row in df.iterrows()]