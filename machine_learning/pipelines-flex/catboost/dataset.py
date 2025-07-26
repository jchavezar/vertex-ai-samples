from google.cloud import bigquery

client = bigquery.Client(project="vtxdemos")

query = f"""
    WITH data AS (
      SELECT *, RAND() AS random_value
      FROM `vtxdemos.demos_us.ecommerce_balanced`
    )
    
    SELECT *, 
      CASE 
        WHEN random_value < 0.7 THEN 'train'
        WHEN random_value >= 0.1 AND random_value < 0.8 THEN 'test'
        ELSE 'val' 
      END AS split_set
    FROM data
    """

df = client.query(query).to_dataframe()

df.to_csv("gs://vtxdemos-datasets-public/ecommerce/ecommerce_balanced.csv", index=False)

job = aiplatform.CustomTrainingJob(
    display_name='test-train',
    script_path='test_script.py',
    requirements=['pandas', 'numpy'],
    container_uri='gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest',
    model_serving_container_image_uri='gcr.io/my-trainer/serving:1',
    model_serving_container_predict_route='predict',
    model_serving_container_health_route='metadata', labels={'key': 'value'}, )
