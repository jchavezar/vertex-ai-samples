#%%
from google.cloud.aiplatform import Model, Endpoint

project="vtxdemos"
deploy_image_uri="us-central1-docker.pkg.dev/vtxdemos/prediction/sd-diff-h:v1.0"
aip_storage_uri="gs://vtxdemos-models/sd-burger/"
model_file_name="BKWhopperSDXLv4-step00004000.safetensors"

!docker build -t $deploy_image_uri .
!docker push $deploy_image_uri

#%%
model = Model.upload(
    display_name="sd-diff-model", 
    serving_container_image_uri=deploy_image_uri,
    artifact_uri=aip_storage_uri,
    serving_container_environment_variables={"MODEL_FILE_NAME": model_file_name}
    )

endpoint = Endpoint.create(
    display_name="sd-diff-endpoint")
#%%
endpoint.deploy(
    machine_type="g2-standard-24",
    accelerator_type="NVIDIA_L4",
    accelerator_count=2,
    min_replica_count=1,
    max_replica_count=1,
    sync=True,
    model=model,
    )
# %%
