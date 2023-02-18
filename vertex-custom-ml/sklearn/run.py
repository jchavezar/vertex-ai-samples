# %%
from google.cloud import aiplatform as aip

aip.init(project='jchavezar-demo', staging_bucket='gs://vtx-staging')
# %%

model = aip.Model.upload(
    display_name='sklearn-ecommerce',
    artifact_uri='gs://vtx-models/ecommerce/onnx',
    serving_container_image_uri='gcr.io/jchavezar-demo/ecommerce:fast-onnx',
    serving_container_predict_route='/predict',
    serving_container_health_route='/health'
)

# %%

model.deploy(
    deployed_model_display_name='sklearn-ecommerce',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=1
)
# %%
