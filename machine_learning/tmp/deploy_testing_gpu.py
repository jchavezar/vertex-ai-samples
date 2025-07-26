#%%
from google.cloud import aiplatform

#region Upload Model to Model Registry
model = aiplatform.Model.upload(
    display_name="gpu_testing",
    artifact_uri="gs://vtxdemos-models/beans/model",
    serving_container_image_uri="us-central1-docker.pkg.dev/vtxdemos/custom-predictions/deploy-testing-gpu:1.0"
)

endpoint = aiplatform.Endpoint.create(
    display_name="llm-deploy"+"-gpu",
)

model.deploy(
    endpoint=endpoint,
    traffic_split={"0": 100},
    machine_type="a3-highgpu-8g",
    accelerator_type="NVIDIA_H100_80GB",
    accelerator_count=1,
    min_replica_count=1,
    max_replica_count=1,
    sync=True
)
#endregion

# %%
