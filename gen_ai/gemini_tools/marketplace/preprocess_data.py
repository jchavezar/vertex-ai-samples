import vertexai
from google.cloud import bigquery
from vertexai.resources.preview import feature_store

project_id = "vtxdemos"
#%%

bq_client = bigquery.Client(project=project_id)

sql_query = """
CREATE OR REPLACE TABLE `demos_us.etsy_embeddings_v1_1` AS (
SELECT 
    *
FROM
  ML.GENERATE_EMBEDDING( MODEL `demos_us.text_embedding_044`,
    (
    SELECT
      *,
      CASE
        WHEN title IS NULL AND listing_id IS NULL AND description IS NULL AND price_usd IS NULL AND tags IS NULL AND materials IS NULL AND attributes IS NULL AND category IS NULL THEN "" -- All NULL, return empty string
        ELSE 
          CASE WHEN title IS NOT NULL THEN "Product Title: " || CAST(title AS STRING) || " " ELSE "" END ||
          CASE WHEN listing_id IS NOT NULL THEN "Product Listing id: " || CAST(listing_id AS STRING) || " " ELSE "" END ||
          CASE WHEN description IS NOT NULL THEN "Product Description: " || CAST(description AS STRING) || " " ELSE "" END ||
          CASE WHEN price_usd IS NOT NULL THEN "Price: " || CAST(price_usd AS STRING) || " " ELSE "" END ||
          CASE WHEN tags IS NOT NULL THEN "Product Tags: " || CAST(tags AS STRING) || " " ELSE "" END ||
          CASE WHEN materials IS NOT NULL THEN "Product Materials: " || CAST(materials AS STRING) || " " ELSE "" END ||
          CASE WHEN attributes IS NOT NULL THEN "Product Attributes: " || CAST(attributes AS STRING) || " " ELSE "" END ||
          CASE WHEN category IS NOT NULL THEN "Product Category: " || CAST(category AS STRING) ELSE "" END
      END AS content
    FROM
      `demos_us.etsy_10k`)  )
)
"""

bq_client.query(sql_query).result()


#%%
vertexai.init(project=project_id, location="us-east1")
fos = feature_store.FeatureOnlineStore("projects/254356041555/locations/us-east1/featureOnlineStores/feature_store_marketplace")

bigquery_source = feature_store.utils.FeatureViewBigQuerySource(
    uri="bq://vtxdemos.demos_us.etsy_embeddings_v1_1",
    entity_id_columns=["listing_id"],
)
index_config = feature_store.utils.IndexConfig(
    embedding_column="ml_generate_embedding_result",
    dimensions=768,
    algorithm_config=feature_store.utils.TreeAhConfig(),
)

fv = fos.create_feature_view(
    name="etsy_view_text_v1_1",
    source=bigquery_source,
    index_config=index_config,
)
#%%
sync_response = fv.sync()

import time

start_time = time.time()
while True:
    feature_view_sync = fv.get_sync(
        sync_response.resource_name.split("/")[9]
    ).gca_resource
    if feature_view_sync.run_time.end_time.seconds > 0:
        status = "Succeed" if feature_view_sync.final_status.code == 0 else "Failed"
        print(f"Sync {status} for {feature_view_sync.name}. \n {feature_view_sync}")
        # wait a little more for the job to properly shutdown
        time.sleep(30)
        break
    else:
        print("Sync ongoing, waiting for 30 seconds.")
    time.sleep(30)
print(time.time() - start_time)